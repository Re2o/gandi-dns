import logging
import json

import requests

API_URL = "https://api.gandi.net/v5/"


class GandiAPIClient:
    """Wrapper for the Gandi API client.

    It handles Gandi API over https for LiveDNS. Logging is done through the
    `gandiAPI` logger. See `logging` package documentation for how to configure
    it.
    """

    def __init__(self, api_key):
        """Initializes the API client.

        Args:
            api_key: the API key as provided by Gandi.
            log_level: logging level (see `logging` package documentation)
        """
        self.logger = logging.getLogger("gandiAPI")
        self.api_key = api_key

    def _request(self, method, url, headers={}, params={}, *args, **kwargs):
        self.logger.debug(
            "Requesting %s: %s, headers=%r, params=%r, args=%r, kwargs=%r",
            method,
            url,
            headers,
            params,
            args,
            kwargs,
        )

        headers.update({"Authorization": "Apikey  %s" % self.api_key})
        response = getattr(requests, method)(
            url, headers=headers, params=params, allow_redirects=False, *args, **kwargs
        )

        self.logger.debug("Got response %r.", response)
        response.raise_for_status()
        try:
            ret = response.json()
        except json.decoder.JSONDecodeError as e:
            ret = None
            self.logger.debug("No valid JSON in the response.")
        self.logger.debug("Request {} {} successful.".format(method, response.url))
        return ret

    def delete(self, *args, **kwargs):
        """Performs a DELETE request.

        DELETE request on a given URL that acts like `requests.delete` except
        that authentication to the API is automatically done and JSON response
        is decoded.

        Args:
            url: The URL of the requests.
            *args: See `requests.delete` parameters.
            **kwargs: See `requests.delete` parameters.

        Returns:
            The JSON-decoded result of the request.

        Raises:
            requests.exceptions.RequestException: An error occured while
            performing the request.
            exceptions.PermissionDenied: The user does not have the right
            to perform this request.
        """
        return self._request("delete", *args, **kwargs)

    def get(self, *args, **kwargs):
        """Performs a GET request.

        GET request on a given URL that acts like `requests.get` except that
        authentication to the API is automatically done and JSON response is
        decoded.

        Args:
            url: The URL of the requests.
            *args: See `requests.get` parameters.
            **kwargs: See `requests.get` parameters.

        Returns:
            The JSON-decoded result of the request.

        Raises:
            requests.exceptions.RequestException: An error occured while
            performing the request.
            exceptions.PermissionDenied: The user does not have the right
            to perform this request.
            """
        return self._request("get", *args, **kwargs)

    def head(self, *args, **kwargs):
        """Performs a HEAD request.

        HEAD request on a given URL that acts like `requests.head` except that
        authentication to the API is automatically done and JSON response is
        decoded.

        Args:
            url: The URL of the requests.
            *args: See `requests.head` parameters.
            **kwargs: See `requests.head` parameters.

        Returns:
            The JSON-decoded result of the request.

        Raises:
            requests.exceptions.RequestException: An error occured while
            performing the request.
            exceptions.PermissionDenied: The user does not have the right
            to perform this request.
            """
        return self._request("get", *args, **kwargs)

    def option(self, *args, **kwargs):
        """Performs a OPTION request.

        OPTION request on a given URL that acts like `requests.option` except
        that authentication to the API is automatically done and JSON response
        is decoded.

        Args:
            url: The URL of the requests.
            *args: See `requests.option` parameters.
            **kwargs: See `requests.option` parameters.

        Returns:
            The JSON-decoded result of the request.

        Raises:
            requests.exceptions.RequestException: An error occured while
            performing the request.
            exceptions.PermissionDenied: The user does not have the right
            to perform this request.
            """
        return self._request("get", *args, **kwargs)

    def patch(self, *args, **kwargs):
        """Performs a PATCH request.

        PATCH request on a given URL that acts like `requests.patch` except
        that authentication to the API is automatically done and JSON response
        is decoded.

        Args:
            url: The URL of the requests.
            *args: See `requests.patch` parameters.
            **kwargs: See `requests.patch` parameters.

        Returns:
            The JSON-decoded result of the request.

        Raises:
            requests.exceptions.RequestException: An error occured while
            performing the request.
            exceptions.PermissionDenied: The user does not have the right
            to perform this request.
            """
        return self._request("patch", *args, **kwargs)

    def post(self, *args, **kwargs):
        """Performs a POST request.

        POST request on a given URL that acts like `requests.post` except that
        authentication to the API is automatically done and JSON response is
        decoded.

        Args:
            url: The URL of the requests.
            *args: See `requests.post` parameters.
            **kwargs: See `requests.post` parameters.

        Returns:
            The JSON-decoded result of the request.

        Raises:
            requests.exceptions.RequestException: An error occured while
            performing the request.
            exceptions.PermissionDenied: The user does not have the right
            to perform this request.
            """
        return self._request("post", *args, **kwargs)

    def put(self, *args, **kwargs):
        """Performs a PUT request.

        PUT request on a given URL that acts like `requests.put` except that
        authentication to the API is automatically done and JSON response is
        decoded.

        Args:
            url: The URL of the requests.
            *args: See `requests.put` parameters.
            **kwargs: See `requests.put` parameters.

        Returns:
            The JSON-decoded result of the request.

        Raises:
            requests.exceptions.RequestException: An error occured while
            performing the request.
            exceptions.PermissionDenied: The user does not have the right
            to perform this request.
            """
        return self._request("put", *args, **kwargs)


