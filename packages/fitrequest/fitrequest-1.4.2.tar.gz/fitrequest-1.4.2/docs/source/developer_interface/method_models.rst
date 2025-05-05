Method Models And Signatures
============================

Global variable for models
--------------------------

.. autodata:: fitrequest.method_models.environment_models

   .. hint:: Don't forget to update this dictionnary with custom models when using them in ``yaml/json`` files.


Models signatures
-----------------

.. autopydantic_model:: fitrequest.method_models.AttrSignature
.. autopydantic_model:: fitrequest.method_models.FlattenedModelSignature
