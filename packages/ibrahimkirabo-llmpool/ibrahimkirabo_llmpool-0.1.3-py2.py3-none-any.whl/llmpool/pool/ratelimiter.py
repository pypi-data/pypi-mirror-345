from typing import Union

from pyrate_limiter import Limiter, Rate, Duration

ONE_MILLION = 1000000

class NoRateLimiter(Limiter):
    def __init__(self):
        # The argument doesn't have any effect in this rate limiter. It is only there to satisfy
        # the contract the base class - Limiter
        super().__init__(argument = [Rate(ONE_MILLION, Duration.MINUTE), Rate(ONE_MILLION, Duration.DAY)])
    
    def try_acquire(self, name, weight = 1):
        pass
