import time

TIME_MULT_MS = 1000  # all measures in milliseconds


class Timer:
    time_started: int = 0

    @classmethod
    def init(cls) -> None:
        cls.time_started = int(time.time() * TIME_MULT_MS)

    @classmethod
    def get_elapsed_time(cls) -> float:  # Get elapse time in seconds
        now_time_ms = (time.time() * TIME_MULT_MS)
        elapsed_time = (now_time_ms - cls.time_started) / 1000
        return elapsed_time

    @classmethod
    def get_timestamp(cls) -> int:  # Get timestamps in milliseconds
        now_time_ms = int(time.time() * TIME_MULT_MS)
        return now_time_ms - cls.time_started

    @classmethod
    def wait(cls, sec_to_wait: float) -> None:
        if sec_to_wait < 0.001:
            sec_to_wait = 0.001
        time.sleep(sec_to_wait)
