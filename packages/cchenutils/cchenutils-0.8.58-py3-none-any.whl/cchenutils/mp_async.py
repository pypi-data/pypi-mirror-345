import asyncio
import random
import traceback
from multiprocessing import Process

from requests.exceptions import ProxyError, ConnectTimeout, ReadTimeout, Timeout, JSONDecodeError, ChunkedEncodingError

from .files import txt_write


async def scraper_async(func, task, proxy_list=None, proxyerr=None, stderr=None, retries=3, debug=False, **func_kwargs):
    if proxy_list is None:
        retries = min(1, retries)
    for _ in range(retries):
        proxy = random.choice([ip for ip, ok in proxy_list.items() if ok]) if proxy_list else None
        try:
            return await func(task, proxy=proxy, **func_kwargs)
        except (ProxyError, ConnectTimeout, ReadTimeout, Timeout):
            if proxy_list and proxy in proxy_list:
                proxy_list[proxy] = False
            if proxyerr:
                txt_write(proxy, proxyerr)
        except (JSONDecodeError, ChunkedEncodingError):
            pass
        except Exception:
            if stderr:
                err = ['------', scraper_async.__name__, proxy, task, traceback.format_exc()]
                txt_write(err, stderr)
            if debug:
                traceback.print_exc()
                await asyncio.sleep(300)
    return None


async def _worker_loop(func, tasks, result_handler, proxy_list, proxyerr, stderr, retries, debug, sem_limit, **func_kwargs):
    sem = asyncio.Semaphore(sem_limit)

    async def run(task):
        async with sem:
            result = await scraper_async(
                func, task,
                proxy_list=proxy_list,
                proxyerr=proxyerr,
                stderr=stderr,
                retries=retries,
                debug=debug,
                **func_kwargs
            )
            if result is not None:
                result_handler(result)

    await asyncio.gather(*(run(task) for task in tasks))


def mrun_async(func, iterable, *, n_workers, result_handler, proxy_list=None, proxyerr=None, stderr=None,
               retries=3, debug=False, sem_limit=10, desc=None, **func_kwargs):
    """
    Run async tasks across multiple processes. Each process runs an asyncio event loop for concurrent execution.

    Args:
        func (coroutine): Async function to run per task.
        iterable (iterable): Task input items.
        n_workers (int): Number of parallel processes.
        result_handler (callable): Called with each successful result.
        proxy_list (Manager().dict, optional): Shared proxy state.
        proxyerr (str): Path to log failed proxies.
        stderr (str): Path to log unhandled errors.
        sem_limit (int): Max concurrent tasks per process.
    """
    iterable = list(iterable)
    if not iterable:
        return False

    chunks = [iterable[i::n_workers] for i in range(n_workers)]
    processes = []

    def worker(chunk):
        asyncio.run(_worker_loop(func, chunk, result_handler, proxy_list, proxyerr, stderr, retries, debug, sem_limit, **func_kwargs))

    for chunk in chunks:
        p = Process(target=worker, args=(chunk,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    return True
