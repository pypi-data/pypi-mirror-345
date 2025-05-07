import asyncio
import atexit
import multiprocessing
import os
import signal
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import AsyncGenerator, AsyncIterator, Optional

import uvicorn
import uvloop
from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.datastructures import State

from vajra.config import ModelConfig
from vajra.engine.remote_inference_engine import RemoteInferenceEngineClient
from vajra.engine.remote_inference_engine.constants import (
    IPC_HEALTH_EXT,
    IPC_INPUT_EXT,
    IPC_OUTPUT_EXT,
)
from vajra.engine.remote_inference_engine.server import (
    run_remote_inference_engine_server,
)
from vajra.entrypoints.openai.config import OpenAIServerConfig
from vajra.entrypoints.openai.protocol import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    CompletionRequest,
    ErrorResponse,
)
from vajra.entrypoints.openai.serving_chat import OpenAIServingChat
from vajra.entrypoints.openai.serving_completion import OpenAIServingCompletion
from vajra.logger import init_logger
from vajra.utils import get_random_ipc_path

TIMEOUT_KEEP_ALIVE = 5  # seconds

logger = init_logger(__name__)

shutdown_event = asyncio.Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Entering lifespan context manager")
    try:
        yield
    finally:
        # Signal shutdown to all components
        shutdown_event.set()
        # Wait a moment for cleanup
        await asyncio.sleep(0.1)
        # Ensure app state including engine ref is gc'd
        if hasattr(app, "state"):
            del app.state
        logger.info("Exiting lifespan context manager")


@asynccontextmanager
async def build_engine_client(
    config: OpenAIServerConfig,
) -> AsyncIterator[RemoteInferenceEngineClient]:
    """Build engine client with multiprocessing support."""
    logger.info("Building engine client")
    base_ipc_path = get_random_ipc_path()
    engine_client: Optional[RemoteInferenceEngineClient] = None

    def cleanup_ipc():
        for suffix in [IPC_HEALTH_EXT, IPC_INPUT_EXT, IPC_OUTPUT_EXT]:
            socket_path = base_ipc_path + suffix
            if os.path.exists(socket_path):
                try:
                    os.remove(socket_path)
                    logger.info("Cleaned up IPC path %s", socket_path)
                except OSError as e:
                    logger.warning(f"Failed to cleanup IPC path: {e}")
            else:
                logger.warning("IPC path %s does not exist", socket_path)

    context = multiprocessing.get_context("spawn")
    engine_alive = multiprocessing.Value("b", True, lock=False)

    engine_process = context.Process(
        target=run_remote_inference_engine_server,
        args=(
            config.inference_engine_config,
            base_ipc_path,
            config.log_level == "debug",
            engine_alive,
        ),
    )

    try:
        engine_process.start()
        engine_pid = engine_process.pid
        assert engine_pid is not None, "Engine process failed to start."
        logger.info("Started engine process with PID %d", engine_pid)

        # Register cleanup only after successful start
        atexit.register(cleanup_ipc)

        engine_client = RemoteInferenceEngineClient(base_ipc_path, engine_pid)
        engine_client.connect()

        yield engine_client
    finally:
        logger.info("Called cleanup on engine client")
        try:
            if engine_process.is_alive():
                engine_process.terminate()
                engine_process.join(timeout=10)
                if engine_process.is_alive():
                    logger.warning("Force killing engine process")
                    engine_process.kill()
                    engine_process.join(timeout=1)
        except Exception as e:
            logger.error(f"Error during engine process cleanup: {e}")

        if engine_client is not None:
            try:
                engine_client.close()
            except Exception as e:
                logger.error(f"Error closing engine client: {e}")

        cleanup_ipc()
        # Deregister cleanup since we already did it
        atexit.unregister(cleanup_ipc)


router = APIRouter()


def chat(request: Request) -> Optional[OpenAIServingChat]:
    return request.app.state.openai_serving_chat


def completion(request: Request) -> Optional[OpenAIServingCompletion]:
    return request.app.state.openai_serving_completion


def engine_client(request: Request) -> RemoteInferenceEngineClient:
    return request.app.state.engine_client


@router.get("/v1/models")
async def show_available_models(raw_request: Request):
    logger.info("Received request to show available models")
    handler = chat(raw_request)
    assert handler is not None

    models_ = await handler.show_available_models()
    return JSONResponse(content=models_.model_dump())


