JSON Configuration File
"""""""""""""""""""""""

You can generate the **fitrequest** client class using a ``json`` configuration file.

.. code-block:: json

  {
    "base_url": "https://test.skillcorner.fr",
    "class_docstring": "Awesome class generated with fitrequest.",
    "class_name": "RestApiClient",
    "client_name": "rest_api",
    "method_config_list": [
      {
        "add_async_method": true,
        "base_name": "items",
        "endpoint": "/items/"
      },
      {
        "endpoint": "/items/{item_id}",
        "name": "get_item"
      },
      {
        "endpoint": "/items/{item_id}/details/{detail_id}",
        "name": "get_item_details"
      }
    ],
    "method_docstring": "Calling endpoint: {endpoint}"
  }

.. code-block:: python

    # Python code
    ClassFromJson = FitConfig.from_json(Path(__file__).parent / 'demo.json')
    client_from_json = ClassFromJson()
