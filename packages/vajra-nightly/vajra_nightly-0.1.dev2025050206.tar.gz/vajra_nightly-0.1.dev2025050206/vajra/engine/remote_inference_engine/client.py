import asyncio
from dataclasses import dataclass
from queue import Queue
from threading import Condition, Lock, Thread
from typing import AsyncIterator, Dict, List, Optional

from vajra._native.configs import ModelConfig as ModelConfig_C
from vajra._native.datatypes import (
    AbortRequest,
    ConfigRequest,
    ProcessRequest,
    RemoteInferenceRequest,
    RemoteInferenceResponseType,
    StartupRequest,
)
from vajra._native.enums import ZmqConstants
from vajra._native.utils import ZmqContext, ZmqSocket
from vajra._native.utils.zmq_helper import (
    recv_remote_inference_response,
    send_remote_inference_request,
)
from vajra.config import ModelConfig
from vajra.datatypes import SamplingParams  # type: ignore
from vajra.engine.remote_inference_engine.constants import (
    HEALTH_CHECK_TIMEOUT,
    IPC_HEALTH_EXT,
    IPC_INPUT_EXT,
    IPC_OUTPUT_EXT,
)
from vajra.logger import init_logger
from vajra.utils.threading_utils import exit_on_error, synchronized

logger = init_logger(__name__)


class EngineDeadError(RuntimeError):
    _ENGINE_DEAD_MSG = "Engine process died or is in error state"

    def __init__(self, cause: Exception):
        super().__init__(self._ENGINE_DEAD_MSG)
        self.cause = cause


@dataclass(frozen=True)
class MinimalRequestOutput:
    """A minimal Python class matching the RequestOutput protobuf structure."""

    request_id: str
    text: str
    token_ids: List[int]
    prompt_token_ids: List[int]
    finish_reason: Optional[str] = None
    finished: bool = False


