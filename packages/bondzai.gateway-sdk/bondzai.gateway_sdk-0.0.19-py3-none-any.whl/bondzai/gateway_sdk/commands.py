from dataclasses import dataclass

from .enums import MessageModule, CommandOperationID, LogCommand, DBMCommand


@dataclass
class CommandGet:
    itemid: int

    def get_size(self) -> int:
        return 2

    def to_dict(self) -> dict:
        return {
            "itemid": self.itemid,
        }


@dataclass
class CommandStartLogGetKpi:
    itemid: int
    index: int

    def get_size(self) -> int:
        return 6

    def to_dict(self) -> dict:
        return {
            "itemid": self.itemid,
            "index": self.index,
        }
    


@dataclass
class CommandStartDbmExportRow:
    itemid: int
    handle: int
    key: str
    index: int = -1

    def get_size(self) -> int:
        return 4 + (4 if len(self.key) == 0 else len(self.key))

    def to_dict(self) -> dict:
        return {
            "itemid": self.itemid,
            "handle": self.handle,
            "key": self.key,
            "index": self.index,
        }


OP_TO_COMMAND_TYPES = {
    MessageModule.LOG: {
        CommandOperationID.CMD_GET : CommandGet,            
        CommandOperationID.CMD_START : {
            LogCommand.LOG_GET_KPI.value: CommandStartLogGetKpi
        }
    },
    MessageModule.DBM: {
        CommandOperationID.CMD_GET : CommandGet,            
        CommandOperationID.CMD_START : {
            DBMCommand.DBM_EXPORT_ROW.value: CommandStartDbmExportRow
        }
    },
    MessageModule.RUN: {
        CommandOperationID.CMD_GET : CommandGet,            
    },
    MessageModule.MAL: {
        CommandOperationID.CMD_GET : CommandGet,            
    }
}


def get_command_class(command_op_id: CommandOperationID, module: MessageModule, *args):
    if module not in OP_TO_COMMAND_TYPES:
        return None

    if command_op_id not in OP_TO_COMMAND_TYPES[module]:
        return None

    if command_op_id in (CommandOperationID.CMD_SET, CommandOperationID.CMD_START):
        return OP_TO_COMMAND_TYPES[module][command_op_id].get(args[0][0], None)

    return OP_TO_COMMAND_TYPES[module][command_op_id]
