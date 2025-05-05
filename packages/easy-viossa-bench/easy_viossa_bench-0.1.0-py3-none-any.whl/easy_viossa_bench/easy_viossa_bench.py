import requests
import functools
import warnings
import time
import threading
from typing import Callable, Union, Literal, Optional, Dict

_session = requests.Session()
_session_lock = threading.Lock()
_server_url = "https://viossabench.barnii77.dev"
MAX_EVAL_SIZE = 16384


class ApiError(Exception):
    pass


class ApiResponseFormatError(ApiError):
    pass


class ApiResponseContentError(ApiError):
    pass


class InvalidEvalIdError(ApiError):
    pass


class ApiKeyError(ApiError):
    pass


class PermissionRequiredError(ApiError):
    pass


class RateLimitExceededError(ApiError):
    pass


class NotAllowedToSaveEvalResultError(PermissionRequiredError):
    def __init__(self, msg: str, score: float, n_samples: int):
        super().__init__(msg)
        self.score = score
        self.n_samples = n_samples


class EvalResult:
    def __init__(self, score: float, eval_id: str, seed: int, n_samples: int):
        self.score = score
        self.eval_id = eval_id
        self.seed = seed
        self.n_samples = n_samples

    def __str__(self):
        return f"EvalResult(score={self.score}, eval_id={self.eval_id})"


def _raise_exception_for_response(resp: requests.Response):
    try:
        json_body = resp.json()
    except requests.exceptions.JSONDecodeError:
        raise ApiResponseFormatError(f"Invalid API response format (expected valid json). Response: {resp.text}")
    if resp.status_code == 200:
        return

    error = json_body.get("error")
    if not isinstance(error, str):
        raise ApiResponseContentError(
            "Expected API json response to contain 'error' field of type 'str', but it did not."
        )

    elif resp.status_code == 429:
        raise RateLimitExceededError(error)
    elif resp.status_code == 403:
        if "'save: true'" in error:
            score, n_samples = json_body.get("score"), json_body.get("n_samples")
            if not isinstance(score, (int, float)) or not isinstance(n_samples, int):
                raise ApiResponseFormatError(
                    "Expected a 'save: true' unpermitted error to contain the eval result anyway, but it did not (at least not in a valid format)"
                )
            score = float(score)
            raise NotAllowedToSaveEvalResultError(error, score, n_samples)
        raise PermissionRequiredError(error)
    else:
        # detect exception based on message
        if "eval id" in error.lower():
            raise InvalidEvalIdError(error)
        elif "submitted title contains your api key" in error.lower():
            # warn the user of their mistake so they can't ignore the error with try: ... except ApiError: pass
            warnings.warn(error)
            raise ApiError(error)
        else:
            raise ApiError(error)


def _get_headers(api_key: str) -> dict:
    if api_key is None:
        return {}
    assert isinstance(api_key, str)
    return {"Authorization": f"Bearer {api_key}"}


def evaluate_model(
    model_request: Callable[[str, str], None],
    model_collect: Callable[[str], str],
    n_samples: Union[int, Literal["tiny-eval", "small-eval", "medium-eval", "large-eval", "huge-eval"]],
    api_key: Optional[str] = None,
    seed: Union[int, Literal["random"]] = 0,
    save_result_in_api: bool = False,
) -> EvalResult:
    """
    Evaluate your model on ViossaBench easily.

    Arguments:
        model_request: `Callable[sample_id: str, prompt: str] -> None`.
            A callback which gives the model eval function a prompt and tells it to schedule the generation
            of a response. This allows the user to batch all their generations because first, model_request will be
            called for every input, then, it will loop and collect all responses using model_collect.
        model_collect: `Callable[sample_id: str] -> response: str`.
            A callback to return the string response given the string request ID returned given to model_request.
        n_samples: Describes how big the eval should be in terms of sample count.
        api_key: Optional API key (providing this increases your rate limits and, if you provide a verified API key,
            allows you to push one eval result per api key to the leaderboard).
        save_result_in_api: Only allowed if you have a 'verified' api key. If set to true, saves the result on the
            ViossaBench server and allows you to later push it to the leaderboard.
        seed: What seed to use for selecting samples. Defaults to 0.

    Returns:
        the score (pass rate) as a number between 0.0 and 1.0
    """
    if not callable(model_request):
        raise ValueError(f"Expected 'model_request' to be callable, but it is not. Got type {type(model_request)}.")
    if not callable(model_collect):
        raise ValueError(f"Expected 'model_collect' to be callable, but it is not. Got type {type(model_collect)}.")
    if isinstance(n_samples, str):
        if n_samples not in ("tiny-eval", "small-eval", "medium-eval", "large-eval", "huge-eval"):
            raise ValueError(
                f'Parameter \'eval_size\' must be one of ("tiny-eval", "small-eval", "medium-eval", "large-eval", "huge-eval")'
            )
    elif isinstance(n_samples, int):
        if n_samples <= 0:
            raise ValueError("Parameter 'eval_size' must be >= 0")
        elif n_samples > MAX_EVAL_SIZE:
            raise ValueError(f"Parameter 'eval_size' must be <= {MAX_EVAL_SIZE}")
    else:
        raise TypeError(
            f"Type mismatch: expected 'eval_size' to be type 'str' or 'int', got {type(n_samples)} instead."
        )
    if not isinstance(api_key, str) and api_key is not None:
        raise TypeError(
            f"Type mismatch: expected 'api_key' to be of type 'str' or be None, got {type(api_key)} instead."
        )
    if not isinstance(save_result_in_api, bool):
        raise TypeError(
            f"Type mismatch: expected 'save_result_in_api' to be of type 'bool', got {type(save_result_in_api)} instead."
        )
    if isinstance(seed, str):
        if seed != "random":
            raise ValueError(f"Expected 'seed' to be either any 'int' or the string literal 'random', got {seed}.")
    elif not isinstance(seed, int):
        raise TypeError(f"Type mismatch: expected 'seed' to be of type 'int' or 'str', got {type(seed)}.")

    headers = _get_headers(api_key)

    with _session_lock:
        resp_samples = _session.get(f"{_server_url}/api/samples/{n_samples}/{seed}", headers=headers, timeout=30)
        _raise_exception_for_response(resp_samples)
        json_resp = resp_samples.json()
        eval_id, samples = json_resp.get("id"), json_resp.get("samples")
        if (
            not isinstance(eval_id, str)
            or not isinstance(samples, dict)
            or not all(isinstance(v, str) for v in samples.values())
        ):
            raise ApiError("Received invalid response from API at /api/samples route.")

        for sample_id, prompt in samples.items():
            model_request(sample_id, prompt)
        translations = {}
        for sample_id in samples.keys():
            translations[sample_id] = model_collect(sample_id)

        resp_evaluate = _session.post(
            f"{_server_url}/api/evaluate",
            headers=headers,
            json={"id": eval_id, "translations": translations, "save": save_result_in_api},
            timeout=30,
        )
        _raise_exception_for_response(resp_evaluate)
        json_resp = resp_evaluate.json()
        score = json_resp.get("score")
        seed = json_resp.get("seed")
        n_samples_resp = json_resp["n_samples"]
        if eval_id != json_resp.get("id"):
            raise ApiError(
                "Received invalid response from API at /api/evaluate route (response eval_id does not match sent one... unreachable?)."
            )
        elif not isinstance(n_samples_resp, int) or isinstance(n_samples, int) and n_samples != n_samples_resp:
            raise ApiError(
                "Received invalid response from API at /api/evaluate route (n_samples is invalid or incorrect)."
            )
        elif not isinstance(score, (int, float)):
            raise ApiError("Received invalid response from API at /api/evaluate route (score is not a number).")
        elif not isinstance(seed, int):
            raise ApiError("Received invalid response from API at /api/evaluate route (seed is not an int).")

    return EvalResult(score, eval_id, seed, n_samples_resp)


