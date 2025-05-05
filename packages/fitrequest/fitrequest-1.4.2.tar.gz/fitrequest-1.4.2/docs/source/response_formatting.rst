Response Formatting
===================

When handling data, the response format is automatically determined based on the content type specified in the header.
Currently, two formats are supported: *JSON/JSONLines* and *XML*.

**XML Format**:
When the content type is *XML*, fitrequest returns an ``Element`` object from the ``xml.etree.ElementTree`` module.
This allows you to work with the *XML* data using standard *XML* parsing techniques.


**JSON/JSONLines Format**:
For *JSON* or *JSONLines* responses, **fitrequest** provides a Python dictionary or list structure,
making it easy to manipulate and access data programmatically.


**Data Extraction with Jsonpath**:
You can use ``jsonpath`` (a query language for *JSON*) to extract specific information from your *JSON* response.
This tool is available via the package `jsonpath-ng <https://pypi.org/project/jsonpath-ng/>`_.


**Pydantic Models Integration**:
To add structure and validation to your *JSON* responses, fitrequest supports Pydantic models.
By defining a ``response_model`` in your :ref:`MethodConfig` or :ref:`MethodConfigFamily`,
you can ensure that the response conforms to a predefined schema.

.. note:: The use of Pydantic models is exclusive to *JSON/JSONLines* responses.
          The model should be specified as either a single instance of ``<PydanticModel>`` or as a list,
          such as ``list[<PydanticModel>]``, to handle multiple items.


In the following example, we utilize the :ref:`@fit decorator <Python @fit Decorator>`,
and the data model is automatically identified based on the function's return type.

.. literalinclude:: ../../tests/demo_decorator_pydantic_return.py
  :language: python


This structured approach ensures clarity and ease of understanding for developers working with different data formats and validation.
For more details, check the ``ResponseFormatter`` :ref:`documentation <ResponseFormatter>`.


Pydantic models can also be specified in **YAML** or **JSON** files.
To ensure that these models are recognized, you should declare them in the ``environment_models`` variable.
This allows the loader to locate and use the desired models.


.. code-block:: yaml

  class_name: RestApiClient
  client_name: rest_api
  class_docstring: 'Awesome class generated with fitrequest.'

  base_url: "https://test.skillcorner.fr"
  method_docstring: "Calling endpoint: {endpoint}"

  method_config_list:
    - base_name: "items"
      endpoint: "/items/"
      add_async_method: true
      response_model: "Item"
      json_path: "[*].items"

    - name: "get_item"
      endpoint: "/items/{item_id}"
      response_model: "Item"
      decorators: ["retry(max_retries=3, on_status='500-600')"]

    - name: "get_item_details"
      endpoint: "/items/{item_id}/details/{detail_id}"
      response_model: "ItemDetails"
      decorators: ["retry(max_retries=2, on_status='507')"]



.. code-block:: python

  from fitrequest.method_models import environment_models

  environment_models.update(
      {
          'Items': Items,
          'ItemDetails': ItemDetails,
      }
  )
