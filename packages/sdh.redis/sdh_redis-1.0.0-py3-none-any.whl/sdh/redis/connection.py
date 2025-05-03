import redis
from datetime import datetime, timezone

from .pool import redis_pool_manager


class RedisConn:
    def __init__(self, db_alias='default'):
        self.conn = None
        self.db_alias = db_alias

    def __enter__(self):
        self.conn = redis.Redis(
            connection_pool=redis_pool_manager.get_pool(self.db_alias))
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @staticmethod
    def stamp2str(stamp):
        """Convert aware stamp into UTC and convert it to format
        %Y-%m-%d %H:%M:%S.%fZ
        Using together with Redis storage and other related
        """
        return stamp.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%fZ')

    @staticmethod
    def str2stamp(stamp_str):
        """ Convert string into aware time stamp,
        assume that string in UTC time zone
        """
        formats = ('%Y-%m-%d %H:%M:%S.%fZ',
                   '%Y-%m-%d %H:%M:%S.%f',
                   '%Y-%m-%d %H:%M:%S',
                   '%Y-%m-%d %H:%M')
        stamp = None
        for fmt in formats:
            try:
                stamp = datetime.strptime(stamp_str, fmt)
            except ValueError:
                continue
        if stamp is None:
            raise ValueError()

        return stamp.replace(tzinfo=timezone.utc)
