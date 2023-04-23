import time

from functools import wraps

from pyproj import Geod
from shapely import Point, Polygon


def retry(exceptions_to_check, tries: int = 4, delay: int = 3, backoff: int = 2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)

                except exceptions_to_check as e:
                    msg = f"{str(e)}, Retrying in {mdelay} seconds..."
                    if logger:
                        logger.warning(msg)

                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


def degree_from_distance_from_node(lon: float, lat: float, distance: float) -> float:
    geod = Geod(ellps='WGS84')
    lon1, lat1, _ = geod.fwd(lon, lat, 0, distance)
    lon2, lat2, _ = geod.fwd(lon, lat, 180, distance)
    lon_diff, lat_diff = abs(lon1 - lon2), abs(lat1 - lat2)
    return max(lon_diff, lat_diff)


def buffer_point(lon: float, lat: float, buffer_dist: float | int) -> Polygon:
    """Create a buffer from a 4326 point"""
    return Point(lat, lon).buffer(degree_from_distance_from_node(lon, lat, buffer_dist), 2)



