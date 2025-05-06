import asyncio
import re
import time
from typing import Any, Dict, List, Optional, Protocol

from fastapi import Body, FastAPI, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from kirara_ai.im.adapter import IMAdapter
from kirara_ai.im.message import ImageMessage, IMMessage, TextMessage, VoiceMessage
from kirara_ai.im.sender import ChatSender
from kirara_ai.logger import get_logger
from kirara_ai.web.app import WebServer
from kirara_ai.workflow.core.dispatch import WorkflowDispatcher

# 全局变量，用于跟踪是否已经设置了路由
_is_first_setup = True
# 全局变量，用于存储所有已授权的API密钥
_authorized_api_keys: List[str] = []


class HttpLegacyConfig(BaseModel):
    """HTTP Legacy API 配置"""

    api_key: Optional[str] = Field(
        description="自定义的API密钥，设置后，请求接口时需要带上这个密钥，若填空则不校验。", default=None)
    host: Optional[str] = Field(description="已废弃，HTTP API 服务器地址，设置后将启动独立服务器。",
                                default=None, json_schema_extra={"hidden_unset": True})
    port: Optional[int] = Field(description="已废弃，HTTP API 服务器端口，设置后将启动独立服务器。",
                                default=None, json_schema_extra={"hidden_unset": True})
    model_config = ConfigDict(extra="allow")


class ResponseResult:
    def __init__(self, message=None, voice=None, image=None, result_status="SUCCESS"):
        self.result_status = result_status
        self.message = (
            []
            if message is None
            else message if isinstance(message, list) else [message]
        )
        self.voice = (
            [] if voice is None else voice if isinstance(voice, list) else [
                voice]
        )
        self.image = (
            [] if image is None else image if isinstance(image, list) else [
                image]
        )

    def to_dict(self):
        return {
            "result": self.result_status,
            "message": self.message,
            "voice": self.voice,
            "image": self.image,
        }

    def pop_all(self):
        self.message = []
        self.voice = []
        self.image = []


class MessageHandler(Protocol):
    async def __call__(self, message: IMMessage) -> None: ...


class V2Request:
    def __init__(self, session_id: str, username: str, message: str, request_time: str):
        self.session_id = session_id
        self.username = username
        self.message = message
        self.result = ResponseResult()
        self.request_time = request_time
        self.done = False
        self.response_event = asyncio.Event()


