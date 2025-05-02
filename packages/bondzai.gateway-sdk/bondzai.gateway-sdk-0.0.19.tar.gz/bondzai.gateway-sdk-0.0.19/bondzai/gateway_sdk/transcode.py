from .enums import EventOperationID, AgentAIType


def transcode(op: EventOperationID, data: dict):
    transcode_data = data

    if op == EventOperationID.EVT_EXT_ASL_RESULT:
        transcode_data = {k: data[k] for k in data if k not in ["result","label_type"] }
        if data["label_type"] != 0:  # Classification
            transcode_data["label_type"] = data["label_type"]
            transcode_data["label"] = data["result"][0]
        else:
            transcode_data["regression"] = data["result"]

    elif op == EventOperationID.EVT_EXT_VM_RESULT:
        transcode_data = {k: data[k] for k in data if k != "result" }
        if data["ai_type"] == AgentAIType.APP_AI_TYPE_CLASSIFICATION.value:
            results = data["result"]
            res_nb = int(len(results) / 2)
            confidences = {}
            for k in range(res_nb):
                confidences[results[2 * k + 1]] = results[2 * k]
            transcode_data["confidences"] = confidences

        else:
            transcode_data ["regression"] = data["result"]
            
    return transcode_data
