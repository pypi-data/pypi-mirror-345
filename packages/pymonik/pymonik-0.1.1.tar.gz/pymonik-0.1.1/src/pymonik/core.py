import contextvars
import io
import os
import zipfile

import grpc
import uuid
import yaml
import cloudpickle as pickle

from datetime import timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from .utils import LazyArgs, create_grpc_channel
from .context import PymonikContext
from .environment import RuntimeEnvironment
from .results import ResultHandle, MultiResultHandle

from armonik.client import ArmoniKTasks, ArmoniKResults, ArmoniKSessions, ArmoniKEvents
from armonik.common import TaskOptions, TaskDefinition, Output, Result
from armonik.worker import TaskHandler, armonik_worker, ClefLogger

_CURRENT_PYMONIK: contextvars.ContextVar[Optional['Pymonik']] = contextvars.ContextVar(
    "_CURRENT_PYMONIK", default=None
)

# A clean way of cancelling submitted tasks maybe ? 
class Task:
    """A wrapper for a function that can be executed as an ArmoniK task."""

    def __init__(self, func: Callable, require_context:bool = False, func_name: str = None):
        self.func = func
        self.func_name = func_name or func.__name__
        self.require_context = require_context
        # We don't store a reference to the pymonik instance here anymore
        # Instead, we'll use the current_pymonik() function to get the active instance

    # TODO: repeat invocations my_function.invoke(repeat=5)
    # TODO: There's a cleaner way for delegation since I treat the is/isn't_worker cases separately but this will have to do for now
    def invoke(self, *args, pymonik: Optional["Pymonik"] = None, delegate=False) -> Union[ResultHandle, MultiResultHandle]:
        """Invoke the task with the given arguments."""

        # Handle the case of a single task
        if pymonik is None:
            pymonik = _CURRENT_PYMONIK.get(None)
            if pymonik is None:
                raise RuntimeError(
                    "No active PymoniK instance found. Please create one and pass it in or use the context manager."
                )
        if len(args) == 0:
            results = self._invoke_multiple([(Pymonik.NoInput,)], pymonik)
            return results[0]
        results = self._invoke_multiple([args], pymonik)
        return results[0]
    
    def map_invoke(self, args_list: List[Tuple], pymonik: Optional["Pymonik"] = None) -> MultiResultHandle:
        """Invoke the task with the given arguments and return a MultiResultHandle."""
        if pymonik is None:
            pymonik = _CURRENT_PYMONIK.get(None)
            if pymonik is None:
                raise RuntimeError(
                    "No active PymoniK instance found. Please create one and pass it in or use the context manager."
                )
        # Handle the case of multiple tasks
        result_handles = self._invoke_multiple(args_list, pymonik)
        return MultiResultHandle(result_handles)

    def __call__(self, *args, **kwds):
        return self.func(*args, **kwds)



    def _invoke_multiple(self, args_list: List[Tuple], pymonik_instance) -> List[ResultHandle]:
        """Invoke a multiple tasks with the given arguments."""
        # Ensure we have an active connection and session
        if not pymonik_instance._connected:
            pymonik_instance.create()

        # Process arguments to extract ResultHandles for data dependencies
        if not pymonik_instance._session_created:
            raise RuntimeError(
                "No existing session to link the invocation to, create one first (hint: call create or use the context manager)"
            )


        # 
        function_instance_remote_name = pymonik_instance._session_id + "__function__" + self.func_name

        if function_instance_remote_name not in pymonik_instance.remote_functions:
            pymonik_instance.register_tasks([self])

        function_id = pymonik_instance.remote_functions[
            pymonik_instance._session_id + "__function__" + self.func_name
        ].result_id

        all_function_invocation_info = []
        all_result_names = []
        all_payloads = {}
        for args in args_list:
            payload_name =  f"{pymonik_instance._session_id}__payload__{self.func_name}__{uuid.uuid4()}"
            result_name = f"{pymonik_instance._session_id}__output__{self.func_name}__{uuid.uuid4()}"
            function_invocation_info = {
                "data_dependencies": [function_id],
                "payload_name": payload_name,
                "result_name": result_name
            }
            processed_args = []
            # Prepare function call args description
            for arg in args:
                if arg is pymonik_instance.NoInput:
                    processed_args.append("__no_input__")
                elif isinstance(arg, ResultHandle):
                    function_invocation_info["data_dependencies"].append(arg.result_id)
                    processed_args.append(f"__result_handle__{arg.result_id}")
                elif isinstance(arg, MultiResultHandle):
                    # If it's a MultiResultHandle, add all result IDs as dependencies
                    for handle in arg.result_handles:
                        function_invocation_info["data_dependencies"].append(handle.result_id)
                    processed_args.append(
                        f"__multi_result_handle__"
                        + ",".join([handle.result_id for handle in arg.result_handles])
                    )
                else:
                    processed_args.append(arg)

            # Serialize the function call information
            payload = pickle.dumps(
                {
                    "func_name": self.func_name,
                    "func_id": function_id,
                    "require_context": self.require_context,
                    "environment": pymonik_instance.environment,
                    "args": LazyArgs(processed_args),
                }
            )

            all_payloads[payload_name] = payload
            all_result_names.append(result_name)
            all_function_invocation_info.append(function_invocation_info)
        # Create result metadata for output
        results_created = pymonik_instance._dispatch_create_metadata(
            all_result_names,
        )
        # Create the payloads for all the tasks to submit
        payload_results = pymonik_instance._dispatch_create_payloads(all_payloads)

        # Submit all the tasks:
        task_definitions = []
        for invocation_info in all_function_invocation_info: 
        # Create the task definition

            task_definitions.append(TaskDefinition(
                payload_id=payload_results[invocation_info["payload_name"]].result_id,
                expected_output_ids=[results_created[invocation_info["result_name"]].result_id],
                data_dependencies=invocation_info["data_dependencies"],
            ))
            

        # Submit the task
        pymonik_instance._dispatch_submit_tasks(
            task_definitions # TODO: use different batch size for tasks/results
        )

        # Return a handle to the result
        result_handles = [ResultHandle(result.result_id, pymonik_instance._session_id, pymonik_instance) for result in results_created.values()]
        return result_handles

