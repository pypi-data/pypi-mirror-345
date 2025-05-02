from __future__ import annotations
from typing import Any
import traceback
import json
import time
import threading
from collections.abc import Callable
from websocket import WebSocketApp, setdefaulttimeout

from .request import Request, RequestActions
from .config import Configuration
from .agent import Agent
from .timer import Timer


class Gateway:
    def __init__(self, host: str, port: int, secure: bool = False, config: Configuration = None) -> None: 
        self.config = config if config is not None else Configuration()
        
        self._host = host
        self._port = port
        self._auth_token = None

        host_parts = host.split("/")
        url = f"{'wss' if secure else 'ws'}://{host_parts.pop(0)}:{port}"
        if len(host_parts):
            url = f"{url}/{'/'.join(host_parts)}"

        self.wss = WebSocketApp(
            url, 
            on_open=self._on_connection_open,
            on_close=self._on_connection_close,
            on_message=self._on_message,
            on_error=self._on_error
        )

        self.is_connected = False
        self.thread = None

        self._on_connect_callbacks: list[Callable[[None], None]] = []
        self._on_close_callbacks: list[Callable[[int, str], None]] = []
        self._on_error_callbacks: list[Callable[[Exception], None]] = []
        self._on_client_msg_callbacks: list[Callable[[Any, str], None]] = []

        self._agents: dict[str, Agent] = {}

    def _on_connection_open(self, _: WebSocketApp):
        self.is_connected = True
        for cb_func in self._on_connect_callbacks:
            cb_func()

    def _on_connection_close(self, _: WebSocketApp, close_status_code, close_msg):
        self.is_connected = False
        for cb_func in self._on_close_callbacks:
            cb_func(close_status_code, close_msg)

    def _on_error(self, _: WebSocketApp, err: Exception):
        for cb_func in self._on_error_callbacks:
            cb_func(err)

    def _on_message(self, wsa: WebSocketApp, message: str):
        try: 
            data = json.loads(message)

            if "action" in data:
                if data["action"] == RequestActions.ACT_GET_DEVICES_LIST.value:
                    device_list = data.get("devices", [])

                    # Adding new agents
                    for d_name in device_list:
                        if d_name not in self._agents:
                            self._agents[d_name] = Agent(self, d_name)

                    # Removing missing agents
                    for agent in self._agents.values():
                        if agent.device_name not in device_list:
                            for cb in self._agents[agent.device_name].on_disconnect_handlers.values():
                                try:
                                    cb(self._agents[agent.device_name])
                                except Exception as e:
                                    traceback.print_exc()
                            del self._agents[agent.device_name]

                elif data["action"] == RequestActions.EVT_ON_DEVICE_MSG.value:
                    device_name = data.get("device_name")
                    msg = data.get("message", "")

                    if device_name in self._agents:
                        self._agents[device_name].handle_message(msg)

                elif data["action"] == RequestActions.EVT_ON_CLIENT_MSG.value:
                    msg = data.get("message", "")
                    from_client_id = data.get("from_client_id", None)

                    for cb in self._on_client_msg_callbacks:
                        try:
                            cb(msg, from_client_id)
                        except Exception as e:
                            traceback.print_exc()
        except Exception as err:
            self._on_error(wsa, err)

    def set_auth_token(self, token: str):
        self._auth_token = token

    def connect(self, wait_for_connection: bool = True, connection_timeout_sec: int = 10) -> None:
        try:
            setdefaulttimeout(connection_timeout_sec)

            self.thread = threading.Thread(target=self.wss.run_forever)
            self.thread.start()
            
            if wait_for_connection:
                start_time = time.time()
                while not self.is_connected:
                    now_time = time.time()
                    if now_time - start_time > connection_timeout_sec:
                        raise Exception("WSP Connection Timeout")
        except Exception as err:
            self.close()
            raise err

    def close(self) -> None:
        if self.is_connected:
            self.wss.close()
        self.thread.join()

    def on_client_msg(self, callback: Callable[[Any], None]) -> None:
        self._on_client_msg_callbacks.append(callback)

    def on_error(self, callback: Callable[[Exception], None]) -> None:
        self._on_error_callbacks.append(callback)

    def send(self, request: Request) -> None:
        if self._auth_token:
            request.token = self._auth_token
        self.wss.send(request.to_json())

    def request_agent_list(self) -> None:
        self.send(Request(RequestActions.ACT_GET_DEVICES_LIST))

    def wait_for_agent(self, agent_name: str, timeout_sec: int = 30) -> Agent:
        self.wait_for_agents(timeout_sec, agent_name)
        return self._agents.get(agent_name, None)

    def wait_for_agents(self, timeout_sec: int = 30, agent_name: str = None) -> list[Agent]:
        if not self._agents.keys():
            self.request_agent_list()
        
        start_time = time.time()
        while not self._agents.keys() or (agent_name is not None and agent_name not in self._agents):
            Timer.wait(0.001)
            now_time = time.time()
            if now_time - start_time > timeout_sec:
                break
        
        return list(self._agents.values())

    def send_to_clients(self, msg: Any, to_client_id: str = None) -> None:
        self.send(Request(
            RequestActions.ACT_TRANSFERS_TO_WS_CLIENTS,
            data=msg,
            to_client_id=to_client_id
        ))
