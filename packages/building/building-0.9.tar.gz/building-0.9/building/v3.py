import copy
import functools
from datetime import datetime
from typing import Optional, Dict, Any

from deceit.exceptions import ApiException
from building.base import BigApi


class BigV3Exception(ApiException):
    """
    marker class to catch exceptions thrown by the v3 api
    """
    pass


class BigV3Api(BigApi):
    exception_class = BigV3Exception
    version = 'v3'

    def logs(
            self,
            page: Optional[int] = None,
            limit: Optional[int] = None,
            **kwargs,
    ):
        """This API can be used to retrieve and filter for specific store logs.
        """
        params = copy.copy(kwargs)
        params.update(
            limit=min(limit or 250, 250),
            page=page or 1)
        return self.get('store/systemlogs', params=params)

    def product_page(self,
            page: Optional[int] = None,
            limit: Optional[int] = None,
            min_date_modified: Optional[datetime] = None,
            raw: bool = False,
            **kwargs) -> Dict[Any, Any]:
        """Returns a list of Products. Optional filter parameters can be
        passed in.

        :Keyword Arguments:
            * *include* (``str``) --
               Sub-resources to include on a product, in a comma-separated list. If options or modifiers is used, results are limited to 10 per page.
                   Allowed values:
                   ``variants``
                   ``images``
                   ``custom_fields``
                   ``bulk_pricing_rules``
                   ``primary_image``
                   ``modifiers``
                   ``options``
                   ``videos``
        :raises: BigV3Exception
        """
        params = copy.copy(kwargs)
        params.update(
            limit=min(limit or 250, 250),
            page=page or 1)
        if min_date_modified:
            params['date_modified:min'] = self.normalize_date(min_date_modified)
        return self.get('catalog/products', params=params, raw=raw)

    def customer_page(self,
            page: Optional[int] = None,
            limit: Optional[int] = None,
            min_date_modified: Optional[datetime] = None,
            max_date_modified: Optional[datetime] = None,
            raw: bool = False,
            **kwargs) -> Dict[Any, Any]:
        """
        Returns a list of Products. Optional filter parameters can be
        passed in.

        :Keyword Arguments:
            * *include* (``str``) --
               Sub-resources to include on a customer, in a comma-separated list. If options or modifiers is used, results are limited to 10 per page.
                   Allowed values:
                   ``addresses``
                   ``storecredit``
                   ``attributes``
                   ``formfields``
                   ``shopper_profile_id``
                   ``segment_ids``
        :raises: BigV3Exception
        """
        params = copy.copy(kwargs)
        params.update(
            limit=min(limit or 50, 50),
            page=page or 1)
        params.setdefault('include', 'addresses,storecredit')
        if min_date_modified:
            params['date_modified:min'] = self.normalize_date(min_date_modified)
        if max_date_modified:
            params['date_modified:max'] = self.normalize_date(max_date_modified)
        return self.get('customers', params=params, raw=raw)

    def variant_page(self,
            page: Optional[int] = None,
            limit: Optional[int] = None,
            raw: bool = False,
            **kwargs) -> Dict[Any, Any]:
        """Returns a list of all variants in your catalog. Optional parameters
        can be passed in.

        :Keyword Arguments:
        :raises: BigV3Exception
        """
        params = copy.copy(kwargs)
        params.update(
            limit=min(limit or 250, 250),
            page=page or 1)
        return self.get('catalog/variants', params=params, raw=raw)

    def page_page(self,
            page: Optional[int] = None,
            limit: Optional[int] = None,
            raw: bool = False,
            **kwargs) -> Dict[Any, Any]:
        """Returns a list of all pages from the content api.
        https://developer.bigcommerce.com/docs/rest-content/pages

        Optional parameters can be passed in.

        :Keyword Arguments:
        :raises: BigV3Exception
        """
        params = copy.copy(kwargs)
        params.update(
            limit=min(limit or 250, 250),
            page=page or 1)
        return self.get('content/pages', params=params, raw=raw)

    def products(self, min_date_modified=None, n_max=0, limit=250, **kwargs):
        fn = self.product_page
        g = self.paginate_and_yield(fn, min_date_modified=min_date_modified, n_max=n_max, limit=limit, **kwargs)
        return list(g)

    def yield_products(self, min_date_modified=None, n_max=0, limit=250, **kwargs):
        fn = self.product_page
        for x in self.paginate_and_yield(fn, min_date_modified=min_date_modified, n_max=n_max, limit=limit, **kwargs):
            yield x

    def variants(self, n_max=0, limit=250):
        fn = self.variant_page
        return list(self.paginate_and_yield(fn, n_max=n_max, limit=limit))

    def yield_variants(self, n_max=0, limit=250):
        fn = self.variant_page
        for x in self.paginate_and_yield(fn, n_max=n_max, limit=limit):
            yield x

    def yield_pages(self, n_max=0, limit=250, **kwargs):
        fn = self.page_page
        for x in self.paginate_and_yield(fn, n_max=n_max, limit=limit, **kwargs):
            yield x

    def yield_customers(self, n_max=0, limit=50, **kwargs):
        fn = self.customer_page
        for x in self.paginate_and_yield(fn, n_max=n_max, limit=limit, **kwargs):
            yield x

    def pages(self, n_max=0, limit=250, **kwargs):
        return list(self.yield_pages(n_max=n_max, limit=limit, **kwargs))
