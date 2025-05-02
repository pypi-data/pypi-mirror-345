from typing import Any
from enum import Enum

from .utils import b2b64
from .config import Configuration
from .timer import Timer
from .enums import MessageModule, EventOperationID, CommandOperationID
from .events import EventHeader, get_event_class
from .commands import get_command_class


class MessageType(Enum):
    COMMAND = 0
    RESPONSE = 1
    ERR = 2
    EVENT = 3


class MessageHeader:
    current_id: int = 0

    def __init__(
        self, 
        msg_type: MessageType, 
        mod: MessageModule, 
        operation: EventOperationID,
        session: bytes = Configuration.session,
        id_num: int = None
    ) -> None:
        self.session = session
        self.operation = operation
        self.mod = mod
        self.type = msg_type
        if id_num is None:
            self.id = MessageHeader.current_id
            MessageHeader.current_id = (MessageHeader.current_id + 1) % 255
        else:
            self.id = id_num

    def to_dict(self):
        return {
            "session": b2b64(self.session),
            "id": self.id,
            "op": self.operation.value,
            "typ": self.type.value,
            "mod": self.mod.value
        }


class Message:
    def __init__(self) -> None:
        self.header: MessageHeader = None
        self.payloads: list[Any] = []

    def to_dict(self) -> dict:
        raise NotImplementedError()


class EventMessage(Message):
    def __init__(self, operation: EventOperationID, module: MessageModule = MessageModule.RUN) -> None:
        super().__init__()
        self.header = MessageHeader(MessageType.EVENT, module, operation)
        self.payloads = []

    def add_payload(self, *args):
        event_class = get_event_class(self.header.operation)
        if event_class is None:
            raise Exception(f"Operation {self.header.operation} has no type associated")

        event = event_class(*args)
        header = EventHeader(
            self.header.mod.value,
            Configuration.app_id,
            Timer.get_timestamp(),
            event.get_size()
        )

        self.payloads.append({
            "header": header,
            "event": event
        })

        return self

    def to_dict(self) -> dict:
        return {
            "header": self.header.to_dict(),
            "payloads": [{
                "header": pl["header"].to_dict(),
                "data": pl["event"].to_dict()
            } for pl in self.payloads]
        }


class CommandMessage(Message):
    def __init__(self, operation: CommandOperationID, module: MessageModule) -> None:
        super().__init__()
        self.header = MessageHeader(MessageType.COMMAND, module, operation)
        self.payloads = []

    def add_payload(self, *args):
        command_class = get_command_class(self.header.operation, self.header.mod, args)
        if command_class is None:
            raise Exception(f"Operation {self.header.operation} has no type associated")

        command = command_class(*args)

        self.payloads.append({
            "command": command
        })

    def to_dict(self) -> dict:
        return {
            "header": self.header.to_dict(),
            "payloads": [{
                "data": pl["command"].to_dict()
            } for pl in self.payloads]
        }
