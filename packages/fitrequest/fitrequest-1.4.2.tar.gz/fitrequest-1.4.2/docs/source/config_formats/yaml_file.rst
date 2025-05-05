YAML Configuration File
"""""""""""""""""""""""

You can generate the **fitrequest** client class using a ``yaml`` configuration file.

.. code-block:: yaml

  ---
  class_name: RestApiClient
  client_name: rest_api
  class_docstring: 'Awesome class generated with FitRequest.'

  base_url: "https://test.skillcorner.fr"
  method_docstring: "Calling endpoint: {endpoint}"

  method_config_list:
    - base_name: items
      endpoint: "/items/"
      add_async_method: true

    - name: get_item
      endpoint: "/items/{item_id}"

    - name: get_item_details
      endpoint: "/items/{item_id}/details/{detail_id}"

.. code-block:: python

    # Python code
    ClassFromYaml = FitConfig.from_yaml(Path(__file__).parent / 'demo.yaml')
    client_from_yaml = ClassFromYaml()
