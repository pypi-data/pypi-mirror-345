Session Update
==============

Some APIs require additional arguments, such as custom headers, to be included in requests.
You can add these by overriding the session property in your **fitrequest** subclass.

.. code-block:: python

  from typing import Any
  from fitrequest.decorators import fit, retry
  from fitrequest.client import FitRequest


  class RestApiClient(FitRequest):
      """Awesome class generated with fitrequest."""

      client_name = 'rest_api'
      base_url = 'https://test.skillcorner.fr'
      method_docstring = 'Calling endpoint: {endpoint}'

      def __init__(self, username: str | None = None, password: str | None = None):
          self.session.update(
              auth={
                  'username': {'env_name': 'API_USERNAME', 'init_value': username},
                  'password': {'env_name': 'API_PASSWORD', 'init_value': password},
              },
              headers={"SOME_FIELD": "SOME_VALUE"},
              verify=False,  # Disable SSL verification
              timeout=20,  # Set request timeout
          )
          self.session.authenticate()

      @fit(endpoint='/items/')
      def get_items(self) -> Any: ...

      @fit(endpoint='/items/')
      async def async_get_items(self) -> Any: ...

      @retry(max_retries=3, on_status='500-600')
      @fit(endpoint='/items/{item_id}')
      def get_item(self, item_id: str) -> Any: ...

      @retry(max_retries=3, on_status='500-600')
      @fit(endpoint='/items/{item_id}/details/{detail_id}')
      def get_item_details(self, item_id: str, detail_id: str) -> Any: ...


  client = RestApiClient(username='toto', password='1234')


- The ``headers`` argument is merged with the default headers provided by **fitrequest**.
- Other arguments, such as ``verify`` (for SSL verification) and ``timeout``, are directly passed to the `httpx.Client <https://www.python-httpx.org/api/#client>`_ or `httpx.AsyncClient <https://www.python-httpx.org/api/#asyncclient>`_ during initialization.

This approach allows you to customize the request session as needed while retaining the flexibility of the default **fitrequest** behavior.


Configuration Merge
-------------------

**fitrequest** allows you to pass ``kwargs`` arguments at two levels:

1. **During Client Initialization**: By updating the ``session`` (as shown above).
2. **At Request Invocation**: When calling the generated method.

In these cases, the `configuration is merged <https://www.python-httpx.org/advanced/clients/#merging-of-configuration>`_ according to the following rules:

- **Headers, Query Parameters, and Cookies**: Values from both levels are combined. If there are conflicts, the request-level values take precedence.
- **Other Parameters**: Request-level values override those set during client initialization.

This merging mechanism ensures that you can define default configurations for the client while allowing specific requests to customize or override these defaults as needed.
