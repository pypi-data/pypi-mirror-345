from dataclasses import dataclass


DEFAULT_SESSION = b"deepserfirstsession"
DEFAULT_DAVINSY_ENDIANNESS = "little"


@dataclass
class Configuration:
    app_id: int = 0
    session: bytes = DEFAULT_SESSION
    endianness: str = DEFAULT_DAVINSY_ENDIANNESS
