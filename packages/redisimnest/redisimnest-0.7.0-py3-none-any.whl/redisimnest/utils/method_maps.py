import functools
from ..settings import SHOW_METHOD_DISPATCH_LOGS


def with_logging(method):
    """
    Decorator to log Redis method dispatches and their results
    when SHOW_METHOD_DISPATCH_LOGS is enabled.

    Requires the decorated method to be a method of an object with:
        - self.key: the full Redis key path
        - self.is_secret / self.is_password: booleans for key sensitivity
    """
    method_name = method.__name__

    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        if SHOW_METHOD_DISPATCH_LOGS:
            key_status = (
                'secret' if getattr(self, 'is_secret', False)
                else 'password' if getattr(self, 'is_password', False)
                else 'plainkey'
            )
            key = getattr(self, 'key', 'UNKNOWN_KEY')
            print(
                f"[redisimnest] {method_name.upper():<8} → [{key_status}]: {key} | args={args} kwargs={kwargs}"
            )

        result = await method(self, *args, **kwargs)

        if SHOW_METHOD_DISPATCH_LOGS:
            print(
                f"[redisimnest] {method_name.upper():<8} ← Result: {repr(result)}"
            )

        return result

    return wrapper
