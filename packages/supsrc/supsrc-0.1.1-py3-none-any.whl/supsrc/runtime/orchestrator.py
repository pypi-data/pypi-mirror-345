#
# supsrc/runtime/orchestrator.py
#

import asyncio
import time  # Import time for unique task names
from contextlib import suppress  # For cleaner task cancellation handling
from pathlib import Path
from typing import Any, Optional, TypeAlias, cast

import attrs
import cattrs  # Needed for config validation exceptions
import structlog

from supsrc.config import SupsrcConfig, load_config
from supsrc.config.models import (
    InactivityRuleConfig,
    RuleConfig,
)

# --- Specific Engine Import (replace with plugin loading later) ---
from supsrc.engines.git import GitEngine, GitRepoSummary  # Import summary class too
from supsrc.exceptions import ConfigurationError, MonitoringSetupError, SupsrcError
from supsrc.monitor import MonitoredEvent, MonitoringService

# --- Import concrete result types and base protocols ---
from supsrc.protocols import (
    CommitResult,
    PushResult,
    RepositoryEngine,
    RepoStatusResult,  # Concrete result classes
    StageResult,
)
from supsrc.rules import check_trigger_condition
from supsrc.state import RepositoryState, RepositoryStatus

# --- Supsrc Imports ---
from supsrc.telemetry import StructLogger

# --- TUI Integration Imports (Conditional) ---
try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from textual.app import App as TextualApp
    from supsrc.tui.app import LogMessageUpdate, StateUpdate
    TEXTUAL_AVAILABLE_RUNTIME = True
except ImportError:
    TEXTUAL_AVAILABLE_RUNTIME = False
    TextualApp = None # type: ignore
    StateUpdate = None # type: ignore
    LogMessageUpdate = None # type: ignore

# Logger for this module
log: StructLogger = structlog.get_logger("runtime.orchestrator")

# Type alias for state map
RepositoryStatesMap: TypeAlias = dict[str, RepositoryState]

