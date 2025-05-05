Python Pydantic Configuration
"""""""""""""""""""""""""""""

This approach uses a Pydantic-oriented syntax to define the client's class.
While it is more verbose and enforces strict typing, it is the most flexible way to work with **fitrequest**.
All other variations are built upon this foundation, providing greater opportunities for customization.


.. code-block:: python

  from pathlib import Path
  from pydantic import Field
  from fitrequest.fit_var import ValidFitVar
  from fitrequest.fit_config import FitConfig
  from fitrequest.method_config import MethodConfig
  from fitrequest.method_config_family import MethodConfigFamily


  # Custom FitConfig
  class RestApiConfig(FitConfig):
      class_name: str = 'RestApiClient'
      class_docstring: str = 'Awesome class generated with fitrequest.'

      base_url: ValidFitVar = 'https://test.skillcorner.fr'
      client_name: str = 'rest_api'
      method_docstring: str = 'Calling endpoint: {endpoint}'

      method_config_list: list[MethodConfig | MethodConfigFamily] = Field(
          default_factory=lambda: [
              MethodConfigFamily(
                  base_name='items',
                  endpoint='/items/',
                  add_async_method=True,
              ),
              MethodConfig(
                  name='get_item',
                  endpoint='/items/{item_id}',
              ),
              MethodConfig(
                  name='get_item_details',
                  endpoint='/items/{item_id}/details/{detail_id}',
              ),
          ]
      )

  # New class created from FitConfig
  ClassDefault = RestApiConfig().fit_class
  ClassWithSpecificArgs = RestApiConfig(base_url='https://staging.skillcorner.fr:8080').fit_class

  # Client instances from generated classes
  client_default = ClassDefault()
  client_with_specific_args = ClassWithSpecificArgs()
