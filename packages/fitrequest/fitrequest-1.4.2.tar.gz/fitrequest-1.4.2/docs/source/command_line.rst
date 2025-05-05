Command Line
============

The **fitrequest** tool automatically generates a command-line interface (CLI) based on the methods it creates.
Each class includes a ``cli_run`` method that launches a `Typer <https://typer.tiangolo.com/>`_ application containing all the generated methods from fitrequest.
This setup ensures that configuration validation and authentication are seamlessly handled.

Additionally, the output is formatted using the `rich library <https://rich.readthedocs.io/en/stable/introduction.html>`_,
which enhances readability with color-coding.
This feature makes it straightforward to test the generated requests quickly and efficiently.

To utilize the CLI tool, simply add the ``cli_run`` function as a console script in your project's pyproject.toml file, as demonstrated below.


.. note::
  When the ``kwargs`` argument is included in the method signature, some ``httpx.request`` arguments are added and made available as options.


.. code-block:: toml

  [project.scripts]
  restapi-cli = "tests.demo_lazy_config_request_params:RestApiClient.cli_run"


Below some examples of output:


.. code-block:: bash

  restapi-cli --help

.. image:: images/restapi-cli.png



.. code-block:: bash

  restapi-cli get-item --help

.. image:: images/restapi-cli-get-item.png



.. code-block:: bash

  restapi-cli get-items --help

.. image:: images/restapi-cli-get-items.png
