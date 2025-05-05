Python @fit Decorator
"""""""""""""""""""""

Instead of using the ``method_config_list`` attribute to define **fitrequest** methods, you can use the ``@fit`` decorator. This option is more IDE-friendly because the generated method is explicitly declared, preventing the IDE from raising warnings when the method is used. It is also more developer-friendly when working with decorators.

.. code-block:: python

  from typing import Any
  from fitrequest.decorators import fit
  from fitrequest.client import FitRequest

  class RestApiClient(FitRequest):
      """Awesome class generated with FitRequest."""

      client_name = 'rest_api'
      base_url = 'https://test.skillcorner.fr'
      method_docstring = 'Calling endpoint: {endpoint}'

      @fit(endpoint='/items/')
      def get_items(self) -> Any: ...

      @fit(endpoint='/items/')
      async def async_get_items(self) -> Any: ...

      @fit(endpoint='/items/{item_id}')
      def get_item(self, item_id: str) -> Any: ...

      @fit(endpoint='/items/{item_id}/details/{detail_id}')
      def get_item_details(self, item_id: str, detail_id: str) -> Any: ...

  client_decorated = RestApiClient()


.. hint:: You can combine both the ``method_config_list`` attribute and the ``@fit`` decorator if needed.