def push_to_leaderboard(eval_id: str, title: str, api_key: str):
    """
    Given your eval ID returned from `evaluate_model`, push the eval result to the leaderboard. Requires a 'verified'
    API key. You can only have one eval result per API key on the leaderboard (which would usually be your top result).
    This means if you already have a result on the leaderboard, this push operation will replace the current one. You
    can revert this by pushing the old one again, which requires you to have the old result's eval ID, so it is
    recommended you store all of your eval IDs. Alternatively, you can also list all stored eval results associated with
    your API key using `list_stored_eval_results(api_key)`.

    Arguments:
        eval_id: the ID of the eval to push to the leaderboard
        title: the title under which it should be shown on the leaderboard
        api_key: must be a 'verified' api key for this operation
    """
    if not isinstance(eval_id, str):
        raise TypeError(f"Expected 'eval_id' to be of type 'str', but got {type(eval_id)}.")
    elif not isinstance(title, str):
        raise TypeError(f"Expected 'title' to be of type 'str', but got {type(title)}.")
    elif not isinstance(api_key, str):
        raise TypeError(f"Expected 'api_key' to be of type 'str', but got {type(api_key)}.")

    with _session_lock:
        resp = _session.post(
            f"{_server_url}/api/push-to-leaderboard",
            headers=_get_headers(api_key),
            json={"id": eval_id, "title": title},
        )
        _raise_exception_for_response(resp)


def list_stored_eval_results(api_key: str) -> Dict[str, Dict[str, Union[int, float, str]]]:
    if not isinstance(api_key, str):
        raise TypeError(f"Expected 'api_key' to be of type 'str', got {type(api_key)}.")

    with _session_lock:
        resp = _session.post(f"{_server_url}/api/list-stored-eval-results", headers=_get_headers(api_key))
        _raise_exception_for_response(resp)

    stored_eval_results = resp.json()
    if not isinstance(stored_eval_results, dict) or not all(isinstance(v, dict) for v in stored_eval_results.values()):
        raise ApiResponseContentError("Expected response to a dict mapping eval IDs to json objects, but it is not.")

    EXPECTED_FORMAT_AND_TYPES = {"api_key": str, "id": str, "score": (int, float), "seed": int, "n_samples": int, "timestamp": (int, float)}
    for eval_obj in stored_eval_results.values():
        if not eval_obj.keys() == EXPECTED_FORMAT_AND_TYPES.keys():
            print(eval_obj)
            raise ApiResponseContentError(
                f"Response object {eval_obj} contains illegal keys. Expected {EXPECTED_FORMAT_AND_TYPES}."
            )
        if not all(isinstance(v, EXPECTED_FORMAT_AND_TYPES[k]) for k, v in eval_obj.items()):
            raise ApiResponseContentError(
                f"Response object {eval_obj} has fields whose types do not match the expected schema {EXPECTED_FORMAT_AND_TYPES}."
            )

    return stored_eval_results


def retry_on_rate_limit_exc(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        last_err = None
        while time.time() - start_time < 150:
            try:
                return func(*args, **kwargs)
            except RateLimitExceededError as e:
                last_err = e
        raise last_err if last_err is not None else RateLimitExceededError

    return functools.update_wrapper(wrapper, func)


def set_server_url(server_url: str):
    global _server_url
    if not isinstance(server_url, str):
        raise TypeError(f"Expected 'server_url' to be of type 'str', got {type(server_url)}")
    _server_url = server_url.strip("/")
