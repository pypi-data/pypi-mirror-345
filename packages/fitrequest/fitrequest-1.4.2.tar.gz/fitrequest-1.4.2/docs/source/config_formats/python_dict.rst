Python dict
"""""""""""

You can generate the **fitrequest** client class using a python ``dict``.

.. code-block:: python

  ClassFromDict = FitConfig.from_dict(
      class_name='RestApiClient',
      client_name='rest_api',
      class_docstring='Awesome class generated with fitrequest.',
      base_url='https://test.skillcorner.fr',
      method_docstring='Calling endpoint: {endpoint}',
      method_config_list=[
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
      ],
  )

  client_from_dict = ClassFromDict()
