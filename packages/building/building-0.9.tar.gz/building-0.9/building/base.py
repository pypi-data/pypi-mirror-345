import logging
import posixpath
import time
from datetime import date
from datetime import datetime
from pytz import utc
from pytz import timezone
from deceit.api_client import ApiClient
from waddle import ParamBunch


log = logging.getLogger(__name__)
default_tz = timezone('PST8PDT')


class BigApi(ApiClient):
    exception_class = None
    version = None

    def __init__(self, *args, access_token=None, store=None,
                 conf: ParamBunch = None, default_timeout=None, **kwargs):
        base_url = kwargs.pop('base_url', None)
        self.store = store
        if conf and not self.store:
            self.store = conf.get('store')
        if not base_url:
            base_url = conf.get('base_url') if conf else None
            base_url = base_url or 'https://api.bigcommerce.com'
            base_url = posixpath.join(base_url, 'stores', self.store, self.version)

        kwargs.setdefault('exception_class', self.__class__.exception_class)
        super().__init__(
            *args,
            default_timeout=default_timeout,
            base_url=base_url,
            **kwargs)
        self.access_token = access_token
        if conf and not self.access_token:
            self.access_token = conf.get('access_token')

    def headers(self, *args, **kwargs):
        h = super().headers(*args, **kwargs)
        h['x-auth-token'] = self.access_token
        h.setdefault('content-type', 'application/json')
        h.setdefault('accept', 'application/json')
        return h

    def handle_rate_limit(self, headers):
        """
        X-Rate-Limit-Time-Window-Ms: 30000
        X-Rate-Limit-Time-Reset-Ms: 15000
        X-Rate-Limit-Requests-Quota: 150
        X-Rate-Limit-Requests-Left: 35
        """
        if not 'x-rate-limit-requests-left' in headers:
            return
        remaining = int(headers.get('x-rate-limit-requests-left'))
        if remaining < 5:
            delay = int(headers.get('x-rate-limit-time-reset-ms')) / 1000
            log.info('rate limit exceeded, sleeping for %s seconds', delay)
            time.sleep(delay)

    @classmethod
    def normalize_date(cls, dt, default_timezone=None):
        if isinstance(dt, date):
            if not isinstance(dt, datetime):
                dt = datetime(dt.year, dt.month, dt.day)
            tz = default_timezone or default_tz
            if not dt.tzinfo:
                dt = tz.localize(dt)
            dt = dt.astimezone(utc)
            result = dt.isoformat('T', 'seconds')
            return result.replace('+00:00', 'Z')
        return dt

    def paginate_and_yield(self, fn, page=1, limit=250, n_max=0, **kwargs):
        n_total = 0
        done = False
        n_pages = -1
        while not done:
            self.log.debug('%s getting page %s / %s', fn.__name__, page, n_pages)
            kwargs.pop('raw', None)
            response = fn(page=page, limit=limit, raw=True, **kwargs)
            headers = response.headers
            payload = response.json()
            pagination = {}
            if isinstance(payload, dict) and 'data' in payload:
                results = payload['data']
                pagination = payload.get('meta', {}).get('pagination') or {}
                n_pages = pagination['total_pages']
            else:
                results = payload

            for x in results:
                n_total += 1
                if n_total > n_max > 0:
                    break
                yield x
            page += 1
            total_pages = pagination.get('total_pages') or 0
            done = n_total >= n_max > 0 or page > total_pages
            if not pagination:
                done = done or len(results) < limit