class RemoteInferenceEngineClient:
    """Client for interacting with an engine on another process, communicating over zmq."""

    def __init__(self, ipc_path: str, engine_pid: int):
        self.context = ZmqContext()
        self.ipc_path = f"ipc://{ipc_path}"
        self.engine_pid = engine_pid

        # Input socket (PUSH)
        self.input_socket = ZmqSocket(self.context, ZmqConstants.PUSH)
        self.input_socket.connect(f"{self.ipc_path}{IPC_INPUT_EXT}")

        # Output socket (PULL)
        self.output_socket = ZmqSocket(self.context, ZmqConstants.PULL)
        self.output_socket.connect(f"{self.ipc_path}{IPC_OUTPUT_EXT}")

        # Health socket (PULL)
        self.health_socket = ZmqSocket(self.context, ZmqConstants.PULL)
        self.health_socket.connect(f"{self.ipc_path}{IPC_HEALTH_EXT}")

        # Store active request queues
        self._output_queue_map: Dict[str, Queue] = {}
        self._queue_lock = Lock()
        self._queue_condition = Condition(self._queue_lock)
        self._closed = False
        self._error: Optional[Exception] = None
        self._health_thread = None

        # Accumulated state for each request
        self._accumulated_state = {}

        # Start output processing thread immediately
        self._output_thread = Thread(target=self._process_outputs, daemon=True)
        self._output_thread.start()

        logger.info(
            "RemoteInferenceEngineClient initialized with engine PID: %d", engine_pid
        )

    @synchronized
    def add_to_output_queue_map(self, key: str, queue: Queue) -> None:
        """Method to notify condition that a new queue has been added."""
        with self._queue_condition:
            self._output_queue_map[key] = queue
            self._queue_condition.notify()

    def connect(self) -> None:
        """Connect to the engine server and verify it's ready."""
        try:
            logger.info("Waiting for engine server to be ready...")

            # Send startup request
            startup_request = StartupRequest(True)
            request = RemoteInferenceRequest(startup_request)
            send_remote_inference_request(self.input_socket, request)

            # Wait for response (this is a blocking call)
            response = recv_remote_inference_response(self.output_socket)

            if (
                response.type == RemoteInferenceResponseType.STARTUP
                and response.startup_response.server_ready
            ):
                # Server is ready, start health monitoring
                self._health_thread = Thread(target=self._monitor_health, daemon=True)
                self._health_thread.start()
                logger.info("Successfully connected to engine server")
                return
            else:
                raise RuntimeError(f"Unexpected response type: {response.type}")

        except Exception as e:
            logger.error(f"Failed to connect to engine server: {e}")
            raise

    def get_model_config(self) -> ModelConfig:
        """Get model configuration from the server."""
        if self._closed:
            raise RuntimeError("Client is closed")

        if self._error:
            raise EngineDeadError(self._error)

        request_id = "config-request"
        queue: Queue = Queue()
        self.add_to_output_queue_map(request_id, queue)

        try:
            # Send config request
            config_request = ConfigRequest(request_id=request_id)

            request = RemoteInferenceRequest(config_request=config_request)
            send_remote_inference_request(self.input_socket, request)

            # Wait for response
            response = queue.get()

            if isinstance(response, Exception):
                raise response

            if isinstance(response, ModelConfig_C):
                return ModelConfig(
                    model=response.model,
                    trust_remote_code=response.trust_remote_code,
                    download_dir=(
                        response.download_dir
                        if hasattr(response, "download_dir")
                        else None
                    ),
                    load_format=response.load_format,
                    dtype=response.dtype,
                    seed=response.seed,
                    revision=(
                        response.revision if hasattr(response, "revision") else None
                    ),
                    max_model_len=response.max_model_len,
                    override_num_layers=response.total_num_layers,
                )
            if isinstance(response, ModelConfig):
                return response
            else:
                raise RuntimeError(f"Unexpected response type: {type(response)}")

        finally:
            self._remove_queue(request_id)

    @exit_on_error
    def _process_outputs(self):
        """Process outputs from the server and route to appropriate queues."""
        try:
            while not self._closed:
                try:
                    with self._queue_condition:
                        while not self._output_queue_map and not self._closed:
                            self._queue_condition.wait()

                    if self._closed:
                        break

                    response = recv_remote_inference_response(self.output_socket)

                    if response.type == RemoteInferenceResponseType.OUTPUT:
                        self._handle_request_output_response(response)
                    elif response.type == RemoteInferenceResponseType.ERROR:
                        self._handle_error_response(response)
                    elif response.type == RemoteInferenceResponseType.MODEL_CONFIG:
                        self._handle_model_config_response(response)
                    else:
                        raise RuntimeError(f"Unexpected response type: {response.type}")

                except Exception as e:
                    logger.error("Error processing output: %s", str(e))
                    self._error = e
                    with self._queue_lock:
                        for queue in self._output_queue_map.values():
                            queue.put(EngineDeadError(e))
                    break

        finally:
            logger.debug("Output processing task finished")

    def _handle_request_output_response(self, response):
        """Handle request output response."""
        req_out = response.output_response
        with self._queue_lock:
            if req_out.request_id in self._output_queue_map:
                # Initialize state for new requests
                if req_out.request_id not in self._accumulated_state:
                    self._accumulated_state[req_out.request_id] = {
                        "text": "",
                        "token_ids": [],
                        "prompt_token_ids": [],
                    }

                state = self._accumulated_state[req_out.request_id]

                # Accumulate text and tokens if this is a delta update
                if req_out.is_delta:
                    state["text"] += req_out.text
                    state["token_ids"].extend(req_out.token_ids)

                    # Store prompt_token_ids only from first chunk
                    if req_out.is_first_chunk:
                        assert req_out.prompt_token_ids
                        state["prompt_token_ids"] = list(req_out.prompt_token_ids)
                else:
                    state["text"] = req_out.text
                    state["token_ids"] = list(req_out.token_ids)
                    state["prompt_token_ids"] = list(req_out.prompt_token_ids)

                output = MinimalRequestOutput(
                    request_id=req_out.request_id,
                    text=state["text"],
                    token_ids=state["token_ids"],
                    prompt_token_ids=state["prompt_token_ids"],
                    finish_reason=(
                        req_out.finish_reason if req_out.finish_reason else None
                    ),
                    finished=req_out.finished,
                )

                self._output_queue_map[req_out.request_id].put(output)

                if req_out.finished:
                    self._output_queue_map.pop(req_out.request_id, None)
                    self._accumulated_state.pop(req_out.request_id, None)
            else:
                logger.error(
                    "Received output for unknown request ID: %s",
                    req_out.request_id,
                )

    def _handle_error_response(self, response):
        """Handle error response."""
        request_id = response.error.request_id
        with self._queue_lock:
            if request_id in self._output_queue_map:
                error = RuntimeError(response.error.error_message)
                self._output_queue_map[request_id].put(error)
                self._output_queue_map.pop(request_id, None)

    def _handle_model_config_response(self, response):
        """Handle model config response."""
        request_id = "config-request"
        with self._queue_lock:
            if request_id in self._output_queue_map:
                queue = self._output_queue_map[request_id]
                config: ModelConfig_C = response.model_config
                queue.put(config)

    def _monitor_health(self):
        """Monitor server health through health check socket."""
        try:
            while not self._closed:
                try:
                    # Use a separate thread with a timeout to handle the blocking recv call
                    health_msg = None
                    recv_error = None

                    def recv_with_timeout():
                        nonlocal health_msg, recv_error
                        try:
                            health_msg = recv_remote_inference_response(
                                self.health_socket
                            )
                        except Exception as e:
                            recv_error = e

                    # Start a thread to handle the blocking recv
                    recv_thread = Thread(target=recv_with_timeout, daemon=True)
                    recv_thread.start()

                    # Wait for the thread with timeout
                    recv_thread.join(timeout=HEALTH_CHECK_TIMEOUT)

                    # Check if we got a message or timed out
                    if recv_thread.is_alive():
                        # Thread is still running after timeout
                        logger.error("Server health check timeout")
                        raise RuntimeError("Server health check timeout")

                    # Check if there was an error during receive
                    if recv_error is not None:
                        raise recv_error

                except Exception as e:
                    logger.error("Health check error: %s", str(e))
                    self._error = e
                    with self._queue_lock:
                        for queue in self._output_queue_map.values():
                            queue.put(EngineDeadError(e))
                    break

        finally:
            logger.debug("Health monitoring task finished")

    async def generate(
        self,
        request_id: str,
        prompt: str,
        sampling_params: SamplingParams,
    ) -> AsyncIterator[MinimalRequestOutput]:
        """Generate completion for the given prompt asynchronously.

        Returns an async iterator that yields MinimalRequestOutput objects.
        """
        if self._closed:
            raise RuntimeError("Client is closed")
        if self._error:
            raise EngineDeadError(self._error)

        # Set up queues for communication
        async_queue: asyncio.Queue = asyncio.Queue()
        sync_queue: Queue = Queue()
        self.add_to_output_queue_map(request_id, sync_queue)

        # Bridge between synchronous and asynchronous
        async def bridge_queues():
            try:
                while True:
                    response = await asyncio.get_event_loop().run_in_executor(
                        None, sync_queue.get
                    )
                    await async_queue.put(response)

                    if (
                        isinstance(response, MinimalRequestOutput) and response.finished
                    ) or isinstance(response, Exception):
                        break
            except Exception as e:
                await async_queue.put(e)

        bridge_task = asyncio.create_task(bridge_queues())

        try:
            # Send generation request
            process_request = ProcessRequest(
                request_id=request_id, prompt=prompt, sampling_params=sampling_params
            )
            request = RemoteInferenceRequest(process_request=process_request)

            await asyncio.get_event_loop().run_in_executor(
                None, lambda: send_remote_inference_request(self.input_socket, request)
            )

            # Stream responses
            while True:
                response = await async_queue.get()

                if isinstance(response, Exception):
                    raise response

                if isinstance(response, MinimalRequestOutput):
                    yield response

                    if response.finished:
                        break

        finally:
            await bridge_task
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._remove_queue(request_id)
            )

    def _remove_queue(self, request_id: str) -> None:
        """Helper method to remove a queue from the output queue map."""
        with self._queue_lock:
            self._output_queue_map.pop(request_id, None)

    def abort(self, request_id: str) -> None:
        """Abort a running generation."""
        if self._closed:
            raise RuntimeError("Client is closed")

        abort_request = AbortRequest(request_id=request_id)

        request = RemoteInferenceRequest(abort_request=abort_request)
        send_remote_inference_request(self.input_socket, request)

    def close(self):
        """Close the client connection."""
        if self._closed:
            return

        logger.info("Closing RemoteInferenceEngineClient")
        self._closed = True

        # Signal any waiting threads
        with self._queue_condition:
            self._queue_condition.notify_all()

        # Wait for threads to finish
        if self._output_thread is not None:
            self._output_thread.join(timeout=1.0)
        if self._health_thread is not None:
            self._health_thread.join(timeout=1.0)

        logger.info("Closed RemoteInferenceEngineClient")
