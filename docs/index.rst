CLI Config
==========

|

.. image:: _static/logo_extend.png
  :align: center
  :width: 1000
  :alt: CLI config logo

|

*CLI Config*: Lightweight library that provides routines to merge nested and flat configs
and set parameters from command line. It is also provide processing functions
that can change the whole configuration before and after each config merge, config
saving and config loading. It also contains many routines to manipulate
the config as flatten or nested dicts.

|PyPI version| |PythonVersion| |License|

|Ruff_logo| |Black_logo|

|Ruff| |Flake8| |Pydocstyle| |MyPy| |PyLint|

|Tests| |Coverage| |Documentation Status|

Make a default config file in your project (configs are merged from left to right):

.. code:: python

   # main.py
   from cliconfig import make_config

   config, _ = make_config('default1.yaml', 'default2.yaml')  # it's a dict

Then launch your script with additional config(s) file(s) and parameters.
By default, these additional configs cannot add new parameters to the default config
(for security and retro-compatibility reasons).

.. code:: bash

   python main.py --config first.yaml,second.yaml --param1=1 --subconfig.param2='foo'

See *Quickstart* section for more details and *Processing* section for advanced usage.

.. |PyPI version| image:: https://img.shields.io/github/v/tag/valentingol/cliconfig?label=Pypi&logo=pypi&logoColor=yellow
   :target: https://pypi.org/project/cliconfig/
.. |PythonVersion| image:: https://img.shields.io/badge/Python-3.7%20%7E%203.11-informational
.. |License| image:: https://img.shields.io/github/license/valentingol/cliconfig?color=999
   :target: https://stringfixer.com/fr/MIT_license
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

.. toctree::
   :maxdepth: 4
   :caption: Contents:

   installation
   quickstart
   edge_cases
   processing
   cliconfig_api
   contribute
   license
