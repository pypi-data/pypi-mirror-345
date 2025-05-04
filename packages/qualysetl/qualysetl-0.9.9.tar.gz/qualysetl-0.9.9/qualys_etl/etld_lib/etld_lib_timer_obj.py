import timeit
from dataclasses import dataclass


@dataclass
class TimerObj:
    def __init__(self, max_time=300):
        self.start_time = timeit.default_timer()
        self.current_time = self.start_time
        self.max_time = max_time
        self.time_elapsed = 0

    def reset_timer(self):
        self.start_time = timeit.default_timer()
        self.current_time = self.start_time
        self.time_elapsed = 0

    def get_time_elapsed(self) -> float:
        current_time = timeit.default_timer()
        time_elapsed = (current_time - self.start_time)
        return time_elapsed

    def if_time_elapsed_past_max_time(self, max_time=300) -> bool:
        self.time_elapsed = self.get_time_elapsed()
        time_elapsed_flag = False
        if self.time_elapsed > max_time:
            time_elapsed_flag = True
        return time_elapsed_flag
