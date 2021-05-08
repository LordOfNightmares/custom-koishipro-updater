import concurrent.futures
from functools import wraps, partial


# import logging
#
# logging.basicConfig(format='%(asctime)s:\t%(threadName)s:%(levelname)s:\t%(message)s',
#                     level=logging.INFO,
#                     datefmt="%H:%M:%S")
#

# workers = 10

def threaded(func=None, *, workers=10):
    if func is None:
        return partial(threaded, workers=workers)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # print(f"{args=}")
        # print(f"{kwargs=}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers, thread_name_prefix='T') as executor:
            if len(args) > 1 and kwargs:
                futures = [executor.submit(func, *arg, *args[1:], **kwargs) for arg in zip(args[0])]
            elif len(args) > 1:
                futures = [executor.submit(func, *arg, *args[1:]) for arg in zip(args[0])]
            elif kwargs:
                futures = [executor.submit(func, *arg, **kwargs) for arg in zip(args[0])]
            else:
                futures = [executor.submit(func, *arg) for arg in zip(args[0])]
        return [future.result() for future in futures if future.done()]

    return wrapper

# -----------------------------------TEST-----------------------------------
#
# @threaded(workers=60)
# def test(*args, **kwargs):
#     # print(kwargs)
#     response = args[0]
#     try:
#         logging.info(f'{args=}\t{kwargs=}\t{response=}')
#         # progress.update(1)
#         return response
#
#     except:
#         logging.exception(f'Exception: {args}')
#         pass
#
#
# if __name__ == '__main__':
#     vals = range(10)
#     kw = {'a': 1, "b": 2, "c": 3}
#     wk = {'a1': True, "b2": False, "c3": None}
#
#     print(f'{test(vals,kw,**wk)=}')
