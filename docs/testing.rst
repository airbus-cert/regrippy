Writing tests for your plugins
==============================

In order to make sure your plugins don't break when there is an architectural change in the 
core of the program, or to allow you some peace of mind when upgrading them, it is highly
recommended to write tests.

We use the pytest_ library for all tests. Each plugin should have a corresponding 
`test_[plugin].py` in the `tests/` directory.

In order to not have to create your own hives when testing your plugins, we have developed 
classes mocking all classes from python-registry. You can build a fake registry tree using these
and pass it to your plugin constructor.

.. literalinclude:: ../tests/test_rdphint.py

.. _pytest: https://pytest.org

.. class:: reg_mock.RegistryMock

   Mocks the `Registry.Registry` class.

   :param hive_name: the "internal name" of the hive
   :type hive_name: str
   :param hive_type: the type of the hive. Usually a standard hive name in lowercase
   :type hive_type: str
   :param root: the root key. Use :meth:`~reg_mock.RegistryKeyMock.root` to get it.
   :type root: reg_mock.RegistryKeyMock

   .. method:: hive_type()

      :rtype: str

   .. method:: hive_name()

      :rtype: str

   .. method:: root()

      Returns the root key

      :returns: this hive's root key
      :rtype: reg_mock.RegistryKeyMock

   .. method:: open(path)
      
      Opens a child key.

      :param path: the path to the child key
      :type path: str

      :returns: the child key.
      :rtype: reg_mock.RegistryKeyMock
      :raises RegistryKeyNotFoundException: if the key doesn't exist

   .. method:: set_ccs(number)

      Helper function to create the `Select` key which determines which `ControlSet00X` key to open.

      :param number: the current ControlSet number
      :type number: int

.. class:: reg_mock.RegistryKeyMock
   
   Mocks the `Registry.RegistryKey` class.

   :param name: the name of the key
   :type name: str
   :param parent: the parent key. If `None`, this means this key is the root key.
   :type parent: reg_mock.RegistryKeyMock

   .. staticmethod:: build(path)

      Build the set of keys forming the given `path`.

      :param path: the path to the leaf key
      :type path: str

      :returns: the leaf key within the there
      :rtype: reg_mock.RegistryKeyMock
    
   .. method:: root()
      
      Find the top-most key accessible from this key.

      :returns: the root key of the hive
      :rtype: reg_mock.RegistryKeyMock

   .. method:: open(path)
      
      Opens a child key.

      :param path: the path to the child key
      :type path: str

      :returns: the child key.
      :rtype: reg_mock.RegistryKeyMock
      :raises RegistryKeyNotFoundException: if the key doesn't exist
    
   .. method:: add_child(key)

      Add a child key to this key.

      :param key: The child key to add. Make sure you correctly set its :attr:`~reg_mock.RegistryKeyMock.parent` attribute.
      :type key: reg_mock.RegistryKeyMock
   
   .. method:: add_value(value)

      Add a value to this key.

      :param value: the value to add.
      :type value: reg_mock.RegistryValueMock

   .. method:: path()
   .. method:: subkeys()
   .. method:: values()
   .. method:: name()
   .. method:: value(name)

.. class:: reg_mock.RegistryValueMock
   
   Mocks the `Registry.RegistryValue` class.

   :param name: the value name
   :type name: str
   :param data: the data contained in this value
   :type data: variable
   :param type: the data type
   :type type: Registry.[RegSZ, RegDWord, ...]

   .. method:: name()
   .. method:: value()
   .. method:: value_type()
   .. method:: value_type_str()