Creating a plugin
=================

A RegRippy plugin consists of one basic component:

.. py:data:: Plugin
   
   A class inheriting from :class:`~regrippy.BasePlugin` and implementing the 
   :meth:`~regrippy.BasePlugin.run` method. It should either return a `list` of 
   :class:`~regrippy.PluginResult` or `yield` them.

   This class needs to have a :data:`~regrippy.BasePlugin.__REGHIVE__` class-level attribute 
   specifying whichi hive(s) your plugin uses.

   Do not hesitate to override the :meth:`~regrippy.BasePlugin.display_human` and 
   :meth:`~regrippy.BasePlugin.display_machine` methods if they do not fit your needs.

As an example, here is the `run.py` plugin, which lists programs running at startup.
It is especially interesting because it has a different behaviour depending on the hive it is
currently analysing.

.. literalinclude:: ../regrippy/plugins/run.py
    :caption: run.py