def task(_func: Optional[Callable] = None, *, require_context: bool = False, function_name: Optional[str] = None) -> Union[Callable, Task]:
    def decorator(func: Callable) -> Task:
        resolved_name = function_name or func.__name__
        return Task(func, require_context=require_context, func_name=resolved_name)

    if _func is None:
        # Case 1: Called with arguments - @task(...)
        return decorator
    else:
        # Case 2: Called without arguments - @task
        return decorator(_func)

class Pymonik:
    """A wrapper around ArmoniK for task-based distributed computing."""

    # A singleton to indicate that a task takes no input
    NoInput = object()

    def __init__(
        self,
        endpoint: Optional[str] = None,
        partition: Optional[str] = "pymonik",
        environment: Dict[str, Any] = {},
        is_worker: bool = False,
        application_name: str = "pymonik",
        application_version: str = "0.1",
        application_namespace: str = "pymonik",
        batch_size: int = 32,
    ):
        self._endpoint = endpoint
        self._partition = partition
        self._application_name = application_name
        self._application_version = application_version  # TODO: remove
        self._application_namespace = application_namespace
        self._connected = False
        self._session_created = False
        self.remote_functions = {}  # TODO: I should probably delete all these results when a session is closed.
        self.environment = environment
        self._token: Optional[contextvars.Token] = None
        self._is_worker_mode = is_worker
        self.batch_size = batch_size
        self.task_handler: Optional[TaskHandler] = None
        # Register all tasks that have been decorated so far

    def _dispatch_create_metadata(self, names: List[str]) -> Dict[str, Result]:
        """Internal method to create result metadata, dispatching to worker/client."""
        if self.is_worker():
            if not self.task_handler:
                 raise RuntimeError("Task handler not available in worker mode.")
            # TaskHandler uses batch_size internally in the method call
            return self.task_handler.create_results_metadata(names, batch_size=self.batch_size)
        else:
            if not self._results_client:
                raise RuntimeError("Results client not initialized.")
            # ArmoniKResults client takes session_id and batch_size explicitly
            return self._results_client.create_results_metadata(
                names, self._session_id, batch_size=self.batch_size
            )

    def _dispatch_create_payloads(self, payloads: Dict[str, bytes]) -> Dict[str, Result]:
         """Internal method to create results with data (payloads), dispatching."""
         if self.is_worker():
             if not self.task_handler:
                 raise RuntimeError("Task handler not available in worker mode.")
             return self.task_handler.create_results(payloads, batch_size=self.batch_size)
         else:
             if not self._results_client:
                 raise RuntimeError("Results client not initialized.")
             return self._results_client.create_results(
                 payloads, self._session_id, batch_size=self.batch_size
             )

    def _dispatch_submit_tasks(self, task_definitions: List[TaskDefinition]) -> None:
        """Internal method to submit tasks, dispatching to worker/client."""
        if self.is_worker():
            if not self.task_handler:
                 raise RuntimeError("Task handler not available in worker mode.")
            self.task_handler.submit_tasks(
                task_definitions,
                batch_size=self.batch_size # NOTE: this is bad, really bad (set client side but we just use the default for worker)
            )
        else:
            if not self._tasks_client:
                raise RuntimeError("Tasks client not initialized.")

            self._tasks_client.submit_tasks(self._session_id, task_definitions)


    def register_tasks(self, tasks: List[Task]):
        """Register a task with the PymoniK instance."""
        pickled_functions = {}
        for task in tasks:
            remote_function_name = self._session_id + "__function__" + task.func_name
            if remote_function_name in self.remote_functions:
                # This shouldn't be a full failure, but a warning, esp. in the case where the user is trying to register stuff manually (TODO: when logging is in)
                raise ValueError(
                    f"Task with name {task.func_name} is already registered. "
                )

            pickled_functions[remote_function_name] = (
                    pickle.dumps(task.func)
                ) 
        # Upload the pickled functions to the cluster
        # NOTE: This is really bad for subtasking, other option would be to get results before invoke to check if task is already registered in this session and if so reuse it
        upload_results = self._dispatch_create_payloads(
            payloads=pickled_functions,
        )

        # Register the function
        self.remote_functions.update(upload_results) 

        return self

    def _zip_directory(self, dir_path: str) -> bytes:
        """ Zips the contents of a directory and returns the bytes. """
        if not os.path.isdir(dir_path):
            raise ValueError(f"Path {dir_path} is not a valid directory.")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Create arcname relative to the directory being zipped
                    arcname = os.path.relpath(file_path, dir_path)
                    zipf.write(file_path, arcname)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def create(self, task_handler: Optional[TaskHandler] = None, expected_output:Optional[str] = None) -> "Pymonik":
        """Initialize client connections and create a session.
        
            Args:
                task_handler (Optional[TaskHandler]): The task handler to use in worker mode.
            Returns:
                Pymonik: The current instance of Pymonik.
        """
        if self._is_worker_mode:
            if task_handler is None:
                 raise ValueError("TaskHandler must be provided in worker mode.")
            self.task_handler = task_handler
            self._connected = True # Mark as 'connected' in worker context
            self._session_id = task_handler.session_id # Get session from handler
            self._session_created = True # Mark session as 'created' in worker context
            return self

        if self._connected:
            return self

        # TODO: Cloudpickle goes in here (maintain registrar of serialized functions, send them over during init, can also do dank thing here like with unison)

        # Initialize clients
        if self._endpoint != None:
            # TODO: Add parameters for TLS
            self._channel = grpc.insecure_channel(self._endpoint)
        else:
            # Check if AKCONFIG is defined
            akconfig_value = os.getenv("AKCONFIG")
            if akconfig_value is None:
                raise RuntimeError(
                    "No endpoint provided and AKCONFIG environment variable is not set."
                )
            else: 
                # Load the AKCONFIG file
                with open(akconfig_value, "r") as f:
                    config = yaml.safe_load(f)
                self._endpoint = config.get("endpoint")
                certificate_authority = config.get("certificate_authority")
                client_certificate = config.get("client_certificate")
                client_key = config.get("client_key")
                self._channel = create_grpc_channel(
                    self._endpoint,
                    certificate_authority=certificate_authority,
                    client_certificate=client_certificate,
                    client_key=client_key,
                )
            
        self._tasks_client = ArmoniKTasks(self._channel)
        self._results_client = ArmoniKResults(self._channel)
        self._sessions_client = ArmoniKSessions(self._channel)
        self._events_client = ArmoniKEvents(self._channel)
        self._connected = True

        # Create a session
        default_task_options = TaskOptions(
            max_duration=timedelta(seconds=300),
            priority=1,
            max_retries=5,
            partition_id=self._partition,
        )
        self._session_id = self._sessions_client.create_session(
            default_task_options=default_task_options,
            partition_ids=[self._partition] if self._partition is not None else None,
        )
        self._session_created = True
        print(f"Session {self._session_id} has been created")

        # Upload environment data if needed
        # TODO: doesn't work as of right now
        if False and self.environment and "mount" in self.environment:
            mounts_to_upload = {}
            mount_name_to_target_map = {} # Maps temporary result name to mount_to path

            original_mounts = self.environment.get("mount", [])
            if not isinstance(original_mounts, list):
                 print(f"Warning: 'mount' in environment should be a list of tuples. Skipping mount processing.") # Or raise error
                 original_mounts = [] # Clear it to avoid later errors

            for mount_info in original_mounts:
                 if not isinstance(mount_info, tuple) or len(mount_info) != 2:
                    print(f"Warning: Invalid mount entry {mount_info}. Expected (mount_from, mount_to). Skipping.")
                    continue

                 mount_from, mount_to = mount_info
                 print(f"Processing mount: Zipping {mount_from} for target {mount_to}...")
                 try:
                     zip_bytes = self._zip_directory(mount_from)
                     # Create a unique name for the result payload for this mount
                     cleaned_mount_from = mount_from.replace('/', '_').replace('\\', '_')
                     mount_result_name = f"{self._session_id}__mount_data__{cleaned_mount_from}"
                     mounts_to_upload[mount_result_name] = zip_bytes
                     mount_name_to_target_map[mount_result_name] = mount_to
                     print(f"  ... Zipped {mount_from} ({len(zip_bytes)} bytes) -> {mount_result_name}")
                 except Exception as e:
                     print(f"  ... Error zipping directory {mount_from}: {e}. Skipping this mount.")
                     # Decide if this should be a fatal error or just skip
                     # raise # Uncomment to make it fatal

            if mounts_to_upload:
                print(f"Uploading {len(mounts_to_upload)} zipped directories...")
                # Upload the zipped directories as results
                upload_results = self._results_client.create_results(
                    results_data=mounts_to_upload,
                    session_id=self._session_id,
                )
                print("  ... Upload complete.")

                # Update self.environment["mount"] to store (result_id, mount_to) pairs
                updated_mount_info = []
                for mount_result_name, output in upload_results.items():
                    if mount_result_name in mount_name_to_target_map:
                        mount_to = mount_name_to_target_map[mount_result_name]
                        result_id = output.result_id
                        updated_mount_info.append((result_id, mount_to))
                        print(f"  ... Mapped {mount_result_name} (Result ID: {result_id}) to target path {mount_to}")
                    else:
                         # This case should ideally not happen if logic is correct
                         print(f"Warning: Uploaded result {mount_result_name} not found in mapping. Inconsistency detected.")

                self.environment["mount"] = updated_mount_info
            else:
                 # If nothing was successfully zipped and prepared for upload
                 self.environment["mount"] = [] # Ensure it's an empty list if mounts were requested but failed



        # # Pickle all the registered functions and store them
        # pickled_functions = {}
        # for function_name, function in self._registered_tasks.items():
        #     pickled_functions[self._session_id + "__function__" + function_name] = (
        #         pickle.dumps(function)
        #     )  # NOTE: there is no caching mechanism so the number of results

        # self.remote_functions = self._results_client.create_results(
        #     results_data=pickled_functions,
        #     session_id=self._session_id,
        # )

        return self

    def is_worker(self) -> bool:
        """Returns True if running in worker mode, False if in client mode."""
        return self._is_worker_mode

    def close(self):
        """Close the session and clean up resources."""
        if self._is_worker_mode:
            return

        if self._session_created:
            try:
                self._sessions_client.close_session(self._session_id)
                print(f"Session {self._session_id} has been closed")
                self._session_created = False
            except Exception as e:
                print(f"Error closing session {self._session_id}: {e}")

        if self._connected:
            self._channel.close()
            self._connected = False

    def __enter__(self):
        """Context manager entry point."""

        if not self._is_worker_mode and not self._connected:
            self.create()
        self._token = _CURRENT_PYMONIK.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        if self._token:
            _CURRENT_PYMONIK.reset(self._token)
            self._token = None
        self.close()
        return False