class APIElement:
    def __init__(self, client, api_endpoint):
        self.client = client
        self.api_endpoint = api_endpoint

    def save(self):
        data = self.as_api()
        if self.exists:
            self.client.put(API_URL + self.api_endpoint, json=data)
        else:
            self.client.post(API_URL + self.api_endpoint, json=data)

    @property
    def exists(self):
        try:
            r = self.client.get(API_URL + self.api_endpoint)
            return True
        except requests.exceptions.HTTPError:
            return False

    def fetch(self):
        r = self.client.get(API_URL + self.api_endpoint)
        self.from_dict(r)

    def delete(self):
        self.client.delete(API_URL + self.api_endpoint)


class Record(APIElement):
    class Types:
        A = "A"
        AAAA = "AAAA"
        ALIAS = "ALIAS"
        CAA = "CAA"
        CDS = "CDS"
        CNAME = "CNAME"
        DNAME = "DNAME"
        DS = "DS"
        KEY = "KEY"
        LOC = "LOC"
        MX = "MX"
        NS = "NS"
        OPENPGPKEY = "OPENPGPKEY"
        PTR = "PTR"
        SPF = "SPF"
        SRV = "SRV"
        SSHFP = "SSHFP"
        TLSA = "TLSA"
        TXT = "TXT"
        WKS = "WKS"

    ENDPOINT = "livedns/domains/{fqdn}/records/{rrset_name}/{rrset_type}"

    def __init__(
        self,
        client,
        domain,
        rrset_name="",
        rrset_type=None,
        rrset_values=None,
        rrset_ttl=10800,
        **kwargs
    ):
        endpoint = self.ENDPOINT.format(
            fqdn=domain, rrset_name=rrset_name, rrset_type=rrset_type
        )
        super().__init__(client, endpoint)
        self.rrset_name = rrset_name
        self.rrset_type = rrset_type
        self.rrset_values = rrset_values
        self.rrset_ttl = rrset_ttl
        if self.rrset_values is None or self.rrset_type is None:
            self.fetch()

    @classmethod
    def from_name(cls, client, domain, name):
        cls(client, domain, rrset_name=name)

    def as_dict(self):
        return {
            "rrset_name": self.rrset_name,
            "rrset_type": self.rrset_type,
            "rrset_values": self.rrset_values,
            "rrset_ttl": self.rrset_ttl,
        }

    def as_api(self):
        return {"rrset_values": self.rrset_values, "rrset_ttl": self.rrset_ttl}

    def from_dict(self, d):
        self.rrset_name = d["rrset_name"]
        self.rrset_type = d["rrset_type"]
        self.rrset_values = d["rrset_values"]
        self.rrset_ttl = d.get("rrset_ttl", 10800)

    def __repr__(self):
        return "<Record name=%s, type=%s, values=%r, ttl=%s>" % (
            self.rrset_name,
            self.rrset_type,
            self.rrset_values,
            self.rrset_ttl,
        )

    def __eq__(self, other):
        return (
            self.rrset_name == other.rrset_name
            and self.rrset_type == other.rrset_type
            and self.rrset_values == other.rrset_values
            and self.rrset_ttl == other.rrset_ttl
        )

    def __hash__(self):
        return hash(repr(self))


class DomainsRecords(APIElement):
    ENDPOINT = "livedns/domains/{fqdn}/records"

    def __init__(self, client, fqdn, records=None, fetch=True):
        endpoint = self.ENDPOINT.format(fqdn=fqdn)
        super().__init__(client, endpoint)
        self.fqdn = fqdn
        self.records = records
        if self.records is None and fetch:
            self.fetch()
        else:
            self.records = []

    def save(self):
        for r in self.records:
            r.save()

    def from_dict(self, d):
        # l is actually an array
        if isinstance(d, dict):
            l = d["records"]
        else:
            l = d
        logging.getLogger("gandiAPI").debug(l)
        self.records = [Record(self.client, self.fqdn, **r) for r in l]

    def as_dict(self):
        return [r.as_dict() for r in self.records]

    def __repr__(self):
        return "<DomainsRecords domain=%s, records=%r>" % (self.fqdn, self.records)