class HttpLegacyAdapter(IMAdapter):
    """HTTP Legacy API适配器"""

    dispatcher: WorkflowDispatcher
    web_server: WebServer

    def __init__(self, config: HttpLegacyConfig):
        self.config = config
        self.app = FastAPI(title="HTTP Legacy API")
        self.request_dic: Dict[str, V2Request] = {}
        self.logger = get_logger("HTTP-Legacy-Adapter")

    async def convert_to_message(self, raw_message: Any) -> IMMessage:
        data = raw_message
        username = data.get("username", "某人")
        message_text = data.get("message", "")
        session_id = data.get("session_id", "friend-default_session")

        if (
            session_id.startswith("group-")
            and len(session_id.split("-")) == 2
            and ":" in session_id.split("-")[1]
        ):
            # group-group_id:user_id
            ids = session_id.split("-")[1].split(":")
            sender = ChatSender.from_group_chat(
                user_id=ids[1], group_id=ids[0], display_name=username
            )
        else:
            sender = ChatSender.from_c2c_chat(
                user_id=session_id, display_name=username)

        return IMMessage(
            sender=sender,
            message_elements=[TextMessage(text=message_text)],
            raw_message={"session_id": session_id, **data},
        )

    async def handle_message_elements(self, result: ResponseResult, message: IMMessage):
        for element in message.message_elements:
            if isinstance(element, VoiceMessage):
                result.voice.append(await element.get_base64_url())
            elif isinstance(element, ImageMessage):
                result.image.append(await element.get_base64_url())
            else:
                result.message.append(element.to_plain())

    def verify_api_key(self, request: Request) -> bool:
        """验证API密钥"""
        if not self.config.api_key:
            return True

        auth_header = request.headers.get("Authorization", "")
        # 支持 Bearer 认证和直接传递 API Key
        if auth_header.startswith("Bearer "):
            auth_header = auth_header[7:]  # 移除 "Bearer " 前缀

        return auth_header == self.config.api_key or auth_header in _authorized_api_keys

    def create_auth_error_response(self):
        """创建认证失败的响应"""
        return JSONResponse(
            content=ResponseResult(
                message="认证失败", result_status="FAILED").to_dict(),
            status_code=401
        )

    def setup_routes(self, target_app=None):
        app = target_app if target_app else self.app

        async def verify_auth(request: Request):
            if not self.verify_api_key(request):
                return self.create_auth_error_response()
            return None

        @app.post("/v1/chat")
        async def v1_chat(request: Request, data: dict = Body(...)):
            auth_response = await verify_auth(request)
            if auth_response:
                return auth_response

            message = await self.convert_to_message(data)
            result = ResponseResult()

            async def handle_response(resp_message: IMMessage):
                await self.handle_message_elements(result, resp_message)

            message.sender.raw_metadata["callback_func"] = handle_response

            await self.dispatcher.dispatch(self, message)
            return result.to_dict()

        @app.post("/v2/chat")
        async def v2_chat(request: Request, data: dict = Body(...)):
            auth_response = await verify_auth(request)
            if auth_response:
                return auth_response

            request_time = str(int(time.time() * 1000))

            message = await self.convert_to_message(data)
            assert message.raw_message is not None
            
            session_id = message.raw_message["session_id"]

            bot_request = V2Request(
                session_id,
                message.sender.display_name,
                data.get("message", ""),
                request_time,
            )
            self.request_dic[request_time] = bot_request

            async def handle_response(resp_message: IMMessage):
                await self.handle_message_elements(bot_request.result, resp_message)
                bot_request.response_event.set()

            message.sender.raw_metadata["callback_func"] = handle_response
            asyncio.create_task(self.dispatcher.dispatch(self, message))
            return request_time

        @app.get("/v2/chat/response")
        async def v2_chat_response(request: Request, request_id: str = Query(...)):
            auth_response = await verify_auth(request)
            if auth_response:
                return auth_response

            request_id = re.sub(
                r'^[%22%27"\'"]*|[%22%27"\'"]*$', "", request_id)

            bot_request = self.request_dic.get(request_id)
            if bot_request is None:
                return ResponseResult(
                    message="没有更多了！", result_status="FAILED"
                ).to_dict()

            await bot_request.response_event.wait()
            bot_request.response_event.clear()

            response = bot_request.result.to_dict()
            bot_request.result = ResponseResult()

            if bot_request.done:
                self.request_dic.pop(request_id)

            return response

    async def send_message(self, message: IMMessage, recipient: ChatSender):
        """此处负责 HTTP 的响应逻辑"""
        await recipient.raw_metadata["callback_func"](message)

    @property
    def is_standalone(self):
        return self.config.host

    async def _start_standalone_server(self):
        """启动独立HTTP服务器"""

        # 使用 hypercorn 配置来正确处理关闭信号
        from hypercorn.asyncio import serve
        from hypercorn.config import Config
        from hypercorn.logging import Logger

        from kirara_ai.logger import HypercornLoggerWrapper

        config = Config()
        host = self.config.host
        port = self.config.port or 18560
        config.bind = [f"{host}:{port}"]
        config._log = Logger(config)
        config._log.access_logger = HypercornLoggerWrapper(self.logger)  # type: ignore
        config._log.error_logger = HypercornLoggerWrapper(self.logger)  # type: ignore
        self.server_task = asyncio.create_task(serve(self.app, config))  # type: ignore

    async def start(self):
        """启动HTTP服务器"""
        global _is_first_setup, _authorized_api_keys

        if self.is_standalone:
            self.logger.warning("正在使用过时的独立模式，请尽快更新为集成模式。")
            await self._start_standalone_server()
            self.setup_routes()
        else:
            # 为所有的路由添加前缀
            if _is_first_setup:
                # 直接往 self.web_server.app 注册路由，而不是mount_app
                self.setup_routes(target_app=self.web_server.app)
                _is_first_setup = False
            else:
                if self.config.api_key and self.config.api_key not in _authorized_api_keys:
                    _authorized_api_keys.append(self.config.api_key)

        # 启动清理过期请求的任务
        self.cleanup_task = asyncio.create_task(
            self.cleanup_expired_requests())

    async def cleanup_expired_requests(self):
        """清理过期的请求"""
        while True:
            now = time.time()
            expired_keys = [
                key
                for key, req in self.request_dic.items()
                if now - int(key) / 1000 > 600
            ]
            for key in expired_keys:
                self.request_dic.pop(key)
            await asyncio.sleep(60)

    async def stop(self):
        """停止HTTP服务器"""
        global _authorized_api_keys

        # 如果有API密钥，从授权列表中移除
        if self.config.api_key and self.config.api_key in _authorized_api_keys:
            _authorized_api_keys.remove(self.config.api_key)

        if self.is_standalone and hasattr(self, "server_task"):
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                self.logger.error(f"Error during server shutdown: {e}")

        if hasattr(self, "cleanup_task"):
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
