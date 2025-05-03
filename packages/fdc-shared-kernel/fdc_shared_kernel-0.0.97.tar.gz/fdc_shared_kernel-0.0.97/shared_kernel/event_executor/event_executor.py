from datetime import datetime, timezone
import json
import threading
from concurrent.futures import Future
from typing import Any, Callable, Dict, Optional
from threading import Semaphore
import os
from typing import Tuple

from shared_kernel.config import Config
from shared_kernel.event_executor.utils import EventConcurrencyManager, EventStats
from shared_kernel.interfaces import DataBus
from shared_kernel.logger import Logger
from shared_kernel.messaging.utils.event_messages import AWSEventMessage, EventMessage
from shared_kernel.status_tracker import StatusTracker
from shared_kernel.enums import TaskStatus
from shared_kernel.utils.thread_local_util import ThreadLocalStorage


app_config = Config()
logger = Logger(app_config.get("APP_NAME"))

thread_local_storage = ThreadLocalStorage()

class EventExecutor:

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance
        
    def __init__(
        self, databus: Optional[DataBus] = None, status_tracker: Optional[StatusTracker] = None
    ):
        """
        Initialize the event executor singleton.
        
        Args:
            databus: databus - AWS Databus (SQS and Events) / NATS / HTTP
            status_tracker: Status tracker to track status of events task and jobs
        """
        with self._lock:

            if self._initialized:
                return
                
            if databus is None or status_tracker is None:
                raise ValueError("DataBus and StatusTracker must be provided for initial initialization")
            
            self.databus = databus
            self.status_tracker = status_tracker
            # listener threads for each events
            self._threads: Dict[str, threading.Thread] = {}
            self._event_concurrency_manager = EventConcurrencyManager()
            self._shutdown_event = threading.Event()
            self._active_futures: Dict[str, set[Future]] = {}
            self._stats: Dict[str, EventStats] = {}
            self._stats_lock = threading.Lock()
            self._initialized = True
            logger.info("EventExecutor singleton initialized.")

    def _process_message(
        self,
        event_msg: EventMessage,
        callback: Callable[[dict, Optional[dict]], None],
    ) -> bool:
        """
        Process a single message with error handling

        Args:
            event_msg: Parsed event message
            callback: Handler function to process the message

        Returns:
            bool: True if processing succeeded, False otherwise
        """
        try:
            # set the start time of the event exceution in the event meta
            event_msg.event_meta.start_event()

            logger.info(
                f"Processing event {event_msg.event_name}. trace-id: {event_msg.event_meta.trace_id}. span-id: {event_msg.event_meta.trace_id}."
            )

            task_details = self.status_tracker.get_task(task_details = event_msg)
            if task_details is not None and task_details["is_duplicate"]:
                logger.info(
                    f"Duplicate task {event_msg.event_name} is already in progress. trace-id: {event_msg.event_meta.trace_id}. span-id: {event_msg.event_meta.trace_id}."
                )
                return
            task = task_details.get("task_details") if task_details is not None else None
            if task is None:
                logger.info(
                    f"Creating new task for event {event_msg.event_name}. trace-id: {event_msg.event_meta.trace_id}. span-id: {event_msg.event_meta.trace_id}."
                )
                self.status_tracker.create_task(
                    trace_id=event_msg.event_meta.trace_id,
                    span_id=event_msg.event_meta.span_id,
                    task=event_msg.event_name,
                    status=TaskStatus.PROCESSING.value,
                    task_id=event_msg.event_meta.job_id,
                    org_id=event_msg.event_meta.org_id,
                    entity_id=event_msg.event_meta.entity_id,
                )
                
                # setting tracking payload without the time taken and end time
                # but with all the other data
                self.status_tracker.set_event_meta_and_message_receipt_handle(
                    event_meta=event_msg.event_meta.to_dict(),
                    task_id=event_msg.event_meta.job_id,
                    task=event_msg.event_name,
                    message_receipt_handle=event_msg.receipt_handle,
                )

                callback(event_msg.raw_message, None)

            elif task["status"] == TaskStatus.QUEUED.value:
                logger.info(
                    f"Task {event_msg.event_name} is already in queue. trace-id: {event_msg.event_meta.trace_id}. span-id: {event_msg.event_meta.trace_id}."
                )

                self.status_tracker.set_event_meta_and_message_receipt_handle(
                    event_meta=event_msg.event_meta.to_dict(),
                    task_id=event_msg.event_meta.job_id,
                    task=event_msg.event_name,
                    message_receipt_handle=event_msg.receipt_handle,
                )
                
                self.status_tracker.update_task(
                    span_id=event_msg.event_meta.span_id,
                    trace_id=event_msg.event_meta.trace_id,
                    task=event_msg.event_name,
                    status=TaskStatus.PROCESSING.value,
                    task_id=event_msg.event_meta.job_id,
                )
                tracking_id = json.loads(task["tracking_id"]) if task["tracking_id"] else None
                callback(event_msg.raw_message, tracking_id)

            elif task["status"] == TaskStatus.PROCESSING.value:
                logger.info(
                    f"Task {event_msg.event_name} is already processing. trace-id: {event_msg.event_meta.trace_id}. span-id: {event_msg.event_meta.trace_id}."
                )
                tracking_id = json.loads(task["tracking_id"]) if task["tracking_id"] else None
                callback(event_msg.raw_message, tracking_id)

            return True

        except Exception as e:
            logger.error(
                f"Error processing event {event_msg.event_name} trace-id: {event_msg.event_meta.trace_id}. span-id: {event_msg.event_meta.trace_id} : {str(e)}"
            )
            logger.info("Error processing event",type="distributed_trace",is_success="False",failure_reason=str(e))

            # adding the failure reason to the event meta
            event_msg.event_meta.failure_reason = str(e)

            self.status_tracker.mark_task_as_failure(
                span_id=event_msg.event_meta.span_id,
                trace_id=event_msg.event_meta.trace_id,
                task=event_msg.event_name,
                failure_reason=str(e),
                task_id=event_msg.event_meta.job_id,
            )

            # NOTE: for dead letter queue we are simply publishing the
            # failed event to the databus as a DLQ event.
            dlq_message = {
                "event_name": event_msg.event_name,
                "event_payload": event_msg.event_payload,
                "event_meta": event_msg.event_meta.to_dict(),
            }

            self.databus.publish_event("DLQ", dlq_message)

            return False

        finally:
            # set the end time of the event exceution in the event meta
            event_msg.event_meta.end_event()

            logger.info(
                    f"Setting tracking payload for event {event_msg.event_name}. trace-id: {event_msg.event_meta.trace_id}. span-id: {event_msg.event_meta.trace_id}."
                )
            # updating event_meta with the time taken and end time
            self.status_tracker.set_event_meta_and_message_receipt_handle(
                    event_meta=event_msg.event_meta.to_dict(),
                    task_id=event_msg.event_meta.job_id,
                    task=event_msg.event_name,
                    message_receipt_handle=event_msg.receipt_handle,
                )
            
    def _update_event_stats(self, event_name: str, success: bool) -> None:
        """Update event statistics with thread-safety"""
        with self._stats_lock:
            if event_name not in self._stats:
                self._stats[event_name] = EventStats()
            
            if success:
                self._stats[event_name].successful_events += 1
            else:
                self._stats[event_name].failed_events += 1

    def _callback_wrapper(self, callback: Callable[[Any], None], event_msg: AWSEventMessage) -> None:
        """
        Wrapper around message processing to handle cleanup and status updates.
        """
        success = False
        event_name = None

        try:
            logger.info(f"Initiating callback for message: {event_msg}")
            event_name = event_msg.event_name

            # Set thread-local context
            thread_local_storage.set_all({
                "trace_id": event_msg.event_meta.trace_id,
                "span_id": event_msg.event_meta.span_id,
                "org_id": event_msg.event_meta.org_id if hasattr(event_msg.event_meta, 'org_id') else None,
                "trigger": event_msg.event_meta.trigger if hasattr(event_msg.event_meta, 'trigger') else None,
                "event_name": event_msg.event_name,
                "event_payload": json.dumps(event_msg.event_payload),
                "parent_span_id": event_msg.event_meta.parent_span_id if hasattr(event_msg.event_meta, 'parent_span_id') else None,
                "event_meta": json.dumps(event_msg.event_meta.__dict__)
                })
            logger.info("Event recieved",type="distributed_trace")
            # Process the message
            success = self._process_message(event_msg, callback)

        finally:
            # Update the event stats whether it succeeded or failed
            if event_name:
                self._update_event_stats(event_name, success)

            if success:
                logger.info(
                    f"Event {event_msg.event_name} completed successfully. "
                    f"trace-id: {event_msg.event_meta.trace_id}. span-id: {event_msg.event_meta.span_id}."
                )
                self.status_tracker.update_task(
                    span_id=event_msg.event_meta.span_id,
                    trace_id=event_msg.event_meta.trace_id,
                    task=event_msg.event_name,
                    status=TaskStatus.COMPLETED.value,
                    task_id=event_msg.event_meta.job_id,
                )
                logger.info("Event processed successfully",type="distributed_trace",is_success="True",time_in_seconds= event_msg.event_meta.time_taken)
            else:
                logger.warning(
                    f"Event {event_msg.event_name} failed during processing. "
                    f"trace-id: {event_msg.event_meta.trace_id}. span-id: {event_msg.event_meta.span_id}."
                )

            # Clean up thread-local storage
            thread_local_storage.clear()

            # Delete the message from the queue
            self.databus.delete_message(event_msg)

    def _task_done_callback(self, future: Future, event_name: str, event_semaphore: Semaphore, message: AWSEventMessage) -> None:
        """
        Callback function to be called when a task in the ThreadPoolExecutor is completed.

        Args:
            future: The Future object representing the completed task.
            event_name: The name of the event associated with the completed task.
        """
        # remove the completed Future object from the set of active futures for the event
        self._active_futures[event_name]["futures"].discard(future)
        self._active_futures[event_name]["message"].discard(message)
        
        # release the semaphore for the event, allowing a new task to be submitted
        event_semaphore.release()

    def _listen_events(
        self,
        event_name: str,
        callback: Callable[[Any], None],
    ) -> None:
        """
        Main event listening loop for a specific event type.
        """
        logger.info(f"Starting event listener for [{event_name}].")

        event_semaphore = self._event_concurrency_manager.get_event_semaphore(event_name=event_name)
        event_threapool_executor = self._event_concurrency_manager.get_event_threadpool_executor(event_name=event_name)

        while not self._shutdown_event.is_set():
            try:
                # try to acquire the semaphore before processing new messages
                # this will block if we've reached max concurrency
                if event_semaphore.acquire():
                    message = self.databus.get_async_message(event_name)
                    if message:
                        logger.info(f"Received message for event {event_name}: {message}")
                        future = event_threapool_executor.submit(self._callback_wrapper, callback, message)
                        # adding a callback to the future object which
                        # will run upon its completion
                        future.add_done_callback(lambda future, event_name=event_name, event_semaphore=event_semaphore: self._task_done_callback(future, event_name, event_semaphore, message))
                        self._active_futures[event_name]["futures"].add(future)
                        self._active_futures[event_name]["message"].add(message)
                    else:
                        # if no message was received, release the semaphore
                        event_semaphore.release()
                else:
                    # 1f we couldn't acquire the semaphore, wait briefly before trying again
                    self._shutdown_event.wait(0.1)
            except Exception as e:
                logger.error(f"Error in event listener for {event_name}: {str(e)}")
        logger.info(f"Event listener for {event_name} has been stopped.")

    # TODO: enable caching here
    def _load_event_schema_and_description(self, event_name: str) -> Tuple[dict, str]:
        """
        Load event schema and description.
        
        Args:
            event_name: Name of the event

        Returns:
            A tuple containing:
            - schema: Parsed JSON schema for the event.
            - description: Text description for the event.
        """
        schema_path = os.path.join('src', 'infrastructure', 'event_details', f"{event_name.lower()}", 'schema.json')
        description_path = os.path.join('src', 'infrastructure', 'event_details', f"{event_name.lower()}", 'description.txt')

        if not os.path.exists(schema_path):
            logger.error(f"Schema file missing for event {event_name}: {schema_path}")
            raise Exception(f"Schema file missing for event {event_name}: {schema_path}")
        if not os.path.exists(description_path):
            logger.error(f"Description file missing for event {event_name}: {description_path}")
            raise Exception(f"Description file missing for event {event_name}: {description_path}")
        
        try:
            with open(schema_path, 'r') as schema_file:
                schema = json.load(schema_file)
            with open(description_path, 'r') as description_file:
                description = description_file.read().strip()

            return schema, description

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON schema for event {event_name}")
            raise Exception(f"Invalid JSON schema for event {event_name}")

    def get_all_stats(self) -> dict:
        """
        Get comprehensive statistics for all registered events.
        """
        all_stats = {}

        for event_name in self._event_concurrency_manager.event_threadpool_executors.keys():
            executor = self._event_concurrency_manager.get_event_threadpool_executor(event_name)
            total_workers = executor._max_workers
            active_futures = self._active_futures[event_name]["futures"]
            busy_workers = len(active_futures)
            available_workers = total_workers - busy_workers
            active_futures_list = list(active_futures)
            message_list = list(self._active_futures[event_name]["message"])
            
            with self._stats_lock:
                event_stats = self._stats.get(event_name, EventStats())

            event_schema, event_description = self._load_event_schema_and_description(event_name)
            
            all_stats[event_name] = {
                "workers": {
                    "total": total_workers,
                    "available": available_workers,
                    "busy": busy_workers
                },
                "events": {
                    "successful": event_stats.successful_events,
                    "failed": event_stats.failed_events,
                    "total": event_stats.total_events,
                    # added current queue size of the event
                    "queue_size": self.databus.get_queued_count(event_name)
                },
                # "schema": event_schema,
                "description": event_description,
            }
            
            busy_worker_details = []
            if busy_workers:
                for i in range(len(active_futures_list)):
                    raw_message = message_list[i].raw_message
                    if raw_message:
                        start_time = datetime.fromisoformat(raw_message.get("start_time"))
                        busy_worker_details.append({
                            "payload": raw_message,
                            "start_time": start_time.strftime("%b %d, %Y %H:%M:%S UTC"),
                            "time_since_start": int((datetime.now(timezone.utc) - start_time).total_seconds())
                        })
            all_stats[event_name]["busy_workers"] = busy_worker_details
        
        return all_stats

    def register_event(
        self,
        event_name: str,
        callback: Callable[[Any], None],
        max_concurrency: int,
    ) -> None:
        """
        Register an event handler with the specified concurrency limit.

        Args:
            event_name: Name of the event to handle
            callback: Function to call with the event payload
            max_concurrency: Maximum number of concurrent executions

        Raises:
            ValueError: If event is already registered
        """
        if event_name in self._threads:
            raise ValueError(f"Event {event_name} is already registered")

        logger.info(
            f"Registering event {event_name} with max concurrency of {max_concurrency}."
        )

        # the DataBus interface requires subscribe_async_event
        # to accept a callback parameter as part of its method signature.
        self.databus.subscribe_async_event(event_name, None)

        self._event_concurrency_manager.set_event_concurrency(event_name=event_name, max_concurrency=max_concurrency)

        # keeping track of active futures returned by
        # submitting a job to the threadpool executor
        self._active_futures[event_name] = {}
        self._active_futures[event_name]["futures"] = set()
        self._active_futures[event_name]["message"] = set()

        thread = threading.Thread(
            target=self._listen_events,
            args=(event_name, callback),
            name=f"EventListener-{event_name}",
            daemon=True,
        )
        self._threads[event_name] = thread
        thread.start()
        logger.info(f"Event {event_name} registered and listener thread started.")

    def shutdown(self) -> None:
        """
        Gracefully shut down all event listeners.
        """
        logger.info("Shutting down EventExecutor.")
        self._shutdown_event.set()

        # wait for threads to finish
        for event_name, thread in self._threads.items():
            thread.join()

        # wait for active tasks to complete
        for event_name, futures in self._active_futures.items():
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logger.error(
                        f"Error during shutdown of {event_name} task: {str(e)}"
                    )

        # shutdown executors
        for event_name, executor in self._event_concurrency_manager.event_threadpool_executors.items():
            executor.shutdown(
                wait=True,
            )

        self._threads.clear()
        self._event_concurrency_manager.event_threadpool_executors.clear()
        self._active_futures.clear()
        logger.info("EventExecutor shutdown complete.")
