CLI Config
==========

*Build your experiment configurations for complex projects with robustness, flexibility and simplicity*

|

.. image:: _static/logo_extend.png
  :align: center
  :width: 1000
  :alt: CLI config logo

|

*CLI Config*: Lightweight library that provides routines to merge nested configs
and set parameters from command line. It is also provide processing functions
that can change the whole configuration before and after each config merge, config
saving, config loading and at the end of config building. It also contains many
routines to manipulate the config as flatten or nested dictionaries.

The package is initially designed for machine learning experiments where the
number of parameters is huge and a lot of them have to be set by the user between
each experiment. If your project matches this description, this package is for you!

`Pypi project <https://pypi.org/project/cliconfig/>`_

`Github project <https://github.com/valentingol/cliconfig>`_


|PyPI version| |PythonVersion| |License| |Waka_Time|

|Ruff_logo| |Black_logo|

|Ruff| |Flake8| |Pydocstyle| |MyPy| |PyLint|

|Tests| |Coverage| |Documentation Status|

Official badge:
|Config|

Make default config yaml file(s) in your project (configs are merged from left to right):

.. code:: python

   # main.py
   from cliconfig import make_config

   config = make_config('default1.yaml', 'default2.yaml')

Then launch your script with additional config(s) file(s) and parameters by command line.
The additional configs are merged on the default one's then the parameters are set.

.. code:: bash

   python main.py --config first.yaml,second.yaml --param1=1 --subconfig.param2='foo'

**By default, these additional configs cannot add new parameters to the default config
(for security and retro-compatibility reasons).**

Now you can get your configuration parameters in your script:

.. code:: python

   # Nested config dict as a native python dict
   config.dict
   # Get a parameter value (you can also set it or delete it)
   config.foo1.foo2.bar

You can also load and save configs with `cliconfig.save_config` and `cliconfig.load_config`.

With processing
---------------

The library provides powerful tools to modify the configuration called "processings".
One of the possibility they add is to merge multiple configurations,
copy a parameter on another, enforce type and more. To do so, simply adding the
corresponding tags to your parameter names (on config files or CLI parameters).

For instance with these config files:

.. code:: yaml

    # main.yaml
    path_1@merge_add: sub1.yaml
    path_2@merge_add: sub2.yaml
    config3.select@select: config3.param1

    # sub1.yaml
    config1:
      param@copy@type:int: config2.param
      param2@type:None|int: 1

    # sub2.yaml
    config2.param@type:int: 2
    config3:
      param1@def: "[(config1.param2 + config2.param) / 2] * 2 if config2.param else None"
      param2: 1

Note that can also use YAML tags separated with "@" (like `key: !tag@tag2 value`)
to add tags instead of putting them in the parameter name (like `key@tag@tag2: value`).

Here `main.yaml` will be interpreted like:

.. code:: yaml

    path_1: sub1.yaml
    path_2: sub2.yaml
    config1:
      param: 2  # the value of config2.param
      param2: 1
    config2:
      param: 2
    config3:
      select: config3.param1
      param1: [1.5, 1.5]
      # param2 is deleted because it is not in the selection

Then, all the parameters in `config1` and `config2` have enforced types
(`config2.param` can also be None) and changing `config2.param` will also update
`config1.param` accordingly (which is protected by direct update).

The default tags include:

* `@merge_add`, `@merge_before`, and `@merge_after`: These tags merge the dictionary
  loaded from the specified value (which should be a YAML path) into the current
  configuration. `@merge_add` allows only the merging of new keys and is useful for
  splitting non-overlapping sub-configurations into multiple files. `@merge_before` merges
  the current dictionary onto the loaded one, while `@merge_after` merges the loaded
  dictionary onto the current one. These tags are used to organize the config files simply.
* `@copy`: This tag copies a parameter from another key. The value should be a string
  that represents the flattened key. The copied value is then protected from further
  updates but will be updated if the copied key change during a merge.
