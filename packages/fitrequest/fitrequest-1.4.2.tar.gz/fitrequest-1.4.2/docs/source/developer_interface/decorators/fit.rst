fit
===

.. autodecorator:: fitrequest.decorators.fit.fit
.. autodecorator:: fitrequest.decorators.fit.get
.. autodecorator:: fitrequest.decorators.fit.put
.. autodecorator:: fitrequest.decorators.fit.post
.. autodecorator:: fitrequest.decorators.fit.patch
.. autodecorator:: fitrequest.decorators.fit.delete


Example
-------

.. code-block:: python

  from typing import Any
  from fitrequest.decorators import get, put, post, patch, delete, retry
  from fitrequest.client import FitRequest


  class RestApiClient(FitRequest):
      """Awesome class generated with fitrequest."""

      client_name = 'rest_api'
      base_url = 'https://test.skillcorner.fr'
      method_docstring = 'Calling endpoint: {request_verb.value.upper()} {endpoint}'

      @retry(max_retries=3, on_status='500-600')
      @get(endpoint='/items/{item_id}')
      def get_item(self, item_id: str) -> Any: ...

      @retry(max_retries=3, on_status='500-600')
      @put(endpoint='/items/{item_id}')
      def put_item(self, item_id: str, json: dict) -> Any: ...

      @retry(max_retries=3, on_status='500-600')
      @post(endpoint='/items/{item_id}')
      def post_item(self, item_id: str, json: dict) -> Any: ...

      @retry(max_retries=3, on_status='500-600')
      @patch(endpoint='/items/{item_id}')
      def patch_item(self, item_id: str, json: dict) -> Any: ...

      @retry(max_retries=3, on_status='500-600')
      @delete(endpoint='/items/{item_id}')
      def delete_item(self, item_id: str) -> Any: ...


  client_decorated_verbs = RestApiClient()
