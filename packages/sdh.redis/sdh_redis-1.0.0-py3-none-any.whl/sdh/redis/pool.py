import redis
from django.conf import settings as django_settings


class RedisPoolManager:
    pool_manager = redis.BlockingConnectionPool

    def __init__(self, settings):
        self.settings = settings
        self.pools = {}

    def get_pool(self, db_alias):
        if db_alias not in self.pools:
            if not hasattr(self.settings, 'REDISDB') and db_alias == 'default':
                self.pools[db_alias] = self.pool_manager(
                    host=django_settings.REDIS_HOST,
                    port=django_settings.REDIS_PORT,
                    db=django_settings.REDIS_DATABASE,
                    password=django_settings.REDIS_PASSWORD,
                    decode_responses=True)
            else:
                params = {}
                config = self.settings.REDISDB[db_alias]
                params['host'] = config.get('HOST', '127.0.0.1')
                params['port'] = config.get('PORT', 6379)
                params['db'] = config.get('DB', 0)
                params['password'] = config.get('PASSWORD', None)
                if config.get('USE_SSL', False):
                    params['connection_class'] = redis.connection.SSLConnection
                    params['ssl_cert_reqs'] = config.get('SSL_CERT_REQS', 'none')
                    params['ssl_certfile'] = config.get('SSL_CERT', None)
                    params['ssl_keyfile'] = config.get('SSL_KEY', None)
                    params['ssl_ca_certs'] = config.get('SSL_CA_CERT', None)
                params['decode_responses'] = True
                self.pools[db_alias] = self.pool_manager(**params)

        return self.pools[db_alias]


redis_pool_manager = RedisPoolManager(django_settings)
