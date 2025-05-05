Authentication
==============

**fitrequest** provides flexible and powerful tools to handle authentication for HTTP requests.


Basic Authentication
""""""""""""""""""""

**fitrequest** supports Basic Authentication. The ``username`` and ``password`` fields are :ref:`FitVar` variables,
meaning their values can be retrieved from AWS Secrets Manager, system environment variables,
or directly provided during initialization.

.. note:: In the examples below, we use the :ref:`Pydantic syntax <Python Pydantic Configuration>` for typing clarity.
          However, you can use any of the other :ref:`available formats <Configuration Formats>`.

.. code-block:: python

  from fitrequest.aws_var import AWSSecretTypeEnum
  from fitrequest.fit_config import FitConfig
  from fitrequest.fit_var import FitVar
  from fitrequest.auth import Auth

  class RestApiClient(FitConfig):
      base_url: ValidFitVar = 'https://test.skillcorner.fr'
      client_name: str = 'rest_api'
      auth: Auth = Auth(
          username=FitVar(env_name="USERNAME"),
          password=FitVar(aws_path="/secret/path", aws_type=AWSSecretTypeEnum.secretsmanager)
      )


Header Token Authentication
"""""""""""""""""""""""""""

**fitrequest** supports token-based authentication by including the token in the request headers.
The token value is an ``FitVar`` variable. This method automatically sets the ``X-Authentication`` header with the provided token.

.. code-block:: python

  from fitrequest.fit_config import FitConfig
  from fitrequest.fit_var import FitVar
  from fitrequest.auth import Auth

  class RestApiClient(FitConfig):
      base_url: ValidFitVar = 'https://test.skillcorner.fr'
      client_name: str = 'rest_api'
      auth: Auth = Auth(header_token=FitVar(env_name="MY_PERSONAL_TOKEN"))


Params Token Authentication
"""""""""""""""""""""""""""

**fitrequest** also supports token-based authentication by including the token in the query parameters of the request.
The token value is an ``FitVar`` variable. This method adds a ``token`` field to the request parameters (e.g., ``www.example.com?token=1234``).

.. code-block:: python

  from fitrequest.fit_config import FitConfig
  from fitrequest.fit_var import FitVar
  from fitrequest.auth import Auth

  class RestApiClient(FitConfig):
      base_url: ValidFitVar = 'https://test.skillcorner.fr'
      client_name: str = 'rest_api'
      auth: Auth = Auth(param_token=FitVar(env_name="MY_PERSONAL_TOKEN"))


Custom Authentication
"""""""""""""""""""""

If the built-in authentication methods don’t meet your requirements, **fitrequest** allows you to define your own authentication mechanism.
You can use a `custom httpx authentication method <https://www.python-httpx.org/advanced/authentication/#custom-authentication-schemes>`_.

.. code-block:: python

  import httpx
  from fitrequest.fit_config import FitConfig
  from fitrequest.fit_var import ValidFitVar
  from fitrequest.auth import Auth

  class CustomAuth(httpx.Auth):
      # Define your custom authentication logic here

  class RestApiClient(FitConfig):
      base_url: ValidFitVar = 'https://test.skillcorner.fr'
      client_name: str = 'rest_api'
      auth: Auth = Auth(custom=CustomAuth())
