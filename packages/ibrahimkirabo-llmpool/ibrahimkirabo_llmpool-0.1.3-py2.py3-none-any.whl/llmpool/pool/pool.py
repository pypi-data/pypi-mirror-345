import time
import logging
import threading

from pyrate_limiter import Rate, Duration, BucketFullException, Limiter
from .ratelimiter import NoRateLimiter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class LLMPool:
    def __init__(self, api_keys: list[str], model_limits: dict[str, dict], cooldown: int = 60):
        """
        :param api_keys: List of API keys to use.
        :param model_limits: A dictionary mapping model identifier to its allowed usage.
                             Example:
                             {
                                "gemma": { "requests_min": 100, "tokens_min": 10000,
                                           "requests_day": 1000, "tokens_day": 100000 },
                                "llama": { "requests_min": 200, "tokens_min": 20000,
                                           "requests_day": 2000, "tokens_day": None },
                             }
                             In the above, a tokens_day value of None means no daily token limit.
        :param cooldown: Cooldown period in seconds when a model hits its limit.
        """
        self.lock = threading.Lock()
        self.cooldown = cooldown
        self.api_keys = api_keys

        # Extract limits from model_limits.
        self.req_min_limits = {model: limits["requests_min"] for model, limits in model_limits.items()}
        self.token_min_limits = {model: limits["tokens_min"] for model, limits in model_limits.items()}
        self.req_day_limits = {model: limits["requests_day"] for model, limits in model_limits.items()}
        
        # For tokens_day, use float('inf') if no limit is provided.
        self.token_day_limits = {
            model: limits["tokens_day"] if limits.get("tokens_day") is not None else float("inf")
            for model, limits in model_limits.items()
        }
        self.models = list(model_limits.keys())
        now = time.time()

        # Internal usage tracking per API key and per model.
        self.keys = {
            key: {
                model: {
                    "used_requests_min": 0,
                    "used_tokens_min": 0,
                    "used_requests_day": 0,
                    "used_tokens_day": 0,
                    "reset_at_min": now,
                    "reset_at_day": now + 86400
                }
                for model in self.models
            }
            for key in api_keys
        }

        # Helper function to return a limiter or a NoRateLimiter for unlimited limits.
        def create_limiter(limit_value, duration):
            # If there's no limit or it is set to infinite, use NoRateLimiter.
            if limit_value is None or limit_value == float("inf"):
                return NoRateLimiter()
            return Limiter([Rate(limit_value, duration)])

        # Create limiters for minute-level limits.
        self.min_limiters = {
            key: {
                model: {
                    "requests": create_limiter(self.req_min_limits[model], Duration.MINUTE),
                    "tokens": create_limiter(self.token_min_limits[model], Duration.MINUTE),
                }
                for model in self.models
            }
            for key in api_keys
        }

        # Create limiters for daily limits.
        self.day_limiters = {
            key: {
                model: {
                    "requests": create_limiter(self.req_day_limits[model], Duration.DAY),
                    "tokens": create_limiter(self.token_day_limits[model], Duration.DAY),
                }
                for model in self.models
            }
            for key in api_keys
        }

    def _reset_if_needed(self, key: str, model: str):
        """Reset usage counters if the reset time has passed for minute or day."""
        now = time.time()
        usage = self.keys[key][model]
        if now >= usage["reset_at_min"]:
            usage["used_requests_min"] = 0
            usage["used_tokens_min"] = 0
            usage["reset_at_min"] = now + 60
        if now >= usage["reset_at_day"]:
            usage["used_requests_day"] = 0
            usage["used_tokens_day"] = 0
            usage["reset_at_day"] = now + 86400

    def _get_available_models(self):
        """
        Iterate over API keys and models, pre-checking all four limiters.
        Models whose token/day limit is infinite are never blocked on day tokens.
        Return a list of (api_key, model) pairs that are available.
        """
        available = []
        for api_key in self.api_keys:
            for model in self.models:
                self._reset_if_needed(api_key, model)
                usage = self.keys[api_key][model]
                # Check minute limits and daily request limits always.
                if (usage["used_requests_min"] >= self.req_min_limits[model] or
                    usage["used_tokens_min"] >= self.token_min_limits[model] or
                    usage["used_requests_day"] >= self.req_day_limits[model]):
                    continue
                # For daily tokens, if the limit is not infinite, then check usage.
                if self.token_day_limits[model] != float("inf") and usage["used_tokens_day"] >= self.token_day_limits[model]:
                    continue
                try:
                    # Pre-check: attempt to acquire 1 unit from all four limiters.
                    self.min_limiters[api_key][model]["requests"].try_acquire(api_key, weight=1)
                    self.min_limiters[api_key][model]["tokens"].try_acquire(api_key, weight=1)
                    self.day_limiters[api_key][model]["requests"].try_acquire(api_key, weight=1)
                    self.day_limiters[api_key][model]["tokens"].try_acquire(api_key, weight=1)
                    available.append((api_key, model))
                except BucketFullException:
                    continue
        return available

    def _execute_call(self, api_key, model, call_func, *args, **kwargs):
        """
        Execute the LLM call for the given API key and model.
        Updates internal usage counters and charges additional token cost.
        Returns the call result.
        """
        # Update request counters.
        self.keys[api_key][model]["used_requests_min"] += 1
        self.keys[api_key][model]["used_requests_day"] += 1

        result, tokens_used = call_func(
            api_key=api_key,
            model=model,
            *args,
            **kwargs,
        )
        additional_cost = tokens_used - 1 if tokens_used > 1 else 0

        # Charge additional tokens.
        self.min_limiters[api_key][model]["tokens"].try_acquire(api_key, weight=additional_cost)
        self.day_limiters[api_key][model]["tokens"].try_acquire(api_key, weight=additional_cost)

        self.keys[api_key][model]["used_tokens_min"] += tokens_used
        # Only update daily token usage if there is a limit.
        if self.token_day_limits[model] != float("inf"):
            self.keys[api_key][model]["used_tokens_day"] += tokens_used

        api_index = self.api_keys.index(api_key)
        logger.info(f"API key index '{api_index}' with model '{model}' consumed {tokens_used} tokens.")
        return result

    def _set_cooldown(self, api_key, model):
        """
        Mark a specific API key and model as having reached its limit by setting the cooldown.
        For models with no daily token limit, the daily token counter is left unchanged.
        """
        now = time.time()
        self.keys[api_key][model]["reset_at_min"] = now + self.cooldown
        self.keys[api_key][model]["reset_at_day"] = now + self.cooldown
        self.keys[api_key][model]["used_requests_min"] = self.req_min_limits[model]
        self.keys[api_key][model]["used_tokens_min"] = self.token_min_limits[model]
        self.keys[api_key][model]["used_requests_day"] = self.req_day_limits[model]
        if self.token_day_limits[model] != float("inf"):
            self.keys[api_key][model]["used_tokens_day"] = self.token_day_limits[model]
        else:
            # For models with unlimited daily tokens, reset tokens_day to 0.
            self.keys[api_key][model]["used_tokens_day"] = 0

    def call_llm(self, call_func, *args, timeout: float = 30, **kwargs):
        """
        Wraps an LLM call by ensuring that both per-minute and per-day limiters have capacity.
        Pre-checks 1 unit on each limiter before executing the call.
        After the call, any additional token cost is charged.
        
        :param call_func: Function implementing the LLM call. Expected to return (result, tokens_used).
        :param timeout: Maximum time in seconds to wait for an available API key/model.
        :return: The result from call_func.
        :raises TimeoutError: If no API key/model is found within the timeout period.
        """
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Timed out waiting for an available API key/model combination.")

            with self.lock:
                available = self._get_available_models()
                if available:
                    for api_key, model in available:
                        try:
                            result = self._execute_call(api_key, model, call_func, *args, **kwargs)
                            api_index = self.api_keys.index(api_key)
                            logger.info(f"Serviced request with model '{model}' using API key index '{api_index}'")
                            return result
                        except BucketFullException:
                            api_index = self.api_keys.index(api_key)
                            logger.info(f"Rate limit exceeded for API key index '{api_index}' and model '{model}'. Setting cooldown.")
                            self._set_cooldown(api_key, model)
                            continue
            time.sleep(1)