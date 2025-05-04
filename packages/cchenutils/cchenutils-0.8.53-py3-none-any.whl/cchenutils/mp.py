import random
import time
import traceback
from multiprocessing import Pool, TimeoutError

from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout, Timeout, JSONDecodeError, ChunkedEncodingError
from tqdm import tqdm

from .files import write, txt_write


def writer(queue):
    """
    Listens to `queue` for file writing tasks. Expects a tuple:

    - For CSV:
        (fp, data, headers, [optional scrape_time])
    - For JSON/JSONL:
        (fp, data)

    Use 'STOP' to end the loop.
    """
    while True:
        args = queue.get()
        if args == 'STOP':
            break
        if len(args) < 2:
            print(f'[writer] Invalid input: {args}')
            continue
        for _ in range(10):
            try:
                write(*args)
                break
            except PermissionError:
                time.sleep(1)


def scraper(func, *func_args,
            proxy_list=None, proxyerr=None, stderr=None, retries=3, debug=False,
            **kwargs):
    """
    A wrapper to call a function with optional proxy rotation, retry logic, and error logging.

    Args:
        func (callable): The function to be called (e.g., your scraper function).
        *func_args: Positional arguments to pass to `func`.
        proxy_list (multiprocessing.Manager().dict, optional): Shared dict of proxies and their quality.
            - Keys are proxy strings.
            - Values are booleans indicating whether the proxy works.
        proxyerr (str, optional): File path to log dead proxies.
        stderr (str, optional): File path to log errors (proxy + args + traceback).
        retries (int, optional): Number of retries. Defaults to 3 (via kwargs).
        debug (bool, optional): If True, will print and pause on errors for 300 seconds.
        **kwargs: Keyword arguments to pass to `func`.

    Returns:
        Any: The return value of `func` if successful. Otherwise, `None`.
    """
    if proxy_list is None:
        retries = min(1, retries)
    for _ in range(retries):
        proxy = random.choice([ip for ip, qual in proxy_list.items() if qual]) if proxy_list else None
        try:
            return func(*func_args, **kwargs, proxy=proxy)
        except (ProxyError, ConnectTimeout, ReadTimeout, Timeout):
            proxy_list[proxy] = False
            if proxyerr is not None:
                txt_write(proxyerr, proxy)
        except (JSONDecodeError, ChunkedEncodingError):
            pass
        except Exception:
            if stderr:
                err = ['------',
                       scraper.__name__,
                       proxy,
                       *func_args,
                       traceback.format_exc()]
                txt_write(stderr, err)
            else:
                print(proxy, *func_args)
            if debug:
                traceback.print_exc()
                time.sleep(300)
    return None


def mrun(
        func,  # the worker function
        iterable,  # iterable of arguments (each element passed to func)
        n_workers,  # max pool size
        result_handler,  # callable to handle (result)
        timeout=60,  # per-task timeout in seconds
        desc=None,  # tqdm description
):
    """
    Run tasks in parallel using multiprocessing with per-task timeout and progress tracking.

    Args:
        func (callable): The worker function to apply to each item in the iterable.
        iterable (iterable): An iterable of items to pass individually to the worker function.
        n_workers (int): Maximum number of parallel worker processes to use.
        result_handler (callable): Function to handle each result (called with non-None results).
        timeout (int, optional): Timeout in seconds for each task result. Defaults to 60.
        desc (str, optional): Description to show in the tqdm progress bar.
    """

    def _run_next(retries=2):
        for _ in range(retries):
            try:
                if (data := results.next(timeout=timeout)) is not None:
                    result_handler(data)
                return True
            except TimeoutError:
                pass
        return False

    iterable = list(iterable)
    pool_size = min(n_workers, len(iterable))
    with Pool(pool_size) as pool, tqdm(total=len(iterable), desc=desc) as bar:
        results = pool.imap_unordered(func, iterable)
        for _ in range(len(iterable)):
            _run_next()
            bar.update(1)
