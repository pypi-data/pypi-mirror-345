from datetime import datetime
import functools
from ..settings import SHOW_METHOD_DISPATCH_LOGS
from termcolor import colored

# Primary identity
def CLR_PACKAGE_NAME(text): return colored(text, 'cyan')

# Method categories
def CLR_METHOD_GET(text): return colored(text, 'green', attrs=['bold'])
def CLR_METHOD_SET(text): return colored(text, 'blue', attrs=['bold'])
def CLR_METHOD_DELETE(text): return colored(text, 'red', attrs=['bold'])
def CLR_METHOD_CLEAR(text): return colored(text, 'red', attrs=['bold'])
def CLR_KEY_NAME(text): return colored(text, 'light_cyan', 'on_black')

# Key type identity
def CLR_METHOD_OHTER(text): return colored(text, 'white', attrs=['bold'])
def CLR_KEY_TYPE_PLAINKEY(text): return colored(text, 'grey')
def CLR_KEY_TYPE_PASSWORD(text): return colored(text, 'magenta', attrs=['bold'])
def CLR_KEY_TYPE_SECRET(text): return colored(text, 'yellow', attrs=['bold'])

# Supporting info
def CLR_ARGS_KWARGS(text): return colored(text, 'dark_grey')
def CLR_RESULT_TEXT(text): return colored(text, 'green')
def CLR_RESULT_VALUE(text): return colored(text, 'grey', attrs=[])


def CLR_TIMESTAMP(text): return colored(text, 'grey')
def get_now():
    now = datetime.now()
    formatted = now.strftime("[%Y-%m-%d %H:%M:%S.") + f"{now.microsecond // 1000:03d}]"
    return CLR_TIMESTAMP(formatted)


def with_logging(method):
    """
    Decorator to log Redis method dispatches and their results
    when SHOW_METHOD_DISPATCH_LOGS is enabled.

    Requires the decorated method to be a method of an object with:
        - self.key: the full Redis key path
        - self.is_secret / self.is_password: booleans for key sensitivity
    """
    method_name = method.__name__.upper()

    def method_color_fn(name):
        return {
            "GET": CLR_METHOD_GET,
            "SET": CLR_METHOD_SET,
            "DELETE": CLR_METHOD_DELETE,
            "CLEAR": CLR_METHOD_CLEAR,
        }.get(name, CLR_METHOD_OHTER)

    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        if SHOW_METHOD_DISPATCH_LOGS:
            # Determine key type
            key_status = (
                'secret' if getattr(self, 'is_secret', False)
                else 'password' if getattr(self, 'is_password', False)
                else 'plainkey'
            )
            key = getattr(self, 'key', 'UNKNOWN_KEY')

            # Apply colors
            colored_prefix = CLR_PACKAGE_NAME("[redisimnest]")
            color_fn = method_color_fn(method_name)
            colored_method = color_fn(f"{method_name:<6}")
            colored_arrow = color_fn("→")
            colored_key_status = {
                'secret': CLR_KEY_TYPE_SECRET,
                'password': CLR_KEY_TYPE_PASSWORD,
                'plainkey': CLR_KEY_TYPE_PLAINKEY,
            }[key_status](f"[{key_status}]")
            colored_key = colored(key, 'white')  # literal key always bright
            colored_args = CLR_ARGS_KWARGS(f"args={args} kwargs={kwargs}")

            key_name = CLR_KEY_NAME(self._name)
            print(f"{colored_prefix} {get_now()} {colored_method} {colored_arrow} {colored_key_status} {key_name}: {colored_key} | {colored_args}")

        result = await method(self, *args, **kwargs)

        if SHOW_METHOD_DISPATCH_LOGS:
            colored_prefix = CLR_PACKAGE_NAME("[redisimnest]")
            color_fn = method_color_fn(method_name)
            colored_arrow = color_fn("←")
            colored_method = color_fn(f"{method_name:<8}")
            result_value = CLR_RESULT_VALUE(repr(result))

            print(f"{colored_prefix:>6} {get_now()}        {colored_arrow} {result_value}")

        return result

    return wrapper



def format_clear_log_line(
    cluster_name: str,
    chunk_num: int,
    chunks_count: int,
    deleted: int,
    deletes_count: int,
    keys: list
) -> str:
    """
    Returns a fully colorized CLEAR log line for cluster-wide deletions,
    with chunk and deletion counts tracked as x/y.
    """
    prefix         = CLR_PACKAGE_NAME("[redisimnest]")
    method         = CLR_METHOD_CLEAR("CLEAR")
    arrow          = CLR_METHOD_CLEAR("→")
    chunk_label    = CLR_ARGS_KWARGS("chunk:")
    deleted_label  = CLR_ARGS_KWARGS("deleted:")
    keys_label     = CLR_ARGS_KWARGS("keys:")

    cluster_type   = CLR_METHOD_DELETE("[cluster]")
    chunk_val      = CLR_RESULT_TEXT(f"{chunk_num}/{chunks_count}")
    deleted_val    = CLR_RESULT_TEXT(f"{deleted}/{deletes_count}")
    keys_val       = repr(keys)

    cluster_name = CLR_KEY_NAME(cluster_name)

    return f"{prefix} {get_now()} {method}  {arrow} {cluster_type}  {cluster_name} | {chunk_label} {chunk_val} | {deleted_label} {deleted_val} | {keys_label} {keys_val}"
