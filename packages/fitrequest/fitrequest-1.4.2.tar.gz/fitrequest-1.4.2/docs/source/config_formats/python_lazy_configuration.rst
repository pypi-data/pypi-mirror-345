Python Configuration
""""""""""""""""""""

This is a straightforward declarative option using Python code that eliminates the need for users to define types explicitly,
as Pydantic models will automatically handle data coercion.


.. code-block:: python

  from fitrequest.client import FitRequest

  class RestApiClient(FitRequest):
      """Awesome class generated with FitRequest."""

      client_name = 'rest_api'
      base_url = 'https://test.skillcorner.fr'
      method_docstring = 'Calling endpoint: {endpoint}'

      method_config_list = [
          {
              'base_name': 'items',
              'endpoint': '/items/',
              'add_async_method': True,
          },
          {
              'name': 'get_item',
              'endpoint': '/items/{item_id}',
          },
          {
              'name': 'get_item_details',
              'endpoint': '/items/{item_id}/details/{detail_id}',
          },
      ]

  client_config = RestApiClient()
