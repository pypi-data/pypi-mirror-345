import json
from typing import Any
from enum import Enum


class RequestActions(Enum):
    ACT_SUB_TO_DEVICE = "sub-to-device"
    ACT_UNSUB_FROM_DEVUCE = "unsub-from-device"
    ACT_SEND_TO_DEVICE = "send-to-device"
    ACT_GET_DEVICES_LIST = "get-device-list"
    ACT_TRANSFERS_TO_WS_CLIENTS = "transfers-to-ws-clients"

    EVT_ON_DEVICE_MSG = "on-device-msg"
    EVT_ON_CLIENT_MSG = "on-client-msg"


    def __repr__(self) -> str:
        return self.value


class Request:
    def __init__(self, action: RequestActions, device_name: str = "", data: Any = None, to_client_id: str = None, from_client_id: str = None) -> None:
        self.action: RequestActions = action
        self.device_name: str = device_name
        self.message: str = json.dumps(data) if data else ""
        self.token = None
        self.to_client_id = to_client_id
        self.from_client_id = from_client_id

    def to_json(self):
        return json.dumps({
            "action": self.action.value,
            "device_name": self.device_name,
            "message": self.message,
            "to_client_id": self.to_client_id,
            "from_client_id": self.from_client_id,
            "token": self.token
        })