@router.post("/v1/chat/completions")
async def create_chat_completion(request: ChatCompletionRequest, raw_request: Request):
    logger.info("Received request to create chat completion")
    handler = chat(raw_request)
    assert handler is not None

    generator = await handler.create_chat_completion(request, raw_request)
    if isinstance(generator, ErrorResponse):
        return JSONResponse(content=generator.model_dump(), status_code=generator.code)
    if request.stream:
        assert isinstance(generator, AsyncGenerator)
        return StreamingResponse(content=generator, media_type="text/event-stream")
    else:
        assert isinstance(generator, ChatCompletionResponse)
        return JSONResponse(content=generator.model_dump())


@router.post("/v1/completions")
async def create_completion(request: CompletionRequest, raw_request: Request):
    logger.info("Received request to create completion")
    handler = completion(raw_request)
    assert handler is not None

    generator = await handler.create_completion(request, raw_request)
    if isinstance(generator, ErrorResponse):
        return JSONResponse(content=generator.model_dump(), status_code=generator.code)
    if request.stream:
        assert isinstance(generator, AsyncGenerator)
        return StreamingResponse(content=generator, media_type="text/event-stream")
    else:
        assert isinstance(generator, ChatCompletionResponse)
        return JSONResponse(content=generator.model_dump())


def build_app(config: OpenAIServerConfig) -> FastAPI:
    logger.info("Building FastAPI app")
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_, exc):
        err = ErrorResponse(
            message=str(exc), type="BadRequestError", code=HTTPStatus.BAD_REQUEST
        )
        return JSONResponse(err.model_dump(), status_code=HTTPStatus.BAD_REQUEST)

    if config.api_key:

        @app.middleware("http")
        async def authentication(request: Request, call_next):
            root_path = (
                "" if config.server_root_path is None else config.server_root_path
            )
            if request.method == "OPTIONS":
                return await call_next(request)
            if not request.url.path.startswith(f"{root_path}/v1"):
                return await call_next(request)

            api_key = config.api_key or ""  # Convert None to empty string if needed
            if request.headers.get("Authorization") != f"Bearer {api_key}":
                return JSONResponse(content={"error": "Unauthorized"}, status_code=401)
            return await call_next(request)

    return app


async def init_app_state(
    engine_client: RemoteInferenceEngineClient,
    model_config: ModelConfig,
    state: State,
    config: OpenAIServerConfig,
) -> None:
    logger.info("Initializing app state")
    served_model_names = [model_config.model]

    state.engine_client = engine_client

    state.openai_serving_chat = OpenAIServingChat(
        engine_client,
        model_config,
        served_model_names,
        config.response_role,
        config.chat_template,
    )
    state.openai_serving_completion = OpenAIServingCompletion(
        engine_client, model_config, served_model_names
    )
    logger.info("Created OpenAIServingChat and OpenAIServingCompletion")


async def run_app(config: OpenAIServerConfig, **uvicorn_kwargs) -> None:
    logger.info("Launching OpenAI compatible server with config: %s", config)

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        # Set the shutdown event
        if not shutdown_event.is_set():
            shutdown_event.set()
        # Let the async loop handle the rest

    # Register signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, signal_handler)

    try:
        async with build_engine_client(config) as engine_client:
            app = build_app(config)
            model_config = engine_client.get_model_config()
            await init_app_state(engine_client, model_config, app.state, config)

            uv_config = uvicorn.Config(
                app,
                host=config.host,
                port=config.port,
                log_level=config.log_level,
                ssl_keyfile=config.ssl_keyfile,
                ssl_certfile=config.ssl_certfile,
                ssl_ca_certs=config.ssl_ca_certs,
                ssl_cert_reqs=config.ssl_cert_reqs,
                timeout_keep_alive=TIMEOUT_KEEP_ALIVE,
            )
            server = uvicorn.Server(uv_config)

            # Add shutdown handler
            async def shutdown():
                await shutdown_event.wait()
                await server.shutdown()

            # Run server with shutdown task
            shutdown_task = asyncio.create_task(shutdown())
            await server.serve()
            await shutdown_task
    except KeyboardInterrupt:
        logger.info("Server shutdown due to KeyboardInterrupt")
    finally:
        # Ensure shutdown event is set
        shutdown_event.set()


if __name__ == "__main__":
    config: OpenAIServerConfig = OpenAIServerConfig.create_from_cli_args()
    logger.info("Starting server with configuration: %s", config)
    uvloop.install()
    asyncio.run(run_app(config))