* `@def`: This tag evaluate an expression to define the parameter value.
  The value associated to a parameter tagged with `@def` can contain any
  parameter name of the configuration. The most useful operators and built-in
  functions are supported, the random and math packages are also supported
  as well as some (safe) numpy, jax, tensorflow, pytorch functions.
  If/else statements and comprehension lists are also supported.
* `@type:<my type>`: This tag checks if the key matches the specified type `<my type>`
  after each update, even if the tag is no longer present. It tries to convert
  the type if it is not the good one. It supports basic types
  (except for tuples and sets, which are not handled by YAML) as well as unions
  (using "Union" or "|"), optional values, nested list, and nested dict.
  For instance: `@type:List[Dict[str, int|float]]`.
* `@select`: This tag select sub-config(s) to keep and delete the other
  sub-configs in the same parent config. The tagged key is not deleted if it is
  in the parent config.
* `@delete`: This tag deletes the key from the config before merging.
* `@new`: This tag allows adding new key(s) to the config that are not already
  present in the default config(s). It can be used for single parameter or a
  sub-config. Disclaimer: it is preferable to have exhaustive default config(s)
  instead of abusing this tag for readability and for security concerning typos.
* `@dict`: This tag allows to have a dictionary object instead of a sub-config
  where you can modify the keys (see the
  [*Edge cases*](https://cliconfig.readthedocs.io/en/latest/edge_cases.html) section)

See *Quickstart* section of the documentation for more details and
*Processing* section for advanced usage.

.. |PyPI version| image:: https://img.shields.io/github/v/tag/valentingol/cliconfig?label=Pypi&logo=pypi&logoColor=yellow
   :target: https://pypi.org/project/cliconfig/
.. |PythonVersion| image:: https://img.shields.io/badge/Python-3.7%20%7E%203.11-informational
.. |License| image:: https://img.shields.io/github/license/valentingol/cliconfig?color=999
   :target: https://stringfixer.com/fr/MIT_license
.. |Waka_Time| image:: https://wakatime.com/badge/github/valentingol/cliconfig.svg
    :target: https://wakatime.com/badge/github/valentingol/cliconfig
.. |Ruff_logo| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json
   :target: https://github.com/charliermarsh/ruff
.. |Black_logo| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
.. |Ruff| image:: https://github.com/valentingol/cliconfig/actions/workflows/ruff.yaml/badge.svg
   :target: https://github.com/valentingol/cliconfig/actions/workflows/ruff.yaml
.. |Flake8| image:: https://github.com/valentingol/cliconfig/actions/workflows/flake.yaml/badge.svg
   :target: https://github.com/valentingol/cliconfig/actions/workflows/flake.yaml
.. |Pydocstyle| image:: https://github.com/valentingol/cliconfig/actions/workflows/pydocstyle.yaml/badge.svg
   :target: https://github.com/valentingol/cliconfig/actions/workflows/pydocstyle.yaml
.. |MyPy| image:: https://github.com/valentingol/cliconfig/actions/workflows/mypy.yaml/badge.svg
   :target: https://github.com/valentingol/cliconfig/actions/workflows/mypy.yaml
.. |PyLint| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/valentingol/ab12676c87f0eaa715bef0f8ad31a604/raw/cliconfig_pylint.json
   :target: https://github.com/valentingol/cliconfig/actions/workflows/pylint.yaml
.. |Tests| image:: https://github.com/valentingol/cliconfig/actions/workflows/tests.yaml/badge.svg
   :target: https://github.com/valentingol/cliconfig/actions/workflows/tests.yaml
.. |Coverage| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/valentingol/098e9c7c53be88779ee52ef2f2bc8803/raw/cliconfig_tests.json
   :target: https://github.com/valentingol/cliconfig/actions/workflows/tests.yaml
.. |Documentation Status| image:: https://readthedocs.org/projects/cliconfig/badge/?version=latest
   :target: https://cliconfig.readthedocs.io/en/latest/?badge=latest
.. |Config| image:: https://custom-icon-badges.demolab.com/badge/cliconfig-black?logo=cliconfig
    :target: https://github.com/valentingol/cliconfig
