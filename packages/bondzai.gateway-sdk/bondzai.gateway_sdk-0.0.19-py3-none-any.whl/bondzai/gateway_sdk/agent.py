# coding: utf-8

from __future__ import annotations
from collections.abc import Callable
import traceback
import uuid

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .gateway import Gateway

from .request import Request, RequestActions
from .message import EventMessage, Message, MessageModule, MessageType, CommandMessage
from .enums import EventOperationID, AgentAIMode, AgentAIType, AgentTriggerType, AgentRecordMode, CommandOperationID, \
    LogCommand, DBMCommandParameter, DBMTable, DBMCommand, LogCommandParameter, RUNCommandParameter, MALCommandParameter
from .utils import unpack_buffer_to_list, b642b
from .timer import Timer

from .transcode import transcode


class Agent:
    def __init__(self, gateway: Gateway, device_name: str) -> None:
        self.device_name = device_name
        self.gateway = gateway

        self._wait_response = {}

        self._on_log_handlers: dict[str, Callable[[Agent, str], None]] = {}
        self._on_event_handlers: dict[str, Callable[[Agent, EventOperationID, dict], None]] = {}
        self._on_exception_handlers: dict[str, Callable[[Agent, dict], None]] = {}

        self._on_flowsteps_ack_handlers: dict[str, Callable[[Agent, dict], None]] = {}
        self._on_ack_handlers: dict[str, Callable[[Agent, dict], None]] = {}
        # special ack very useful
        self._on_train_done_handlers: dict[str, Callable[[Agent, dict], None]] = {}

        # final result
        self._on_final_process_result_handlers: dict[str, Callable[[Agent, dict], None]] = {}
        # result
        self._on_data_acq_result_handlers: dict[str, Callable[[Agent, dict], None]] = {}
        self._on_data_transform_result_handlers: dict[str, Callable[[Agent, dict], None]] = {}
        self._on_enroll_result_handlers: dict[str, Callable[[Agent, dict], None]] = {}
        self._on_infer_result_handlers: dict[str, Callable[[Agent, dict], None]] = {}
        self._on_dataset_preparation_result_handlers: dict[str, Callable[[Agent, dict], None]] = {}
        self._on_training_result_handlers: dict[str, Callable[[Agent, dict], None]] = {}

        self.on_disconnect_handlers: dict[str, Callable[[Agent], None]] = {}

    def handle_message(self, msg: dict) -> None:
        if "header" in msg:
            mod = MessageModule(msg['header']['mod'])
            typ = MessageType(msg['header']['typ'])
            msg_id = msg["header"]["id"]
            operation = EventOperationID(msg['header']['op'])

            data: dict = None
            if "payloads" in msg and len(msg["payloads"]):
                data = msg["payloads"][0]['data']
                data_transcode = transcode(operation, data)

            if typ == MessageType.RESPONSE:
                if msg_id in self._wait_response:
                    self._wait_response[msg_id] = data

            def exec_callback(func, *args):
                try:
                    func(self, *args)
                except:
                    traceback.print_exc()

            if typ == MessageType.EVENT:
                if mod == MessageModule.LOG:
                    if operation == EventOperationID.EVT_EXT_LOG:
                        content = data.get("msg", "")
                        for callback in self._on_log_handlers.values():
                            exec_callback(callback, content)
                else:
                    if operation == EventOperationID.EVT_EXT_ASL_RESULT:
                        for callback in self._on_final_process_result_handlers.values():
                            exec_callback(callback, data_transcode)
                    # Flow Steps Result
                    elif operation == EventOperationID.EVT_EXT_DATA_ACQ_RESULT:
                        for callback in self._on_data_acq_result_handlers.values():
                            exec_callback(callback, data_transcode)
                    elif operation == EventOperationID.EVT_EXT_DATA_TRANSFORM_RESULT:
                        for callback in self._on_data_transform_result_handlers.values():
                            exec_callback(callback, data_transcode)
                    elif operation == EventOperationID.EVT_EXT_VM_RESULT:
                        for callback in self._on_infer_result_handlers.values():
                            exec_callback(callback, data_transcode)
                    elif operation == EventOperationID.EVT_EXT_ENROLL_RESULT:
                        for callback in self._on_enroll_result_handlers.values():
                            exec_callback(callback, data_transcode)
                    elif operation == EventOperationID.EVT_EXT_DATASET_PREPARATION_RESULT:
                        for callback in self._on_dataset_preparation_result_handlers.values():
                            exec_callback(callback, data_transcode)
                    elif operation == EventOperationID.EVT_EXT_TRAINING_RESULT:
                        for callback in self._on_training_result_handlers.values():
                            exec_callback(callback, data_transcode)
                    # Acknowledge
                    elif operation == EventOperationID.EVT_EXT_PROCESS_ACK:
                        evt_id = data_transcode.get("evt_id", None)
                        process_id = data_transcode.get("process_id", 0)
                        if process_id == 0: # TRIGGER / SET_AI_MODE / SET_RECORD_MODE
                            for callback in self._on_ack_handlers.values():
                                exec_callback(callback, data_transcode)
                        else:
                            for callback in self._on_flowsteps_ack_handlers.values():
                                exec_callback(callback, data_transcode)
                            
                            #special train callback
                            if evt_id == EventOperationID.EVT_INT_TRAIN_DONE.value: # process_id TRAINING
                                for callback in self._on_train_done_handlers.values():
                                    exec_callback(callback, data_transcode)
                    elif operation == EventOperationID.EVT_EXT_EXCEPTION:
                        for callback in self._on_exception_handlers.values():
                            exec_callback(callback, data_transcode)
                            
                    for callback in self._on_event_handlers.values():
                        exec_callback(callback, operation, data)

    def remove_observer(self, dict_obj_name, idx):
        if not hasattr(self, dict_obj_name):
            return
        dict_obj = getattr(self, dict_obj_name)
        if idx in dict_obj:
            del dict_obj[idx]

    def on_disconnect(self, callback: Callable[[Agent], None]) -> callable:
        cb_id = f"ondisconnect-{uuid.uuid4()}"
        self.on_disconnect_handlers[cb_id] = callback
        return lambda: self.remove_observer("on_disconnect_handlers", cb_id)

    def on_log(self, callback: Callable[[Agent, str], None]) -> callable:
        cb_id = f"onlog-{uuid.uuid4()}"
        self._on_log_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_log_handlers", cb_id)

    def on_event(self, callback: Callable[[Agent, EventOperationID, dict], None]) -> callable:
        cb_id = f"onevent-{uuid.uuid4()}"
        self._on_event_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_event_handlers", cb_id)

    def on_exception(self, callback: Callable[[Agent, dict], None]) -> callable:
        cb_id = f"onexception-{uuid.uuid4()}"
        self._on_exception_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_exception_handlers", cb_id)

    def on_training_done(self, callback: Callable[[Agent, dict], None]) -> callable:
        cb_id = f"ontraindone-{uuid.uuid4()}"
        self._on_train_done_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_train_done_handlers", cb_id)

    def on_flowsteps_ack(self, callback: Callable[[Agent, dict], None]) -> callable:
        cb_id = f"on-flowstep-ack-{uuid.uuid4()}"
        self._on_flowsteps_ack_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_flowsteps_ack_handlers", cb_id)

    def on_ack(self, callback: Callable[[Agent, dict], None]) -> callable:
        cb_id = f"onack-{uuid.uuid4()}"
        self._on_ack_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_ack_handlers", cb_id)

    def on_final_process_result(self, callback: Callable[[Agent, dict], None]) -> callable:
        cb_id = f"onfinaldone-{uuid.uuid4()}"
        self._on_final_process_result_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_final_process_result_handlers", cb_id)

    # flow step result
    def on_data_acq_result(self, callback: Callable[[Agent, dict], None]) -> callable:
        cb_id = f"ondataacqresult-{uuid.uuid4()}"
        self._on_data_acq_result_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_data_acq_result_handlers", cb_id)
    
    def on_data_transform_result(self, callback: Callable[[Agent, dict], None]) -> callable:
        cb_id = f"ondatatransformresult-{uuid.uuid4()}"
        self._on_data_transform_result_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_data_transform_result_handlers", cb_id)

    def on_enroll_result(self, callback: Callable[[Agent, dict], None]) -> callable:
        cb_id = f"onenrollresult-{uuid.uuid4()}"
        self._on_enroll_result_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_enroll_result_handlers", cb_id)

    def on_inference_result(self, callback: Callable[[Agent, dict], None]) -> callable:
        cb_id = f"oninferresult-{uuid.uuid4()}"
        self._on_infer_result_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_infer_result_handlers", cb_id)

    def on_dataset_preparation_result(self, callback: Callable[[Agent, dict], None]) -> callable:
        cb_id = f"ondatasetpreparationresult-{uuid.uuid4()}"
        self._on_dataset_preparation_result_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_dataset_preparation_result_handlers", cb_id)
    
    def on_training_result(self, callback: Callable[[Agent, dict], None]) -> callable:
        cb_id = f"ontrainingresult-{uuid.uuid4()}"
        self._on_training_result_handlers[cb_id] = callback
        return lambda: self.remove_observer("_on_training_result_handlers", cb_id)

    def send_message(self, message: Message, sync: bool = False, timeout_ms: int = 10000):
        self.gateway.send(Request(
            RequestActions.ACT_SEND_TO_DEVICE,
            self.device_name,
            message.to_dict()
        ))

        if sync:
            return self.wait_command_response(message, timeout_ms=timeout_ms)

        return None

    def subscribe(self):
        self.gateway.send(Request(
            RequestActions.ACT_SUB_TO_DEVICE,
            self.device_name
        ))

    def send_chunk(self, source_id: int, chunk: list[float]) -> None:
        msg = EventMessage(EventOperationID.EVT_EXT_DATA_IN) \
            .add_payload(source_id, "<f", chunk)
        self.send_message(msg)

    def send_data(self, source_id: int, data: list[float], chunk_size: int, chunk_rate: int) -> None:
        sent_data = 0
        start_idx = 0
        end_idx = chunk_size
        chunk_period = 1 / chunk_rate
        data_len = len(data)
        while sent_data < len(data):
            time_1 = Timer.get_elapsed_time()
            self.send_chunk(source_id, data[start_idx:end_idx])
            sent_data += chunk_size
            send_time = Timer.get_elapsed_time() - time_1
            start_idx += chunk_size
            end_idx += chunk_size
            if end_idx > data_len:
                end_idx = data_len
            Timer.wait(chunk_period - send_time)

    def set_ai_mode(self, mode: AgentAIMode, ground_truth: list = []) -> None:
        ai_type = AgentAIType.APP_AI_TYPE_CLASSIFICATION
        if len(ground_truth) > 0 and isinstance(ground_truth[0], float):
            ai_type = AgentAIType.APP_AI_TYPE_REGRESSION

        msg = EventMessage(EventOperationID.EVT_EXT_SET_MODE) \
            .add_payload(mode.value, ai_type.value, ground_truth)
        self.send_message(msg)

    def trigger(self, trigger_type: AgentTriggerType, source_id: int ) -> None:
        msg = EventMessage(EventOperationID.EVT_EXT_TRIGGER) \
            .add_payload(trigger_type.value, source_id)
        self.send_message(msg)

    def set_record_mode(self, record_mode: AgentRecordMode, source_id: int) -> None:
        msg = EventMessage(EventOperationID.EVT_EXT_SET_RECORD_MODE) \
            .add_payload(record_mode.value, source_id)
        self.send_message(msg)

    def train(self) -> None:
        msg = EventMessage(EventOperationID.EVT_EXT_LAUNCH_TRAIN) \
            .add_payload()
        self.send_message(msg)

    def kill(self) -> None:
        msg = EventMessage(EventOperationID.EVT_EXT_KILL) \
            .add_payload()
        self.send_message(msg)

    def correct(self, ground_truth: list, source_id: int, position: int = 0, remove: bool = False):
        ai_type = AgentAIType.APP_AI_TYPE_CLASSIFICATION
        if remove:
            ground_truth = []
        if len(ground_truth) > 0 and isinstance(ground_truth[0], float):
            ai_type = AgentAIType.APP_AI_TYPE_REGRESSION
        msg = EventMessage(EventOperationID.EVT_EXT_CORRECTION) \
            .add_payload(position, source_id, ai_type.value, ground_truth)
        self.send_message(msg)

    def wait_command_response(self, msg: Message, timeout_ms: int = 10000):
        msg_id = msg.header.id
        self._wait_response[msg_id] = None

        timeout = timeout_ms / 1000.0
        sleeptime = 0.001
        start_time = Timer.get_elapsed_time()
        while msg_id in self._wait_response and self._wait_response[msg_id] is None:
            elapsed_time = Timer.get_elapsed_time() - start_time
            if elapsed_time > timeout:
                raise Exception("Command message Timeout")
            Timer.wait(sleeptime)

        return_value = self._wait_response[msg_id]
        del self._wait_response[msg_id]
        return return_value

    # OTA 
    def get_kpi(self, timeout_ms: int = 10000):
        msg = CommandMessage(CommandOperationID.CMD_GET, MessageModule.LOG)
        msg.add_payload(LogCommandParameter.LOG_NB_KPIS.value)
        data: dict = self.send_message(msg, sync=True, timeout_ms=timeout_ms)

        if "number" not in data:
            raise Exception("Missing number in data")

        nbkpis = data.get("number")
        kpi_list = []
        for i in range(nbkpis):
            msg = CommandMessage(CommandOperationID.CMD_START, MessageModule.LOG)
            msg.add_payload(LogCommand.LOG_GET_KPI.value, i)
            kpi = self.send_message(msg, sync=True, timeout_ms=timeout_ms)
            kpi_list.append({
                "id": kpi.get("kpid", 0),
                "vmid": kpi.get("vmid", 0),
                "modelid": kpi.get("modelid", 0),
                "description": kpi["description"],
                "value": kpi["value"],
                "type": kpi["typ"]
            })

        return kpi_list

    def export_dataset(self) -> list:
        datasets = []
        for data in self.export_table_data(DBMTable.DBM_DAT):
            if data != {}:
                # default configuration
                is_little = True
                pack_unit_format = "f"
                data_len = 4 # bytes for float 32bits
                if "datatype" in data:
                    datatype = data.get("datatype")
                    is_little = datatype[0] == "<"
                    pack_unit_format = datatype[1]
                val = data.get("record")
                if val is not None:
                    data["record"] = unpack_buffer_to_list(
                        b642b(val),
                        is_little,
                        data_len,
                        pack_unit_format
                    )
                datasets.append(data)
        return datasets

    def export_vm_list(self) -> list:
        return self.export_table_data(DBMTable.DBM_VM)

    def export_tables(self, timeout_ms: int = 10000) -> list:
        msg = CommandMessage(CommandOperationID.CMD_GET, MessageModule.DBM)
        msg.add_payload(DBMCommandParameter.DBM_PARAM_INFO.value)
        data = self.send_message(msg, sync=True, timeout_ms=timeout_ms)

        return data.get("tables", [])

    def export_table_data(self, data_type: DBMTable, timeout_ms: int = 10000) -> list:
        tables = self.export_tables()
        results = []

        for table in tables:
            if table.get("typ") != data_type.value:
                continue
            for i in range(table.get("count", 0)):
                msg = CommandMessage(CommandOperationID.CMD_START, MessageModule.DBM)
                msg.add_payload(DBMCommand.DBM_EXPORT_ROW.value, table.get("handle"), "", i)
                data = self.send_message(msg, sync=True, timeout_ms=timeout_ms)
                attr = data.get("attributes")
                if attr is not None:
                    results.append(attr)

        return results
    
    def get_asl_meta(self, timeout_ms: int = 10000) -> dict:
        msg = CommandMessage(CommandOperationID.CMD_GET, MessageModule.RUN)
        msg.add_payload(RUNCommandParameter.RUN_PARAM_APPS.value)
        data = self.send_message(msg, sync=True, timeout_ms=timeout_ms)
        return data

    def get_life_cycle(self, timeout_ms: int = 10000) -> dict:
        data = None
        msg = CommandMessage(CommandOperationID.CMD_GET, MessageModule.MAL)
        msg.add_payload(MALCommandParameter.MAL_PARAM_LIFE_CYCLE.value)

        data = self.send_message(msg, sync=True, timeout_ms=timeout_ms)

        return data        