class WatchOrchestrator:
    """
    Manages the core watch lifecycle, coordinating monitoring, state, rules,
    engines, and optionally updating a Textual TUI.
    """

    def __init__(
        self,
        config_path: Path,
        shutdown_event: asyncio.Event,
        app: Optional["TextualApp"] = None # Accept optional TUI app instance
        ) -> None:
        """
        Initializes the orchestrator.

        Args:
            config_path: Path to the configuration file.
            shutdown_event: Event signalling graceful shutdown.
            app: Optional instance of the Textual TUI application.
        """
        self.config_path = config_path
        self.shutdown_event = shutdown_event
        self.app: TextualApp | None = app if TEXTUAL_AVAILABLE_RUNTIME else None # Store the TUI app instance only if usable
        self.config: SupsrcConfig | None = None
        self.monitor_service: MonitoringService | None = None
        self.event_queue: asyncio.Queue[MonitoredEvent] = asyncio.Queue()
        self.repo_states: RepositoryStatesMap = {}
        self.repo_engines: dict[str, RepositoryEngine] = {}
        self._running_tasks: set[asyncio.Task[Any]] = set()
        self._log = log.bind(orchestrator_id=id(self))
        self._is_tui_active = bool(self.app) # Flag for easier checking

    # --- TUI Update Helpers ---

    def _post_tui_log(self, repo_id: str | None, level: str, message: str) -> None:
        """Safely posts a log message to the TUI if active."""
        if self._is_tui_active and self.app and LogMessageUpdate:
            try:
                # Use call_later for thread safety from worker
                self.app.call_later(self.app.post_message, LogMessageUpdate(repo_id, level.upper(), message))
            except Exception as e:
                 self._safe_log("warning", "Failed to post log message to TUI", repo_id=repo_id, error=str(e))

    def _post_tui_state_update(self) -> None:
        """Safely posts the current repository states to the TUI."""
        if self._is_tui_active and self.app and StateUpdate:
            try:
                # Create a copy for thread safety/mutability concerns
                states_copy = {rid: attrs.evolve(state) for rid, state in self.repo_states.items()}
                self.app.call_later(self.app.post_message, StateUpdate(states_copy))
            except Exception as e:
                 self._safe_log("warning", "Failed to post state update to TUI", error=str(e))

    # --- Core Logic Methods ---

    async def _trigger_action_callback(self, repo_id: str) -> None:
        """
        Callback executed when a trigger condition is met. Executes repository actions.
        """
        repo_state = self.repo_states.get(repo_id)
        repo_config = self.config.repositories.get(repo_id) if self.config else None
        global_config = self.config.global_config if self.config else None
        repo_engine = self.repo_engines.get(repo_id)

        callback_log = self._log.bind(repo_id=repo_id)
        callback_log.debug("Entering action callback")

        if not repo_state or not repo_config or not global_config or not repo_engine:
            callback_log.error("Action Triggered: Could not find state, config, or engine.")
            self._post_tui_log(repo_id, "ERROR", "Action failed: Missing state/config/engine.")
            return

        # Check status first
        # Allow triggering from IDLE (e.g., timer fired before any new change) or CHANGED
        if repo_state.status not in (RepositoryStatus.CHANGED, RepositoryStatus.IDLE):
            callback_log.warning("Action Triggered: Repo not in CHANGED/IDLE state, skipping.",
                                current_status=repo_state.status.name)
            self._post_tui_log(repo_id, "WARNING", f"Action skipped (state: {repo_state.status.name}).")
            repo_state.cancel_inactivity_timer()
            return

        # Mark as triggered and clear timer immediately
        repo_state.update_status(RepositoryStatus.TRIGGERED)
        repo_state.cancel_inactivity_timer()
        self._post_tui_state_update() # Update TUI status

        rule_config_obj: RuleConfig = repo_config.rule
        rule_type_str = getattr(rule_config_obj, "type", "unknown_rule_type")

        callback_log.info(
            "Action Triggered: Performing actions...",
            rule_type=rule_type_str,
            current_save_count=repo_state.save_count
        )
        self._post_tui_log(repo_id, "INFO", f"Action triggered by rule: {rule_type_str}")

        engine_config_dict = repo_config.repository # This is the dict for the engine
        working_dir = repo_config.path

        try:
            # --- 1. Get Status ---
            repo_state.update_status(RepositoryStatus.PROCESSING)
            self._post_tui_log(repo_id, "DEBUG", "Checking repository status...")
            self._post_tui_state_update()
            # Expecting a RepoStatusResult object now
            status_result: RepoStatusResult = await repo_engine.get_status(repo_state, engine_config_dict, global_config, working_dir)
            callback_log.debug("Received status result from engine", status_result=attrs.asdict(status_result))

            if not status_result.success:
                # Use the message from the result object
                raise SupsrcError(f"Failed to get repository status: {status_result.message}")

            # Check specific flags from the result
            if status_result.is_conflicted:
                callback_log.warning("Action Skipped: Repository has conflicts.")
                self._post_tui_log(repo_id, "ERROR", "Action skipped: Conflicts detected!")
                repo_state.update_status(RepositoryStatus.ERROR, "Conflicts detected") # Stay in ERROR state
                self._post_tui_state_update()
                return

            if status_result.is_clean and status_result.is_unborn:
                callback_log.info("Action Skipped: Unborn repository is clean, no commit needed.")
                self._post_tui_log(repo_id, "INFO", "Action skipped: Unborn repository clean.")
                repo_state.reset_after_action() # Reset to IDLE
                self._post_tui_state_update()
                return
            elif status_result.is_clean:
                 callback_log.info("Action Skipped: Repository is clean, no commit needed.")
                 self._post_tui_log(repo_id, "INFO", "Action skipped: Repository clean.")
                 repo_state.reset_after_action() # Reset to IDLE
                 self._post_tui_state_update()
                 return

            # --- 2. Stage Changes ---
            repo_state.update_status(RepositoryStatus.STAGING)
            self._post_tui_log(repo_id, "INFO", "Staging changes...")
            self._post_tui_state_update()
            # Expecting a StageResult object
            stage_result: StageResult = await repo_engine.stage_changes(None, repo_state, engine_config_dict, global_config, working_dir)
            if not stage_result.success:
                raise SupsrcError(f"Failed to stage changes: {stage_result.message}")
            callback_log.info("Action: Staging successful.", files_staged=stage_result.files_staged)
            self._post_tui_log(repo_id, "DEBUG", f"Staging successful ({len(stage_result.files_staged or [])} files).")

            # --- 3. Perform Commit ---
            repo_state.update_status(RepositoryStatus.COMMITTING)
            self._post_tui_log(repo_id, "INFO", "Performing commit...")
            self._post_tui_state_update()
            # Expecting a CommitResult object
            commit_result: CommitResult = await repo_engine.perform_commit(
                message_template="unused", # Engine handles template lookup via config
                state=repo_state,
                config=engine_config_dict,
                global_config=global_config,
                working_dir=working_dir
            )
            if not commit_result.success:
                raise SupsrcError(f"Commit failed: {commit_result.message}")

            if commit_result.commit_hash is None:
                # Engine skipped commit (e.g., no changes after staging)
                callback_log.info("Action Skipped: Commit skipped by engine.", reason=commit_result.message)
                self._post_tui_log(repo_id, "INFO", f"Commit skipped: {commit_result.message}")
                repo_state.reset_after_action() # Reset to IDLE
                self._post_tui_state_update()
                return
            else:
                commit_short_hash = commit_result.commit_hash[:7]
                callback_log.info("Action: Commit successful", hash=commit_result.commit_hash)
                self._post_tui_log(repo_id, "SUCCESS", f"Commit successful: {commit_short_hash}")

            # --- 4. Perform Push ---
            repo_state.update_status(RepositoryStatus.PUSHING)
            self._post_tui_log(repo_id, "INFO", "Performing push (if enabled)...")
            self._post_tui_state_update()
            # Expecting a PushResult object
            push_result: PushResult = await repo_engine.perform_push(repo_state, engine_config_dict, global_config, working_dir)

            if not push_result.success:
                # Log warning, but still reset state to IDLE as commit was successful
                callback_log.warning("Action: Push failed", reason=push_result.message)
                self._post_tui_log(repo_id, "WARNING", f"Push failed: {push_result.message}")
                repo_state.reset_after_action() # Reset even on push fail
            else:
                if push_result.skipped:
                    callback_log.info("Action: Push skipped by configuration.")
                    self._post_tui_log(repo_id, "INFO", "Push skipped (disabled in config).")
                else:
                    callback_log.info("Action: Push successful.")
                    self._post_tui_log(repo_id, "SUCCESS", "Push successful.")
                repo_state.reset_after_action() # Reset after success/skip

            self._post_tui_state_update() # Final TUI state update

        except Exception as action_exc:
            callback_log.error("Action Failed: Error during execution", error=str(action_exc), exc_info=True)
            # Ensure state exists before updating
            if repo_state:
                 repo_state.update_status(RepositoryStatus.ERROR, f"Action failed: {action_exc}")
                 self._post_tui_log(repo_id, "ERROR", f"Action failed: {action_exc}")
                 self._post_tui_state_update() # Update TUI with error
            else:
                 # This case should be rare due to initial checks
                 self._post_tui_log(repo_id, "CRITICAL", f"Action failed (state missing): {action_exc}")


    async def _consume_events(self) -> None:
        """Consumes events from the queue, updates state, manages timers, checks rules."""
        consumer_log = self._log.bind(component="EventConsumer")
        consumer_log.info("Event consumer starting loop.")
        asyncio.get_running_loop()
        processed_event_count = 0

        while not self.shutdown_event.is_set():
            event: MonitoredEvent | None = None # Keep default None
            repo_id: str | None = None # Initialize repo_id outside try

            get_task: asyncio.Task | None = None
            shutdown_wait_task: asyncio.Task | None = None

            try:
                consumer_log.debug(f"Consumer loop iteration. Processed: {processed_event_count}. Waiting on queue.get()...", queue_id=id(self.event_queue))
                # Create tasks for BOTH awaitables
                get_task = asyncio.create_task(self.event_queue.get(), name=f"QueueGet-{id(self.event_queue)}-{processed_event_count}")
                shutdown_wait_task = asyncio.create_task(self.shutdown_event.wait(), name=f"ShutdownWait-{processed_event_count}")

                # Wait for either task to complete
                done, pending = await asyncio.wait(
                    {get_task, shutdown_wait_task},
                    return_when=asyncio.FIRST_COMPLETED
                )

                # Prioritize checking shutdown task completion
                if shutdown_wait_task in done or self.shutdown_event.is_set():
                    consumer_log.info("Consumer detected shutdown while waiting.")
                    if get_task in pending:
                         get_task.cancel()
                         with suppress(asyncio.CancelledError): await get_task
                    if shutdown_wait_task in pending:
                        shutdown_wait_task.cancel()
                        with suppress(asyncio.CancelledError): await shutdown_wait_task
                    break # Exit the while loop

                # If shutdown didn't happen, get_task must be in done
                if get_task in done:
                    event = get_task.result()
                    consumer_log.debug(">>> Consumer AWOKE from queue.get() with event.")
                    # Assign repo_id *before* the main processing try block
                    repo_id = event.repo_id
                else:
                     consumer_log.warning("asyncio.wait returned unexpectedly without queue item or shutdown signal.")
                     continue

                # Cancel the shutdown_wait_task if the event was received
                if shutdown_wait_task in pending:
                    shutdown_wait_task.cancel()
                    with suppress(asyncio.CancelledError): await shutdown_wait_task


                # --- Process Event ---
                processed_event_count += 1
                event_log = consumer_log.bind(repo_id=repo_id, event_type=event.event_type, src_path=str(event.src_path))
                event_log.debug(">>> Processing received event details")

                # Inner Try/Except for event processing logic
                try:
                    repo_state = self.repo_states.get(repo_id)
                    repo_config = self.config.repositories.get(repo_id) if self.config else None

                    if not repo_state or not repo_config:
                        event_log.warning("Ignoring event for unknown/disabled/unconfigured repository.")

                    else:
                        # Record change, check rules, schedule actions/timers
                        repo_state.record_change()
                        event_log = event_log.bind(save_count=repo_state.save_count, status=repo_state.status.name)
                        self._post_tui_log(repo_id, "DEBUG", f"Change: {event.event_type} {event.src_path.name}")
                        self._post_tui_state_update()
                        event_log.debug("State updated after recording change")

                        rule_config_obj: RuleConfig = repo_config.rule
                        rule_type_str = getattr(rule_config_obj, "type", "unknown_rule_type")
                        event_log.debug(">>> About to check trigger condition", rule_type=rule_type_str)

                        rule_met = check_trigger_condition(repo_state, repo_config)
                        event_log.debug("Rule check evaluated", rule_met=rule_met)

                        if rule_met:
                            event_log.info("Rule condition met, scheduling action", rule_type=rule_type_str)
                            # Use time.monotonic() for potentially more unique task names
                            action_task = asyncio.create_task(self._trigger_action_callback(repo_id), name=f"Action-{repo_id}-{time.monotonic()}")
                            self._running_tasks.add(action_task)
                            action_task.add_done_callback(self._running_tasks.discard)
                        else:
                            if isinstance(rule_config_obj, InactivityRuleConfig):
                                delay = rule_config_obj.period.total_seconds()
                                event_log.debug("Rescheduling inactivity check", delay_seconds=delay)
                                self._post_tui_log(repo_id, "DEBUG", f"Activity detected, rescheduling check in {delay:.1f}s.")
                                current_loop = asyncio.get_running_loop()
                                # Ensure the callback lambda creates a task
                                timer_handle = current_loop.call_later(
                                    delay, lambda rid=repo_id: asyncio.create_task(self._trigger_action_callback(rid))
                                )
                                repo_state.set_inactivity_timer(timer_handle)

                except Exception as processing_exc:
                     event_log.error("Error during event processing logic", error=str(processing_exc), exc_info=True)
                     if repo_id and repo_id in self.repo_states:
                         self.repo_states[repo_id].update_status(RepositoryStatus.ERROR, f"Event processing error: {processing_exc}")
                         self._post_tui_log(repo_id, "ERROR", f"Event processing error: {processing_exc}")
                         self._post_tui_state_update()

            except asyncio.CancelledError:
                 consumer_log.info("Consumer task processing cancelled.")
            except Exception as e:
                current_repo_id = repo_id if repo_id else "UNKNOWN_PRE_ASSIGNMENT"
                consumer_log.error("Error in consumer main try block", repo_id=current_repo_id, error=str(e), exc_info=True)

            finally:
                if event is not None:
                    try:
                        self.event_queue.task_done()
                    except ValueError:
                        consumer_log.warning("queue.task_done() called unexpectedly.", event_processed=bool(event))
                    except Exception as td_exc:
                         consumer_log.error("Error calling queue.task_done()", error=str(td_exc))

        consumer_log.info(f"Event consumer finished after processing {processed_event_count} events.")

    async def _initialize_repositories(self) -> list[str]:
        """Initializes states, loads engines, and logs initial repo summary."""
        enabled_repo_ids = []
        if not self.config:
            self._safe_log("error", "Config missing, cannot initialize repos.")
            return []

        self._safe_log("info", "--- Initializing Repositories ---")
        self._post_tui_log(None, "INFO", "Initializing repositories...")
        for repo_id, repo_config in self.config.repositories.items():
            init_log = self._log.bind(repo_id=repo_id)
            if repo_config.enabled and repo_config._path_valid:
                init_log.debug("Initializing state object")
                self.repo_states[repo_id] = RepositoryState(repo_id=repo_id)
                engine_instance: RepositoryEngine | None = None

                # --- Load Engine ---
                engine_config = repo_config.repository
                engine_type = engine_config.get("type")
                if not engine_type or not isinstance(engine_type, str):
                    init_log.error("Repo config missing 'type' for engine.", config_section=engine_config)
                    self.repo_states[repo_id].update_status(RepositoryStatus.ERROR, "Missing engine type")
                    self._post_tui_log(repo_id, "ERROR", "Config Error: Missing engine type.")
                    continue

                try:
                    init_log.debug("Loading repo engine", engine_type=engine_type)
                    # --- TODO: Replace with plugin loading logic ---
                    if engine_type == "supsrc.engines.git": engine_instance = GitEngine()
                    # elif engine_type == "plugin:my_custom_hg_engine": engine_instance = load_plugin(...)
                    else: raise NotImplementedError(f"Engine type '{engine_type}' not supported.")
                    # ---------------------------------------------
                    self.repo_engines[repo_id] = engine_instance
                    init_log.debug("Engine loaded ok.", engine_class=type(engine_instance).__name__)
                    self._post_tui_log(repo_id, "DEBUG", f"Engine '{engine_type}' loaded.")
                    enabled_repo_ids.append(repo_id)
                except Exception as load_exc:
                    init_log.error("Failed to load repo engine", engine_type=engine_type, error=str(load_exc), exc_info=True)
                    self.repo_states[repo_id].update_status(RepositoryStatus.ERROR, f"Failed to load engine: {load_exc}")
                    self._post_tui_log(repo_id, "ERROR", f"Engine load failed: {load_exc}")
                    continue

                # --- Get Initial Summary ---
                try:
                    init_log.debug("Getting initial repo summary...")
                    # Use hasattr for safety, assuming get_summary might be optional
                    if hasattr(engine_instance, "get_summary"):
                        # Cast to expected type if necessary and confident
                        summary = cast(GitRepoSummary, await engine_instance.get_summary(repo_config.path))

                        if summary.head_ref_name == "ERROR":
                            summary_msg = f"Init Error: {summary.head_commit_message_summary}"
                            init_log.error(summary_msg)
                            self._post_tui_log(repo_id, "ERROR", summary_msg)
                            # Optionally set state to ERROR here
                            # self.repo_states[repo_id].update_status(RepositoryStatus.ERROR, summary_msg)
                        elif summary.is_empty:
                            summary_msg = "Init: Repository empty."
                            init_log.info(summary_msg)
                            self._post_tui_log(repo_id, "INFO", summary_msg)
                        elif summary.head_ref_name == "UNBORN":
                            summary_msg = "Init: Repository has no commits yet (unborn HEAD)."
                            init_log.info(summary_msg)
                            self._post_tui_log(repo_id, "INFO", summary_msg)
                        elif not summary.head_ref_name or not summary.head_commit_hash:
                            summary_msg = "Init: Unable to determine HEAD reference or commit."
                            init_log.warning(summary_msg)
                            self._post_tui_log(repo_id, "WARNING", summary_msg)
                        else:
                            commit_short_hash = summary.head_commit_hash[:7]
                            commit_msg_summary = summary.head_commit_message_summary or "No commit message"
                            summary_msg = f"Init: HEAD at {summary.head_ref_name} ({commit_short_hash}) | {commit_msg_summary}"
                            init_log.info(summary_msg)
                            self._post_tui_log(repo_id, "INFO", summary_msg)
                    else:
                         init_log.warning("Engine lacks get_summary method.")
                         self._post_tui_log(repo_id, "WARNING", "Engine lacks get_summary.")

                except Exception as summary_exc:
                    init_log.error("Failed to get initial repo summary", error=str(summary_exc), exc_info=True)
                    self._post_tui_log(repo_id, "ERROR", f"Failed to get summary: {summary_exc}")

            else:
                init_log.info("Skipping initialization (disabled or invalid path)",
                              enabled=repo_config.enabled, path_valid=repo_config._path_valid)

        self._post_tui_state_update()
        self._safe_log("info", "--- Repo Initialization Complete ---", count=len(enabled_repo_ids))
        self._post_tui_log(None, "INFO", f"{len(enabled_repo_ids)} repos initialized.")
        return enabled_repo_ids

    def _setup_monitoring(self, enabled_repo_ids: list[str]) -> list[str]:
        """Adds successfully initialized repositories to the MonitoringService."""
        setup_errors = 0
        successfully_added_ids = []
        if not self.config: return []

        self._safe_log("info", "Setting up filesystem monitoring...")
        self._post_tui_log(None, "INFO", "Setting up filesystem monitoring...")
        self.monitor_service = MonitoringService(self.event_queue)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
             self._safe_log("critical", "Cannot get running event loop during monitoring setup.")
             return []

        for repo_id in enabled_repo_ids:
            if repo_id not in self.repo_states or repo_id not in self.repo_engines:
                self._safe_log("warning", "Skipping monitor setup for repo with failed init/engine load", repo_id=repo_id)
                continue

            repo_config = self.config.repositories[repo_id]
            monitor_log = self._log.bind(repo_id=repo_id)
            try:
                monitor_log.debug("Adding repository to monitoring service", path=str(repo_config.path))
                # Pass the loop to add_repository
                self.monitor_service.add_repository(repo_id, repo_config, loop)
                successfully_added_ids.append(repo_id)
                monitor_log.info("Monitoring successfully scheduled.")
                self._post_tui_log(repo_id, "INFO", "Monitoring started.")
            except MonitoringSetupError as e:
                monitor_log.error("Failed to setup monitoring", error=str(e))
                if repo_id in self.repo_states: self.repo_states[repo_id].update_status(RepositoryStatus.ERROR, f"Monitoring setup failed: {e}")
                self._post_tui_log(repo_id, "ERROR", f"Monitoring setup failed: {e}")
                self._post_tui_state_update()
                setup_errors += 1
            except Exception as e:
                monitor_log.error("Unexpected error adding repository to monitor", error=str(e), exc_info=True)
                if repo_id in self.repo_states: self.repo_states[repo_id].update_status(RepositoryStatus.ERROR, f"Unexpected setup error: {e}")
                self._post_tui_log(repo_id, "CRITICAL", f"Unexpected monitor setup error: {e}")
                self._post_tui_state_update()
                setup_errors += 1

        if setup_errors > 0:
            self._safe_log("warning", f"Encountered {setup_errors} error(s) during monitoring setup.")
            self._post_tui_log(None, "WARNING", f"{setup_errors} monitoring setup error(s).")

        self._safe_log("info", f"Monitoring setup complete for {len(successfully_added_ids)} repositories.")
        return successfully_added_ids


    async def run(self) -> None:
        """Main execution method for the watch process."""
        self._safe_log("info", "Starting orchestrator run", config_path=str(self.config_path), tui_mode=self._is_tui_active)

        try:
            # Load Config
            self._safe_log("debug", "Loading configuration...")
            try:
                self.config = load_config(self.config_path)
                self._safe_log("info", "Config loaded successfully.")
                self._post_tui_log(None, "INFO", f"Config loaded: {self.config_path.name}")
            except (ConfigurationError, cattrs.BaseValidationError) as e:
                 self._safe_log("error", "Failed to load/validate config", error=str(e), path=str(self.config_path))
                 self._post_tui_log(None, "CRITICAL", f"Config Error: {e}")
                 raise
            except Exception as e:
                 self._safe_log("critical", "Unexpected error loading config", error=str(e), exc_info=True)
                 self._post_tui_log(None, "CRITICAL", f"Unexpected Config Error: {e}")
                 raise

            # Initialize Repos
            enabled_repo_ids = await self._initialize_repositories()
            if not enabled_repo_ids:
                 self._safe_log("warning", "No enabled/valid repos found. Exiting.")
                 self._post_tui_log(None, "WARNING", "No valid/enabled repositories found.")
                 return

            # Setup & Start Monitoring
            successfully_added_ids = self._setup_monitoring(enabled_repo_ids)
            if not successfully_added_ids:
                 self._safe_log("critical", "No repos could be monitored. Exiting.")
                 self._post_tui_log(None, "CRITICAL", "Failed to start monitoring any repository.")
                 return

            if self.monitor_service:
                 self._safe_log("debug", "Starting monitor service thread...")
                 self.monitor_service.start()
                 if not self.monitor_service.is_running:
                     self._safe_log("critical", "Monitor service failed to start. Exiting.")
                     self._post_tui_log(None, "CRITICAL", "Monitor service failed to start.")
                     return
                 self._post_tui_log(None, "INFO", f"Monitoring active for {len(successfully_added_ids)} repositories.")
            else:
                 self._safe_log("error", "Monitor service not initialized after setup.")
                 self._post_tui_log(None, "CRITICAL", "Internal Error: Monitor service missing.")
                 return

            # Start Consumer Task
            self._safe_log("debug", "Creating event consumer task...")
            consumer_task = asyncio.create_task(self._consume_events(), name="EventConsumer")
            self._running_tasks.add(consumer_task)
            consumer_task.add_done_callback(self._running_tasks.discard)

            self._safe_log("info", "Orchestrator running. Waiting for shutdown signal.")

            # Wait for Shutdown
            await self.shutdown_event.wait()
            self._safe_log("info", "Shutdown signal received.")
            self._post_tui_log(None, "INFO", "Shutdown requested...")

        except SupsrcError as e:
            self._safe_log("critical", "Critical supsrc error during watch", error=str(e), exc_info=True)
            self._post_tui_log(None, "CRITICAL", f"Runtime Error: {e}")
        except asyncio.CancelledError:
             self._safe_log("warning", "Orchestrator run task cancelled.")
             if not self.shutdown_event.is_set(): self.shutdown_event.set()
        except Exception as e:
            self._safe_log("critical", "Unexpected error in orchestrator run", error=str(e), exc_info=True)
            self._post_tui_log(None, "CRITICAL", f"Unexpected Error: {e}")
            if not self.shutdown_event.is_set(): self.shutdown_event.set()
        finally:
            # Orchestrator Cleanup
            self._safe_log("info", "Orchestrator starting cleanup...")
            self._post_tui_log(None, "INFO", "Cleaning up...")

            # 1. Cancel Repo Timers
            self._safe_log("debug", "Cancelling active repo timers...")
            timers_cancelled = sum(1 for state in self.repo_states.values() if state.inactivity_timer_handle)
            for state in self.repo_states.values(): state.cancel_inactivity_timer()
            self._safe_log("debug", f"Cancelled {timers_cancelled} repo timer(s).")

            # 2. Cancel Running Tasks (Consumer)
            tasks_to_cancel = list(self._running_tasks)
            if tasks_to_cancel:
                self._safe_log("debug", f"Cancelling {len(tasks_to_cancel)} running task(s)...", tasks=[t.get_name() for t in tasks_to_cancel])
                for task in tasks_to_cancel: task.cancel()
                await asyncio.gather(*tasks_to_cancel, return_exceptions=True)
                self._safe_log("debug", "Running tasks cancellation gathered.")
            else: self._safe_log("debug", "No running tasks to cancel.")

            # 3. Stop Monitoring Service
            if self.monitor_service and self.monitor_service.is_running:
                 self._safe_log("debug", "Stopping monitoring service...")
                 try:
                     await self.monitor_service.stop()
                     self._safe_log("debug", "Monitoring service stop completed.")
                     self._post_tui_log(None, "INFO", "Monitoring stopped.")
                 except Exception as stop_exc:
                     self._safe_log("error", "Error during monitor service stop", error=str(stop_exc), exc_info=True)
                     self._post_tui_log(None, "ERROR", "Error stopping monitor service.")
            elif self.monitor_service: self._safe_log("debug", "Monitor service already stopped.")
            else: self._safe_log("debug", "Monitor service was not initialized.")

            self._safe_log("info", "Orchestrator finished cleanup.")
            self._post_tui_log(None, "INFO", "Cleanup complete.")

    def _safe_log(self, level: str, msg: str, **kwargs):
        """Helper to suppress logging errors during final shutdown."""
        kwargs["orchestrator_id"] = id(self)
        try:
            if hasattr(self, "_log") and self._log: getattr(self._log, level)(msg, **kwargs)
            else: pass
        except Exception: pass

# 🔼⚙️
