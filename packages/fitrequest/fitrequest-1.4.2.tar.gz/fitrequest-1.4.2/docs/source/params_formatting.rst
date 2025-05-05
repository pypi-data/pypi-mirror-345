Params Formatting
=================

There are different ways to deal with the url parameters in **fitrequest**.
Below we explore the different provided options and their pros and cons.


Kwargs
------

The **fitrequest** methods accept unknown keyword arguments (``kwargs``),
which are then passed to the ``httpx`` requests.
Therefore, the simplest approach is to use the params as unknown keyword arguments.

.. code-block:: python

  client.get_item(item_id=5, params={"lang":"en", "rformat":"json"})


The main disadvantage of this approach is that params are not included in the method's signature,
making it less clear which parameters the method accepts for the user.
Additionally, since params are not part of the method signature,
they are also not handled by the command-line interface (CLI) generation.


Endpoint template
-----------------

The parameters can also be added as part of the endpoint template.

.. code-block:: python

  class RestApiClient(FitRequest):
      client_name = 'rest_api'
      base_url = 'https://test.skillcorner.fr'

      method_config_list = [
          {
              'name': 'get_item',
              'endpoint': '/items/{item_id}?lang={lang}&rformat={rformat}'
          },
      ]

  client = RestApiClient()
  client.get_item(item_id=5, lang="en", rformat="json")


An advantage of this approach is that params are included in the method signature.
However, a drawback is that it requires all parameters to be provided in the final URL,
which means there is no way to declare default values. Parameters must always be specified.
Moreover, providing lists as parameters can be challenging.

This limitation can be partially addressed using the ``@fit`` decorator.


.. code-block:: python

  class RestApiClient(FitRequest):
      client_name = 'rest_api'
      base_url = 'https://test.skillcorner.fr'

      @fit(endpoint='/items/{item_id}?lang={lang}&rformat={rformat}')
      def get_item(self, item_id: str, lang: str , rformat: str = "json") -> Any: ...

  client = RestApiClient()
  client.get_item(item_id=5, lang="en")


Here, we have set a default value for the ``rformat`` parameter.

Using the ``@fit`` decorator requires defining parameters twice:
once in the endpoint template and again in the method signature.

On the other hand, it provides more expressive type annotations for the parameters.
For example, we can explicitly define possible choices for a parameter:


.. code-block:: python

  from typing import Literal

  class RestApiClient(FitRequest):
      client_name = 'rest_api'
      base_url = 'https://test.skillcorner.fr'

      @fit(endpoint='/items/{item_id}?lang={lang}&rformat={rformat}')
      def get_item(self, item_id: str, lang: Literal["en", "fr"] , rformat: Literal["json", "xml"] = "json") -> Any: ...


However, using this approach is exclusive to the ``@fit`` decorator format and cannot be applied to other formats.
Additionally, while the enhanced type annotations provide better documentation,
they do not offer any runtime validation - except for the generated CLI.


Params model
------------

**fitrequest** offers a solution to address the issues mentioned above.

:ref:`MethodConfig` and :ref:`MethodConfigFamily` fields include the ``params_model`` attribute,
which allows you to specify a Pydantic model representing the desired parameters.


.. code-block:: python

  from typing import Literal
  from pydantic import BaseModel

  class Params(BaseModel):
    lang: Literal["en", "fr"]
    rformat: Literal["json", "xml"] = "json"

  class RestApiClient(FitRequest):
      client_name = 'rest_api'
      base_url = 'https://test.skillcorner.fr'

      method_config_list = [
          {
              'name': 'get_item',
              'endpoint': '/items/{item_id}',
              'params_model': Params,
          },
      ]

  client = RestApiClient()
  client.get_item(item_id=5, lang="en", rformat="json")


This method offers several advantages:
it uses ``Pydantic`` for robust data validation, generates a complete method signature,
and effectively handles :py:meth:`nested Pydantic models <fitrequest.method_models.FlattenedModelSignature>`.

