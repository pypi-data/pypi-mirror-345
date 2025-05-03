import copy
import functools
from datetime import datetime
from typing import Optional, Union
import requests.models
from deceit.exceptions import ApiException
from building.base import BigApi


class BigV2Exception(ApiException):
    """
    marker class to catch exceptions thrown by the v2 api
    """
    pass


class BigV2Api(BigApi):
    exception_class = BigV2Exception
    version = 'v2'

    def time(self, raw: bool = False) -> Union[requests.models.Response, dict]:
        """Returns the system timestamp at the time of the request. The time
        resource is useful for validating API authentication details and
        testing client connections.

        :raises: BigV2ApiException
        """
        return self.get('time')

    def order_page(
            self,
            page: Optional[int] = None,
            limit: Optional[int] = None,
            min_date_modified: Optional[datetime] = None,
            max_date_modified: Optional[datetime] = None,
            raw: bool = False,
            **kwargs):
        """Gets a list of orders using the filter query. The default sort is by
        order id, from lowest to highest.

        :raises: BigV2Exception
        """
        params = copy.copy(kwargs)
        params.update(
            limit=min(limit or 250, 250),
            page=page or 1)
        if min_date_modified:
            params['min_date_modified'] = self.normalize_date(min_date_modified)
        if max_date_modified:
            params['max_date_modified'] = self.normalize_date(max_date_modified)
        return self.get('orders', params=params, raw=raw)

    def page_page(
            self,
            page: Optional[int] = None,
            limit: Optional[int] = None,
            raw: bool = False,
            **kwargs):
        """
        gets a page of pages

        :raises: BigV2Exception
        """
        params = copy.copy(kwargs)
        params.update(
            limit=min(limit or 100, 100),
            page=page or 1)
        return self.get('pages', params=params, raw=raw)

    def orders(self, *args, min_date_modified=None, max_date_modified=None, n_max=0, **kwargs):
        """Get a list of orders using the filter query. The default sort is by
        order id, from lowest to highest.

        :raises: BigV2Exception
        """
        g = self.yield_orders(
            *args,
            min_date_modified=min_date_modified,
            max_date_modified=max_date_modified,
            n_max=n_max,
            **kwargs)
        return list(g)
        
    def yield_orders(self, *args, min_date_modified=None, max_date_modified=None, n_max=0, **kwargs):
        """Get a list of orders using the filter query. The default sort is by
        order id, from lowest to highest.

        :raises: BigV2Exception
        """
        fn = self.order_page
        for x in self.paginate_and_yield(
            fn, *args,
            min_date_modified=min_date_modified,
            max_date_modified=max_date_modified,
            n_max=n_max,
            **kwargs):
            yield x

    def shipments(self, order_id, **kwargs):
        """
        Get a list of shipments for a given
        order id.

        :raises: BigV2Exception
        """
        route = f'orders/{order_id}/shipments'
        return self.get(route, **kwargs)

