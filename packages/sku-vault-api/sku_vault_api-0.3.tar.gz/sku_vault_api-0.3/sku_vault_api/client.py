from datetime import datetime
import logging
import time
from pytz import utc
from deceit.exceptions import ApiException
from deceit.api_client import ApiClient


log = logging.getLogger(__name__)


class SkuVaultException(ApiException):
    # marker class to note api exceptions from
    # the sku vault api
    pass


class SkuVaultApi(ApiClient):
    def __init__(self, user_token=None, tenant_token=None, conf=None):
        super().__init__(
            base_url='https://app.skuvault.com/api',
            default_timeout=30,
            exception_class=SkuVaultException,
        )
        if conf:
            self.user_token = conf.get('user_token')
            self.tenant_token = conf.get('tenant_token')
        else:
            self.user_token = user_token
            self.tenant_token = tenant_token

    def headers(self, *args, **kwargs):
        return {
            'accept': 'application/json',
            'content-type': 'application/json',
        }

    def update_payload(self, payload):
        payload['UserToken'] = self.user_token
        payload['TenantToken'] = self.tenant_token
        return payload

    @classmethod
    def to_iso(cls, dt):
        if isinstance(dt, datetime):
            if dt.tzinfo:
                dt = dt.astimezone(utc)
                dt = dt.replace(tzinfo=None)
            return dt.isoformat('T', 'seconds')
        return dt

    def get_products_page(self, after=None, before=None, page=0, limit=10000, raw=False, **kwargs):
        """
        Get a page of products from sku vault

        :param (str) after: Modified product details after date time in UTC.
        :param (str) before: Modified product details before date time in UTC.
        :param (int) page: Page number to return.
        :param (int) limit: max number of items to return.

        """
        payload = {
            'PageNumber': page,
            'PageSize': limit,
        }
        if after:
            payload['ModifiedAfterDateTimeUtc'] = self.to_iso(after)
        if before:
            payload['ModifiedBeforeDateTimeUtc'] = self.to_iso(before)
        payload = self.update_payload(payload)
        return self.post('products/getProducts', json_data=payload, raw=raw)

    def get_transactions_page(self, from_date, to_date, page=0, limit=10000, raw=False, **kwargs):
        """
        Get a page of transactions from sku vault

        :param (str) from_date: date time in UTC.
        :param (str) to_date: date time in UTC.
        :param (int) page: Page number to return.
        :param (int) limit: max number of items to return.

        """
        payload = {
            'PageNumber': page,
            'PageSize': limit,
            'FromDate': self.to_iso(from_date),
            'ToDate': self.to_iso(to_date),
        }
        payload = self.update_payload(payload)
        return self.post('inventory/getTransactions', json_data=payload, raw=raw)

    def get_inventory_by_location_page(self, page=0, limit=10000, raw=False, **kwargs):
        """
        Get a page of products from sku vault

        :param (int) page: Page number to return.
        :param (int) limit: max number of items to return.

        """
        payload = {
            'PageNumber': page,
            'PageSize': limit,
        }
        payload = self.update_payload(payload)
        return self.post('inventory/getInventoryByLocation', json_data=payload, raw=raw)

    def get_pos_page(self, page=0, limit=10000,
                     include_products=False,
                     status='Everything except Completed',
                     min_date=None, max_date=None,
                     raw=False, **kwargs):
        """
        Get a page of pos from sku vault

        :param (int) page: Page number to return.
        :param (int) limit: max number of items to return.
        :param (datetime | str) min_date: Modified product details after date time in UTC.
        :param (datetime | str) max_date: Modified product details before date time in UTC.
        :param (bool) include_products: Include products in the response.
        :param (str) status: Status of the pos to return.
        """
        payload = {
            'PageNumber': page,
            'PageSize': limit,
            'IncludeProducts': include_products or False,
            'Status': status,
        }
        if min_date:
            payload['ModifiedAfterDateTimeUtc'] = self.to_iso(min_date)
        if max_date:
            payload['ModifiedBeforeDateTimeUtc'] = self.to_iso(max_date)
        payload = self.update_payload(payload)
        return self.post('purchaseorders/getPOs', json_data=payload, raw=raw)

    def get_kits_page(self, after=None, before=None, page=0, raw=False, timeout=120, **kwargs):
        """
        Get a page of kits from sku vault

        :param (str) after: Modified product details after date time in UTC.
        :param (str) before: Modified product details before date time in UTC.
        :param (int) page: Page number to return.

        """
        payload = {
            'PageNumber': page,
            'IncludeKitCost': True,
        }
        keys = [ x for x in kwargs ]
        for key in keys:
            value = None
            if key in ('AvailableQuantityModifiedAfterDateTimeUtc', 'AvailableQuantityModifiedBeforeDateTimeUtc'):
                value = kwargs.pop(key)
            elif key in ('GetAvailableQuantity', 'IncludeKitCost', 'KitSKUs'):
                value = kwargs.pop(key)
            if value is not None:
                payload[key] = value
        if after:
            payload['ModifiedAfterDateTimeUtc'] = self.to_iso(after)
        if before:
            payload['ModifiedBeforeDateTimeUtc'] = self.to_iso(before)
        payload = self.update_payload(payload)
        return self.post(
            'products/getKits',
            json_data=payload,
            raw=raw,
            timeout=timeout,
            **kwargs)

    def get_locations(self, raw=False):
        """
        Get all locations
        """
        payload = {}
        payload = self.update_payload(payload)
        result = self.post('inventory/getLocations', json_data=payload, raw=raw)
        if raw:
            return result
        return result['Items']

    @classmethod
    def yielder(cls, fn, key, after=None, before=None, dict_key=None, **kwargs):
        """
        yields products from sku vault
        """
        page = 0
        while True:
            kwargs.pop('raw', None)
            response = fn(after=after, before=before, page=page, raw=True, **kwargs)
            headers = response.headers
            data = response.json()
            result = data.get(key)
            if not result:
                break
            if isinstance(result, list):
                yield from result
            elif isinstance(result, dict):
                for key, value in result.items():
                    for x in value:
                        x[dict_key] = key
                        yield x
            page += 1
            cls.handle_rate_limit(headers)
            if page > 500:
                break

    def yield_products(self, after=None, before=None):
        """
        yields products from sku vault
        """
        fn = self.get_products_page
        key = 'Products'
        for x in self.yielder(fn, key, after, before):
            yield x

    def yield_kits(self, after=None, before=None):
        """
        yields kits
        """
        fn = self.get_kits_page
        key = 'Kits'
        for x in self.yielder(fn, key, after, before):
            yield x

    @classmethod
    def handle_rate_limit(cls, headers):
        remaining = int(headers['X-RateLimit-Remaining'])
        if remaining == 0:
            delay = headers['X-RateLimit-Reset'].split(':', 2)[-1]
            delay = int(delay.split('.', 1)[0])
            delay += 1
            log.info('rate limit reached, sleeping for %s seconds', delay)
            time.sleep(delay)

    def yield_inventory_by_location(self, n_max=None):
        """
        yields inventory by locationfrom sku vault
        """
        fn = self.get_inventory_by_location_page
        key = 'Items'
        for i, x in enumerate(self.yielder(fn, key, dict_key='Sku'), 1):
            yield x
            if n_max and i >= n_max:
                break

    def yield_transactions(self, from_date, to_date):
        """
        yields inventory transactions from sku vault
        """
        fn = self.get_transactions_page
        key = 'Transactions'
        for x in self.yielder(fn, key, from_date=from_date, to_date=to_date):
            yield x
