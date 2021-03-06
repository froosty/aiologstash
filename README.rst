aiologstash
==============

.. image:: https://travis-ci.org/wikibusiness/aiologstash.svg?branch=master
  :target:  https://travis-ci.org/wikibusiness/aiologstash
  :align: right

.. image:: https://codecov.io/gh/wikibusiness/aiologstash/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/wikibusiness/aiologstash

.. image:: https://badge.fury.io/py/aiologstash.svg
    :target: https://badge.fury.io/py/aiologstash

.. image:: https://badges.gitter.im/Join%20Chat.svg
    :target: https://gitter.im/aio-libs/Lobby
    :alt: Chat on Gitter


asyncio logging handler for logstash.


Installation::

   $ pip install aiologstash


Usage::

   import logging
   from aiologstash import create_tcp_handler

   async def init_logger():
        handler = await create_tcp_handler('127.0.0.1', 5000)
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        root.addHandler(handler)
