Library to make simples integration RedisDb with Django


Database connect string example in django settings.py file:

.. code-block:: python

    REDISDB = {'default': {'HOST': '127.0.0.1',
                           'PORT': 6379,
                           'DB': 0,
                           'PASSWORD': 'secret string'}}


Example access to redis database:


.. code-block:: python

   from sdh.redis import RedisConn

   with RedisConn() as redis:
       redis.set('test', 'value')


RedisConn accept argument *db_alias* that point to required database 
from REDISDB parameters:


.. code-block:: python

   from sdh.redis import RedisConn

   with RedisConn('db2') as redis:
       redis.set('test', 'value')

