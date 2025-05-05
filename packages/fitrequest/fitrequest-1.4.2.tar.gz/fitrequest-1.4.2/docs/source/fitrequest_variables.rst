FitRequest Variables (FitVar)
=============================

**fitrequest** simplifies managing configuration values by using the ``FitVar`` type for some variables.
These variables can have their values sourced from one or more of the following, with priority as outlined below:

1. **Provided Initialization Value**: Explicitly set when creating the variable.
2. **System Environment Variables**: Pulled from the system's environment.
3. **AWS**: Retrieved from AWS Secrets Manager or Parameter Store.


Key Features:

- **fitrequest** provides built-in support for ``base_url`` and most ``Auth`` attributes as ``FitVar`` variables.
- The ``ValidFitVar`` type acts as an alias for ``FitVar | str | None``, adding validation to allow seamless transformation of string declarations into ``FitVar`` objects.


Here are some examples demonstrating different ways to define ``base_url`` using ``FitVar``:

.. note:: In the examples below, we use the :ref:`Pydantic syntax <Python Pydantic Configuration>` for typing clarity.
          However, you can use any of the other :ref:`available formats <Configuration Formats>`.


Simple Initialization
---------------------

.. code-block:: python

  from fitrequest.fit_config import FitConfig
  from fitrequest.fit_var import ValidFitVar

  class RestApiClient(FitConfig):
      client_name: str = 'rest_api'
      base_url: ValidFitVar = 'https://test.skillcorner.fr'


This is equivalent to:


.. code-block:: python

  from fitrequest.fit_config import FitConfig
  from fitrequest.fit_var import FitVar

  class RestApiClient(FitConfig):
      client_name: str = 'rest_api'
      base_url: ValidFitVar = FitVar(init_value='https://test.skillcorner.fr')


Value from AWS
--------------

.. code-block:: python

  from fitrequest.fit_config import FitConfig
  from fitrequest.fit_var import FitVar

  class RestApiClient(FitConfig):
      client_name: str = 'rest_api'
      base_url: ValidFitVar = FitVar(aws_path="awesome/path/to/variable")


Value from System Environment Variables
---------------------------------------

.. code-block:: python

  from fitrequest.fit_config import FitConfig
  from fitrequest.fit_var import FitVar

  class RestApiClient(FitConfig):
      client_name: str = 'rest_api'
      base_url: ValidFitVar = FitVar(env_name="REST_API_AWESOME_CLIENT_BASE_URL")


Multiple Sources with Fallback Priority
---------------------------------------

.. code-block:: python

  from fitrequest.fit_config import FitConfig
  from fitrequest.fit_var import FitVar

  class RestApiClient(FitConfig):
      client_name: str = 'rest_api'
      base_url: ValidFitVar = FitVar(
          aws_path="awesome/path/to/variable",
          init_value=some_variable_that_can_be_none,
          env_name="REST_API_AWESOME_CLIENT_BASE_URL"
      )


As stated above, the init value will be used first.
If it's ``None``, the provided environment variable will be used. Otherwise, the AWS value will be retrieved.