If data validation is not necessary, you can simply provide a list of parameter names to simplify the syntax:


.. code-block:: python

  class RestApiClient(FitRequest):
      client_name = 'rest_api'
      base_url = 'https://test.skillcorner.fr'

      method_config_list = [
          {
              'name': 'get_item',
              'endpoint': '/items/{item_id}',
              'params_model': ["lang", "rformat"],
          },
      ]

  client = RestApiClient()
  client.get_item(item_id=5, lang="en", rformat="json")


For the syntax using the ``@fit`` decorator,
the Pydantic model is inferred from parameters in the method signature that are not part of the endpoint variables
or the reserved **fitrequest** arguments (such as ``self``, ``raise_for_status``, and ``filepath``).


.. code-block:: python

  from typing import Literal

  class RestApiClient(FitRequest):
      client_name = 'rest_api'
      base_url = 'https://test.skillcorner.fr'

      @fit(endpoint='/items/{item_id}')
      def get_item(self, item_id: str, lang: Literal["en", "fr"] , rformat: Literal["json", "xml"] = "json") -> Any: ...

  client = RestApiClient()
  client.get_item(item_id=5, lang="en", rformat="json")


Pydantic models can also be specified in **YAML** or **JSON** files.
To ensure that these models are recognized, you should declare them in the ``environment_models`` variable.
This allows the loader to locate and use the desired models.


.. code-block:: yaml

  class_name: RestApiClient
  client_name: rest_api
  base_url: "https://test.skillcorner.fr"

  method_config_list:
    - name: "get_item"
      endpoint: "/items/{item_id}"
      params_model: "Params"


.. code-block:: python

  from fitrequest.method_models import environment_models

  environment_models.update(
      {
          'Params': Params,
          'UltraComplexParams': UltraComplexParams,
      }
  )


.. warning::

  The generated keyword arguments in the signature can be combined with the classic ``params`` field in ``kwargs``,
  using the following priority

  1. (Pydantic model) runtime method argument
  2. (``kwargs``) runtime ``params`` argument.

  But it is not recommended to mix statically declared parameters in the endpoint
  with either of the two methods described, as this can lead to unexpected behaviour.

  Also note that using :py:meth:`reserved words <fitrequest.utils.check_reserved_names>` as parameter names is not allowed.


Parameter Aliases
-----------------

You can assign alternative names (aliases) to parameters, allowing the parameter names in the method signature to differ from those used in the final URL.

**Example:**

.. code-block:: python

    @fit(endpoint='/items/{item_id}')
    def get_item(
        self,
        item_id: str,
        language: Literal["en", "fr"] = Field(alias="lang"),
        rformat: Literal["json", "xml"] = Field(alias="format", default="json")
    ) -> Any: ...

In this example:
  - The ``language`` parameter in the method maps to ``lang`` in the URL.
  - The ``rformat`` parameter maps to ``format`` in the URL and defaults to ``"json"``.

**Usage:**

.. code-block:: python

    # GET /items/1234?lang=fr&format=json
    client.get_item(1234, language="fr")

Here, ``language="fr"`` translates to ``lang=fr`` in the URL, and ``rformat`` is automatically set to ``"json"`` unless specified otherwise.


Default Factory for Parameters
------------------------------

You can use the ``default_factory`` attribute from Pydantic’s ``Field`` function to dynamically generate default values when the method is called.

**Example**

.. code-block:: python

    @fit(endpoint='/items/{item_id}')
    def get_item(
        self,
        item_id: str,
        date: datetime = Field(default_factory=lambda: datetime.now()),
    ) -> Any: ...


In this case, the ``date`` parameter will automatically be set to the current date and time whenever ``get_item`` is called, unless explicitly provided.
This ensures that dynamic values, such as timestamps, are set at the time of execution rather than when the function is defined.
