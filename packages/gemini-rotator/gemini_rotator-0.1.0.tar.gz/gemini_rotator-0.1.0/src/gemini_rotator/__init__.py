from itertools import cycle
from typing import List, Optional
try:
    import google.auth.api_key as api_key_module
    from google.auth.api_key import Credentials as OriginalCredentials
except ImportError:
    raise ImportError(
        "Couldn't import google.auth.api_key. Use pip install -U google-auth to install the library."
    )
# Keep originals so we can restore if needed
_original_init = OriginalCredentials.__init__
_original_apply = OriginalCredentials.apply


def patch(api_keys: List[str], api_main: Optional[str] = None) -> None:
    """Monkey-patch google.auth.api_key.Credentials to add rotating keys.

    Args:
        api_keys: A non-empty list of API key strings to rotate through.
        api_main:  If provided, only rotate when the .token equals this key.
                   If None, always rotate on every apply(). HIGHLY RECOMMENDED TO NOT BREAK OTHER GOOGLE LIBRARIES.
    Raises:
        ValueError: if api_keys is empty.
    """
    if not api_keys:
        raise ValueError("api_keys must be a non-empty list")

    def extended_init(self, token: str):
        # run original __init__ (validation + token set)
        _original_init(self, token)
        # install our rotation state
        self.api_keys = api_keys
        self.api_main = api_main
        self.apis = cycle(api_keys)

    def patched_apply(self, headers: dict, token: Optional[str] = None):
        # decide whether to rotate
        if api_main is None or self.token == api_main:
            try:
                chosen = next(self.apis)
            except StopIteration:
                # shouldn't happen—cycle never StopIteration, but incase cycle somehow dynamically modified
                raise ValueError("API key list is empty")
        else:
            chosen = token or self.token

        headers["x-goog-api-key"] = chosen

    # install patches
    api_key_module.Credentials.__init__ = extended_init
    api_key_module.Credentials.apply = patched_apply


def restore() -> None:
    """Restore original like nothing ever happened."""
    api_key_module.Credentials.__init__ = _original_init
    api_key_module.Credentials.apply = _original_apply

__all__ = [
    "patch",
    "restore",
]