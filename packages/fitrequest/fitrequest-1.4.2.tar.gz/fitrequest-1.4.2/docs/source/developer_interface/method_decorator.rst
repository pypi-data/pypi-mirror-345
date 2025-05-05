Method Decorator Validation
===========================


ValidMethodDecorator
--------------------

.. py:type:: fitrequest.method_decorator.ValidMethodDecorator
   :canonical: Callable | str

   Annotated type used for validation, coercion, and serialization of decorators.


Globale variable for decorators
-------------------------------

.. autodata:: fitrequest.method_decorator.environment_decorators

   .. hint:: Don't forget to update this dictionnary with custom decorators when using them in ``yaml/json`` files.


ValidMethodDecorator validation
-------------------------------

.. autofunction:: fitrequest.method_decorator.eval_decorator_signature
.. autofunction:: fitrequest.method_decorator.validate_init_value
