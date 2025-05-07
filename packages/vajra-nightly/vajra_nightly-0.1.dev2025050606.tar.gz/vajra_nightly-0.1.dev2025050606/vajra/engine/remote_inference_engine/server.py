import os
import signal
import time
from dataclasses import dataclass
from threading import Event, Lock, Thread
from typing import Dict, List

from vajra._native.datatypes import (
    AbortRequest,
    ConfigRequest,
    ErrorResponse,
    OutputResponse,
    ProcessRequest,
    RemoteInferenceRequest,
    RemoteInferenceRequestType,
    RemoteInferenceResponse,
    StartupRequest,
    StartupResponse,
)
from vajra._native.enums import ZmqConstants
from vajra._native.utils import ZmqContext, ZmqSocket
from vajra._native.utils.zmq_helper import (
    recv_remote_inference_request,
    send_remote_inference_response,
)
from vajra.config import InferenceEngineConfig, ModelConfig
from vajra.datatypes import RequestOutput, SamplingParams  # type: ignore
from vajra.engine.inference_engine import InferenceEngine
from vajra.engine.remote_inference_engine.constants import (
    HEALTH_SEND_INTERVAL,
    IPC_HEALTH_EXT,
    IPC_INPUT_EXT,
    IPC_OUTPUT_EXT,
)
from vajra.logger import init_logger
from vajra.utils.threading_utils import exit_on_error

logger = init_logger(__name__)


@dataclass
class SenderState:
    """Track the length of the last sent text and token IDs for each request to for incremental sends."""

    last_text_len: int = 0
    last_token_ids_len: int = 0


