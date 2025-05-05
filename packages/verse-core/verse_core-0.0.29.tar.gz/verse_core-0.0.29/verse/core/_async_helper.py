import asyncio


class AsyncHelper:
    @staticmethod
    def to_async(func, *args, **kwargs):
        return asyncio.to_thread(func, *args, **kwargs)
