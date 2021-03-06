import abc
import asyncio
import logging

from async_timeout import timeout
from logstash import LogstashFormatterVersion1

from .log import logger


class BaseLogstashHandler(logging.Handler):

    def __init__(self,
                 formatter, level, close_timeout, qsize, loop,
                 **kwargs):
        self._close_timeout = close_timeout

        self._loop = loop

        self._queue = asyncio.Queue(maxsize=qsize, loop=self._loop)

        if formatter is None:
            formatter = LogstashFormatterVersion1()

        super().__init__(level=level, **kwargs)
        self.setFormatter(formatter)

        self._closing = False
        self._worker = self._loop.create_task(self._work())

    @abc.abstractmethod
    async def connect(self):
        pass  # pragma: no cover

    def emit(self, record):
        if self._closing:
            msg = 'Log message skipped due shutdown "%(record)s"'
            context = {'record': record}
            logger.warning(msg, context)
            return

        if self._queue.full():
            msg = 'Queue is full, drop oldest message: "%(record)s"'
            context = {'record': self._queue.get_nowait()}
            logger.warning(msg, context)

        self._queue.put_nowait(record)

    async def _work(self):
        while True:
            record = await self._queue.get()

            if record is ...:
                self._queue.put_nowait(...)
                break

            try:
                await self._send(record)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                msg = 'Unexpected Exception while sending log'
                logger.warning(msg, exc_info=exc)

    def _serialize(self, record):
        return self.format(record) + b'\n'

    @abc.abstractmethod
    async def _send(self, record):
        pass  # pragma: no cover

    # dummy statement for default handler close()
    # non conditional close() usage actually
    def close(self):
        if self._closing:
            return
        self._closing = True

        if self._queue.full():
            msg = ('Queue is full, drop oldest message before closing'
                   ': "%(record)s"')
            context = {'record': self._queue.get_nowait()}
            logger.warning(msg, context)
        self._queue.put_nowait(...)

        super().close()

    @abc.abstractmethod
    async def wait_closed(self):
        if self._worker is None:
            return  # already closed
        try:
            async with timeout(self._close_timeout, loop=self._loop):
                await self._worker
        except asyncio.TimeoutError:
            self._worker.cancel()

            try:
                await self._worker
            except:  # noqa
                pass

        self._worker = None

        assert self._queue.qsize() == 1
        assert self._queue.get_nowait() is ...
