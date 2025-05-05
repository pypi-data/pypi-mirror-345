Welcome to FitRequest
=====================

Overview
--------

**fitrequest** is a Python library designed to simplify the creation of REST API clients by automating code generation.
It enables developers to generate both synchronous and asynchronous methods for interacting with REST APIs,
handle response formatting, and manage authentication seamlessly.


Key Features
------------

What This Module Does
"""""""""""""""""""""

- **Easy Synchronous and Asynchronous Code Generation**

  Quickly create methods to interact with REST endpoints.


- **Response Formatting**

  Automatically handle JSON and XML responses, support JSONPath exploration and Pydantic formatting for JSON responses.


- **Docstring Templating**

  Generate meaningful docstrings for each method using `Jinja templates <https://jinja.palletsprojects.com/en/stable/>`_.


- **Basic Authentication**

  Support basic authentication using environment variables or AWS secrets.


- **FitRequest Variable Management**

  Easily retrieve data from AWS, system environment variables, or set default values.


- **Argument Generation**

  Automatically generate method arguments based on endpoint variables.


- **Decorator handling**

  Easily enhance generated fitrequest methods with custom decorators.


- **Retry Behavior**

  A ``@retry`` decorator is provided to allow user to implement basic retry logic.


- **Rich syntax options**

  Several syntax options provided that can be tailored to your needs and preferences.


- **Auto-generated CLI**


  An out-of-the-box CLI is provided with fitrequest classes to easily test methods from a terminal.



What This Module Doesn't Do
"""""""""""""""""""""""""""

- **Handle OpenApi**

  Generate python clients from *OpenAPI* documents. This may be a future feature.


- **Complex Authentication**

  For complex authentication, use a custom HTTPX Authentication method or directly provide the `auth` argument to the generated method.


- **Multiple Request Methods**

  Generates only one method per endpoint.


- **XML/HTML Parsing**

  Limited support for extracting data from XML and HTML.


- **Streaming Handling**

  Does not handle streaming requests/responses. This may be a future feature.


Useful Links
""""""""""""

* **Code**: `fitrequest GitLab <https://gitlab.com/public-corner/fitrequest/>`_
* **Pypi**: `fitrequest PyPI <https://pypi.org/project/fitrequest/>`_



Contents
--------

.. toctree::
   :maxdepth: 3
   :titlesonly:

   getting_started
   fitrequest_variables
   authentication
   session
   config_formats/index
   response_formatting
   params_formatting
   command_line
   pickling
   examples
   developer_interface/index