def run_pymonik_worker():
    """Run the worker."""
    @armonik_worker()
    def processor(task_handler: TaskHandler) -> Output:
        try:
            logger = ClefLogger.getLogger("ArmoniKWorker")
            # Deserialize the payload
            payload = pickle.loads(task_handler.payload)
            func_name = payload["func_name"]
            func_id = payload["func_id"]
            require_context = payload["require_context"]
            args = payload["args"]
            requested_environment = payload["environment"]
            logger.info(
                f"Processing task {task_handler.task_id} : {func_name} -> {func_id} with arguments {args} in session {task_handler.session_id} "
            )
            # # Look up the function
            # if func_name not in self._registered_tasks:
            #     return Output(f"Function {func_name} not found")


            env = RuntimeEnvironment(logger)
            env.construct_environment(requested_environment)

            retrieved_args = args.get_args()

            # Process arguments, retrieving results if needed
            processed_args = []
            for arg in retrieved_args:
                if isinstance(arg, str) and arg == "__no_input__":
                    # Skip NoInput arguments
                    continue
                elif isinstance(arg, str) and arg.startswith("__result_handle__"):
                    # Retrieve the result data
                    result_id = arg[len("__result_handle__") :]
                    result_data = task_handler.data_dependencies[result_id]
                    processed_args.append(pickle.loads(result_data))
                elif isinstance(arg, str) and arg.startswith(
                    "__multi_result_handle__"
                ):
                    # Retrieve multiple result data
                    result_ids = arg[len("__multi_result_handle__") :].split(",")
                    processed_args.append(
                        [
                            pickle.loads(task_handler.data_dependencies[result_id])
                            for result_id in result_ids
                        ]
                    )
                else:
                    processed_args.append(arg)

            # Load the function
            func = pickle.loads(task_handler.data_dependencies[func_id])
            logger.info(
                f"Processing task {task_handler.task_id} : Retrieved function {func_name} from data dependencies"
            )

            # Call the function with the arguments
            if require_context:
                # If the function requires context, pass the task handler
                context = PymonikContext(task_handler, logger) # TODO: create the context before and make enrich logs with task/function info
                processed_args = [context] + processed_args
            else:
                # Otherwise, just pass the arguments
                processed_args = processed_args

            pymonik_worker_client = Pymonik(is_worker=True)
            pymonik_worker_client.create(task_handler=task_handler)
            with pymonik_worker_client:
                result = func(*processed_args)

            # Check if the result is a task and if so delegate
            # Serialize the result
            result_data = pickle.dumps(result)

            # Get the expected result ID
            result_id = task_handler.expected_results[0]

            # Send the result
            task_handler.send_results({result_id: result_data})

            return Output()

        except Exception as e:
            import traceback

            logger.error(
                f"Error processing task {task_handler.task_id} : {e}\n{traceback.format_exc()}"
            )
            return Output(f"Error processing task: {e}\n{traceback.format_exc()}")

    # Run the worker
    processor.run()
