Pickling
--------

Python's `pickle <https://docs.python.org/3/library/pickle.html>`_ module relies on being able to import classes using
the fully-qualified name: `module_name.class_name`.
This means that any class must be defined in the module's global scope to be pickled successfully.


Classes dynamically generated (e.g., by ``FitConfig(...).fit_class`` or ``FitConfig.from_...``)
are *not* automatically registered in the global scope, which makes them unpicklable by default.

To fix this, you have two options:

1. Register the class in the global namespace manually:

   .. code-block:: python

    import sys
    setattr(sys.modules[__name__], 'MyClientClass', generated_class)

2. Or create a named subclass in the global scope:

   .. code-block:: python

     class MyClient(FitConfig(...).fit_class):
         pass


Either approach ensures the class has a stable, importable name that `pickle <https://docs.python.org/3/library/pickle.html>`_
can resolve when deserializing.

Or you can use an automated tools like `dill <https://pypi.org/project/dill/>`_
or `cloudpickle <https://pypi.org/project/cloudpickle/>`_, which are more forgiving in these scenarios.
