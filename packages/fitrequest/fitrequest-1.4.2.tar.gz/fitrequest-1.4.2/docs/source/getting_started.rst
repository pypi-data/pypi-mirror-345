Getting Started
===============

Installation
------------

To start using **fitrequest**, you need to install it first:

.. code-block:: bash

    pip install --upgrade fitrequest

How to Use It
-------------

**fitrequest** allows you to create your own api client.
To facilitate this, we provide several syntax options, see :ref:`Configuration Formats` section.

Below an simple example:

.. code-block:: python

  from fitrequest.client import FitRequest


  class RestApiClient(FitRequest):
      """Awesome class generated with fitrequest."""

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


  client = RestApiClient()


In this example there are 4 methods generated, 2 using the :ref:`MethodConfig`, a 2 using the :ref:`MethodConfigFamily`.