class RemoteInferenceEngineServer:
    """Wrapper over InferenceEngine to handle requests over zmq from a RemoteInferenceEngineClient."""

    def __init__(
        self,
        context: ZmqContext,
        engine: InferenceEngine,
        ipc_path: str,
    ):
        self.context = context
        self.engine = engine
        self.ipc_path = f"ipc://{ipc_path}"

        # Input socket (PULL)
        self.input_socket = ZmqSocket(context, ZmqConstants.PULL)
        self.input_socket.bind(f"{self.ipc_path}{IPC_INPUT_EXT}")

        # Output socket (PUSH)
        self.output_socket = ZmqSocket(context, ZmqConstants.PUSH)
        self.output_socket.bind(f"{self.ipc_path}{IPC_OUTPUT_EXT}")

        # Health check socket (PUSH)
        self.health_socket = ZmqSocket(context, ZmqConstants.PUSH)
        self.health_socket.bind(f"{self.ipc_path}{IPC_HEALTH_EXT}")

        self._active_generations: Dict[str, SenderState] = {}
        self._running = True
        self._lock = Lock()
        logger.debug("RemoteInferenceEngineServer bound to IPC path")

        # Create threads
        self.input_thread = Thread(target=self._input_loop, daemon=True)
        self.output_thread = Thread(target=self._output_loop, daemon=True)
        self.health_thread = Thread(target=self._health_check_loop, daemon=True)

    def run(self):
        """Run the server loop."""
        logger.info("RemoteInferenceEngineServer is running")

        # Start threads
        self.input_thread.start()
        self.output_thread.start()
        self.health_thread.start()

        try:
            # Use an Event to keep the main thread dormant but responsive to KeyboardInterrupt
            Event().wait()
        except KeyboardInterrupt:
            logger.info("Server interrupted, shutting down")
        finally:
            self.shutdown()

    @exit_on_error
    def _health_check_loop(self):
        """Send periodic health check messages."""
        while self._running:
            try:
                startup_response = StartupResponse(server_ready=True)
                response = RemoteInferenceResponse(startup_response=startup_response)
                send_remote_inference_response(self.health_socket, response)
            except Exception as e:
                logger.error("Health check failed: %s", str(e))
            time.sleep(HEALTH_SEND_INTERVAL)

    @exit_on_error
    def _input_loop(self):
        """Loop to handle new inputs."""
        while self._running:
            self._handle_new_input()

    @exit_on_error
    def _output_loop(self):
        """Loop to handle engine outputs."""
        while self._running:
            try:
                # Engine step.
                request_outputs: List[RequestOutput] = self.engine.get_outputs(False)

                # Send request outputs
                self._send_outputs(request_outputs)

            except Exception as e:
                logger.error("Error in output loop: %s", str(e), exc_info=True)
                error = ErrorResponse(request_id="", error_message=str(e))
                error_resp = RemoteInferenceResponse(error_response=error)
                self._send_response(error_resp)

    def _handle_new_input(self):
        """Process incoming messages from the input socket."""
        try:
            request: RemoteInferenceRequest = recv_remote_inference_request(
                self.input_socket
            )

            if request.type == RemoteInferenceRequestType.STARTUP:
                self._handle_startup_request(request.startup_request)
            elif request.type == RemoteInferenceRequestType.PROCESS:
                self._handle_generate_request(request.process_request)
            elif request.type == RemoteInferenceRequestType.ABORT:
                self._handle_abort_request(request.abort_request)
            elif request.type == RemoteInferenceRequestType.CONFIG:
                self._handle_config_request(request.config_request)

        except Exception as e:
            logger.error("Error processing input: %s", str(e), exc_info=True)
            error = ErrorResponse(request_id="", error_message=str(e))
            error_resp = RemoteInferenceResponse(error_response=error)
            self._send_response(error_resp)

    def _send_outputs(self, request_outputs: List[RequestOutput]):
        """Send request outputs to the output socket."""
        for chunk in request_outputs:
            request_id = chunk.seq_id
            if request_id not in self._active_generations:
                logger.error("Received output for unknown request: %s", request_id)
                continue

            sender_state = self._active_generations[request_id]
            is_first_chunk = sender_state.last_text_len == 0

            new_text = chunk.text[sender_state.last_text_len :]
            new_token_ids = chunk.token_ids[sender_state.last_token_ids_len :]

            prompt_token_ids = chunk.prompt_token_ids if is_first_chunk else []

            finish_reason = chunk.finish_reason if chunk.finish_reason else ""

            output_response = OutputResponse(
                request_id=chunk.seq_id,
                text=new_text,
                token_ids=new_token_ids,
                prompt_token_ids=prompt_token_ids,
                finish_reason=finish_reason,
                finished=chunk.finished,
                is_delta=True,
                is_first_chunk=is_first_chunk,
            )

            response = RemoteInferenceResponse(output_response=output_response)

            sender_state.last_text_len = len(chunk.text)
            sender_state.last_token_ids_len = len(chunk.token_ids)
            self._send_response(response)

    def _handle_startup_request(self, startup_request: StartupRequest):
        """Handle a startup request."""
        if not startup_request.client_ready:
            return

        startup_response = StartupResponse(server_ready=True)

        response = RemoteInferenceResponse(startup_response=startup_response)

        send_remote_inference_response(self.output_socket, response)

    def _handle_generate_request(self, request: ProcessRequest):
        """Handle a generation request."""
        request_id = request.request_id
        logger.info("Processing generation request: %s", request_id)

        try:
            # Convert vajra_proto SamplingParams to vajra SamplingParams
            sampling_params = SamplingParams(
                temperature=request.sampling_params.temperature,
                top_p=request.sampling_params.top_p,
                top_k=request.sampling_params.top_k,
                ignore_eos=request.sampling_params.ignore_eos,
                max_tokens=request.sampling_params.max_tokens,
            )

            self._active_generations[request_id] = SenderState()
            self.engine.add_request(
                prompt=request.prompt,
                sampling_params=sampling_params,
                prompt_token_ids=[],
                seq_id=request_id,
            )

        except Exception as e:
            error_resp = RemoteInferenceResponse()
            error_resp.error = ErrorResponse()
            error_resp.error.request_id = request_id
            error_resp.error.error_message = str(e)
            self._send_response(error_resp)

    def _handle_abort_request(self, request: AbortRequest):
        """Handle an abort request."""
        request_id = request.request_id
        if request_id in self._active_generations:
            # TODO handle abort
            # self.engine.abort(request_id)
            del self._active_generations[request_id]

            output_response = OutputResponse(
                request_id=request_id,
                text="",
                token_ids=[],
                prompt_token_ids=[],
                finish_reason="aborted",
                finished=True,
                is_delta=False,
                is_first_chunk=False,
            )

            response = RemoteInferenceResponse(output_response=output_response)

            self._send_response(response)

    def _handle_config_request(self, request: ConfigRequest):
        """Handle a model config request."""
        config: ModelConfig = self.engine.controller.get_model_config()

        response = RemoteInferenceResponse(config.native_handle)

        self._send_response(response)

    def _send_response(self, response: RemoteInferenceResponse):
        """Send a response through the output socket."""
        send_remote_inference_response(self.output_socket, response)

    def shutdown(self):
        """Clean shutdown of the server."""
        logger.info("Shutting down RemoteInferenceEngineServer")
        self._running = False

        # Abort all active generations
        for request_id in self._active_generations:
            try:
                # TODO handle abort
                # self.engine.abort(request_id)
                pass
            except Exception as e:
                logger.error(f"Error aborting generator {request_id}: {e}")
        self._active_generations.clear()

        # Wait for threads to finish
        if self.input_thread.is_alive():
            self.input_thread.join(timeout=2.0)
        if self.output_thread.is_alive():
            self.output_thread.join(timeout=2.0)
        if self.health_thread.is_alive():
            self.health_thread.join(timeout=2.0)


def run_remote_inference_engine_server(
    inference_engine_config: InferenceEngineConfig,
    ipc_path: str,
    verbose: bool,
    engine_alive,
) -> None:
    """Run the engine in a separate process."""
    logger.info("Starting engine with IPC path: %s", ipc_path)

    # Track shutdown state
    is_shutting_down = False

    try:
        os.makedirs(os.path.dirname(ipc_path), exist_ok=True)
        engine_wrapper = InferenceEngine(inference_engine_config)
        logger.info("Engine wrapper created")

        def sigterm_handler(signum, frame):
            nonlocal is_shutting_down
            if is_shutting_down:
                logger.debug("Shutdown already in progress, ignoring signal")
                return

            is_shutting_down = True
            logger.info("Received termination signal, shutting down")
            raise KeyboardInterrupt()

        signal.signal(signal.SIGTERM, sigterm_handler)
        signal.signal(signal.SIGINT, sigterm_handler)

        context = ZmqContext()
        server = RemoteInferenceEngineServer(context, engine_wrapper, ipc_path)
        logger.info("RemoteInferenceEngineServer created and running")
        server.run()

    except KeyboardInterrupt:
        logger.info("Server interrupted, shutting down")
    except Exception as e:
        if engine_alive is not None:
            engine_alive.value = False
        logger.error("Exception in engine process: %s", str(e), exc_info=True)
        raise e
    finally:
        if engine_alive is not None:
            engine_alive.value = False
        logger.info("Engine process terminated")
