CLI Config API
==============

The submodules are listed below. For a short summary:

* :mod:`config_routines` - routines for creating, loading, saving, updating, copying,
  ... configuration files (using YAML files and CLI if needed)
* :mod:`processing` - processing classes to bring more features to the
  configuration building process. Contains the default processings (@merge_add, @copy, ...)
* :mod:`process_routines` - operation functions on configuration that trigger processings
* :mod:`dict_routines` - operation functions on python native dictionaries
* :mod:`tag_routines` - operation functions on tags names (like `param@tag@tag2`).
* :mod:`cli_parser` - CLI parser for building configuration from command line arguments
* :mod:`base` - base class of configuration objects

Contents:

.. toctree::
   :maxdepth: 3

   config_routines
   processing/main
   process_routines
   dict_routines
   tag_routines
   cli_parser
   base
