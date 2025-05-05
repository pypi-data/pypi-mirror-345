##########
ka_uts_dic
##########

Overview
********

.. start short_desc

**Dictionary 'Utilities'**

.. end short_desc

Installation
************

.. start installation

Package ``ka_uts_dic`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ka_uts_dic

To install with ``conda``:

.. code-block:: shell

	$ conda install -c conda-forge ka_uts_dic

.. end installation

Package logging
***************

c.f.: **Appendix: Package Logging**

Package files
*************

Classification
==============

The Files of Package ``ka_uts_log`` could be classified into the follwing file types:

#. *Special Python package files*. ==> **Appendix: Special python package files**
   a. *py.typed*

#. *Special Python package modules*

   a. *__init__.py*. ==> **Appendix: Python package Sub-directoriess**
   #. *__version__.py*

#. *Python package modules*    

   #. **Modules for dictionaries**

      a. **dic.py**

   #. **Modules for dictionaries of arrays**

      a. **doaod.py**
      #. **doa.py**

   #. **Modules for dictionaries of callables**

      a. **doc.py**

   #. **Modules for dictionaries of dataframes**
   
      a. **dopddf.py**
      #. **dopldf.py**

   #. **Modules for dictionaries of dictionaries**
   
      a. **dodoa.py**
      #. **dodoa.py**
      #. **dodod.py**
      #. **dodows.py**
      #. **dod.py**

   #. **Modules for dictionaries of objects**
   
      a. **doo.py**
   
Modules for Dictionaries
************************

  .. Management-Modules-for-Dictionary-label:
  .. table:: *Management Modules for Dictionary*

   +------+------------------------+
   |Name  |Description             |
   +======+========================+
   |dic.py|Management of Dictionary|
   +------+------------------------+

Module: dic.py
==============

Classes
-------

The Module ``dic.py`` contains the followinga static classes:

   +----+--------------------------+
   |Name|Description               |
   +====+==========================+
   |Arr |Management of Arrays      |
   +----+--------------------------+
   |Dic |Management of Dictionaries|
   +----+--------------------------+

Class: Arr
----------

The static Class ``Arr`` is used to manage Arrays used for flattening of dictionaries;
it contains the subsequent methods.

Arr Methods
^^^^^^^^^^^

  .. Arr-Methods-label:
  .. table:: *Arr Methods*

   +---------------------+------------------------------------------------------+
   |Name                 |Description                                           |
   +=====================+======================================================+
   |flatten_merge_to_aod |Type-dependent flattening of array elements to arrays |
   |                     |of dictionaries and merging of these arrays.          |
   +---------------------+------------------------------------------------------+
   |flattenx_keys        |show last key or concatinate keys with separator of   |
   |                     |flatten-dictionary if concatination is requested      |
   |                     |by given switch defined in flatten-dictionary.        |
   +---------------------+------------------------------------------------------+
   |flattenx_merge_to_aod|Type-dependent extended flattening of array elements  |
   |                     |to arrays of dictionaries and merging of these arrays.|
   +---------------------+------------------------------------------------------+

Class: Dic
----------

The static Class ``Dic`` is used to manage Dictionaries;
The Methods of Class ``Dic`` could be classified into the following method types:

#. *Flatten Methods*

Flatten Methods
^^^^^^^^^^^^^^^

  .. Flatten-Methods-of-class-Dic-label:
  .. table:: *Flatten Methods of class Dic*

   +------------------+-------------------------------------------------------------------+
   |Name              |Description                                                        |
   +==================+===================================================================+
   |flatten_to_aod    |Flatten dictionary to array of dictionaries                        |
   +------------------+-------------------------------------------------------------------+
   |flatten_using_d2p |Flatten dictionary nded flattening of array elements               |
   +------------------+-------------------------------------------------------------------+
   |flatten           |Flatten dictionary                                                 |
   +------------------+-------------------------------------------------------------------+
   |flattenx_to_aod   |Flatten dictionary in array of dictionaries in extended mode.      |
   +------------------+-------------------------------------------------------------------+
   |flattenx_using_d2p|Type-dependent extended flattening of array elements               |
   +------------------+-------------------------------------------------------------------+
   |flattenx          |Flatten dictionary in extended mode                                |
   +------------------+-------------------------------------------------------------------+

Appendix
********

Package Logging
===============

Description
-----------

The Standard or user specifig logging is carried out by the log.py module of the logging
package ka_uts_log using the configuration files **ka_std_log.yml** or **ka_usr_log.yml**
in the configuration directory **cfg** of the logging package **ka_uts_log**.
The Logging configuration of the logging package could be overriden by yaml files with
the same names in the configuration directory **cfg** of the application packages.

Log message types
-----------------

Logging defines log file path names for the following log message types: .

#. *debug*
#. *info*
#. *warning*
#. *error*
#. *critical*

Application parameter for logging
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  .. Application-parameter-used-in-log-naming-label:
  .. table:: *Application parameter used in log naming*

   +-----------------+--------------------------+-----------------+------------+
   |Name             |Decription                |Values           |Example     |
   |                 |                          +-----------------+            |
   |                 |                          |Value|Type       |            |
   +=================+==========================+=====+===========+============+
   |dir_dat          |Application data directory|     |Path       |/otev/data  |
   +-----------------+--------------------------+-----+-----------+------------+
   |tenant           |Application tenant name   |     |str        |UMH         |
   +-----------------+--------------------------+-----+-----------+------------+
   |package          |Application package name  |     |str        |otev_xls_srr|
   +-----------------+--------------------------+-----+-----------+------------+
   |cmd              |Application command       |     |str        |evupreg     |
   +-----------------+--------------------------+-----+-----------+------------+
   |pid              |Process ID                |     |str        |evupreg     |
   +-----------------+--------------------------+-----+-----------+------------+
   |log_ts_type      |Timestamp type used in    |ts   |Timestamp  |ts          |
   |                 |loggin files              +-----+-----------+------------+
   |                 |                          |dt   |Datetime   |            |
   +-----------------+--------------------------+-----+-----------+------------+
   |log_sw_single_dir|Enable single log         |True |Bool       |True        |
   |                 |directory or multiple     +-----+-----------+            |
   |                 |log directories           |False|Bool       |            |
   +-----------------+--------------------------+-----+-----------+------------+
   |log_sw_pid       |Enable display of pid     |True |Bool       |True        |
   |                 |in log file name          +-----+-----------+            |
   |                 |                          |False|Bool       |            |
   +-----------------+--------------------------+-----+-----------+------------+

Log type and Log directories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Single or multiple Application log directories can be used for each message type:

  .. Log-types-and-Log-directories-label:
  .. table:: *Log types and directoriesg*

   +--------------+---------------+
   |Log type      |Log directory  |
   +--------+-----+--------+------+
   |long    |short|multiple|single|
   +========+=====+========+======+
   |debug   |dbqs |dbqs    |logs  |
   +--------+-----+--------+------+
   |info    |infs |infs    |logs  |
   +--------+-----+--------+------+
   |warning |wrns |wrns    |logs  |
   +--------+-----+--------+------+
   |error   |errs |errs    |logs  |
   +--------+-----+--------+------+
   |critical|crts |crts    |logs  |
   +--------+-----+--------+------+

Log files naming
^^^^^^^^^^^^^^^^

Conventions
"""""""""""

  .. Naming-conventions-for-logging-file-paths-label:
  .. table:: *Naming conventions for logging file paths*

   +--------+-------------------------------------------------------+-------------------------+
   |Type    |Directory                                              |File                     |
   +========+=======================================================+=========================+
   |debug   |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |info    |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |warning |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |error   |/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+
   |critical|/<dir_dat>/<tenant>/RUN/<package>/<cmd>/<Log directory>|<Log type>_<ts>_<pid>.log|
   +--------+-------------------------------------------------------+-------------------------+

Examples (with log_ts_type = 'ts')
""""""""""""""""""""""""""""""""""

The examples use the following parameter values.

#. dir_dat = '/data/otev'
#. tenant = 'UMH'
#. package = 'otev_srr'
#. cmd = 'evupreg'
#. log_sw_single_dir = True
#. log_sw_pid = True
#. log_ts_type = 'ts'

  .. Naming-examples-for-logging-file-paths-label:
  .. table:: *Naming examples for logging file paths*

   +--------+----------------------------------------+------------------------+
   |Type    |Directory                               |File                    |
   +========+========================================+========================+
   |debug   |/data/otev/umh/RUN/otev_srr/evupreg/logs|debs_1737118199_9470.log|
   +--------+----------------------------------------+------------------------+
   |info    |/data/otev/umh/RUN/otev_srr/evupreg/logs|infs_1737118199_9470.log|
   +--------+----------------------------------------+------------------------+
   |warning |/data/otev/umh/RUN/otev_srr/evupreg/logs|wrns_1737118199_9470.log|
   +--------+----------------------------------------+------------------------+
   |error   |/data/otev/umh/RUN/otev_srr/evupreg/logs|errs_1737118199_9470.log|
   +--------+----------------------------------------+------------------------+
   |critical|/data/otev/umh/RUN/otev_srr/evupreg/logs|crts_1737118199_9470.log|
   +--------+----------------------------------------+------------------------+

Python Terminology
==================

Python package
--------------

Overview
^^^^^^^^

  .. Python package-label:
  .. table:: *Python package*

   +-----------+-----------------------------------------------------------------+
   |Name       |Definition                                                       |
   +===========+==========+======================================================+
   |Python     |Python packages are directories that contains the special module |
   |package    |``__init__.py`` and other modules, packages files or directories.|
   +-----------+-----------------------------------------------------------------+
   |Python     |Python sub-packages are python packages which are contained in   |
   |sub-package|another pyhon package.                                           |
   +-----------+-----------------------------------------------------------------+

Python package sub-directories
------------------------------

Overview
^^^^^^^^

  .. Python package sub-direcories-label:
  .. table:: *Python package sub-directories*

   +---------------------+----------------------------------------+
   |Name                 |Definition                              |
   +=====================+========================================+
   |Python               |directory contained in a python package.|
   |package sub-directory|                                        |
   +---------------------+----------------------------------------+
   |Special python       |Python package sub-directories with a   |
   |package sub-directory|special meaning like data or cfg.       |
   +---------------------+----------------------------------------+

Special python package sub-directories
--------------------------------------

Overview
^^^^^^^^

  .. Special-python-package-sub-directories-label:
  .. table:: *Special python sun-directories*

   +----+------------------------------------------+
   |Name|Description                               |
   +====+==========================================+
   |data|Directory for package data files.         |
   +----+------------------------------------------+
   |cfg |Directory for package configuration files.|
   +----+------------------------------------------+

Python package files
--------------------

Overview
^^^^^^^^

  .. Python-package-files-label:
  .. table:: *Python package files*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python        |File within a python package.                            |
   |package file  |                                                         |
   +--------------+---------------------------------------------------------+
   |Special python|Python package file which are not modules and used as    |
   |package file  |python marker files like ``__init__.py``.                |
   +--------------+---------------------------------------------------------+
   |Python        |File with suffix ``.py`` which could be empty or contain |
   |package module|python code; Other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |Special python|Python package module with special name and functionality|
   |package module|like ``main.py`` or ``__init__.py``.                     |
   +--------------+---------------------------------------------------------+

Special python package files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Overview
°°°°°°°°

  .. Special-python-package-files-label:
  .. table:: *Special python package files*

   +--------+--------+---------------------------------------------------------------+
   |Name    |Type    |Description                                                    |
   +========+========+===============================================================+
   |py.typed|Type    |The ``py.typed`` file is a marker file used in Python packages |
   |        |checking|to indicate that the package supports type checking. This is a |
   |        |marker  |part of the PEP 561 standard, which provides a standardized way|
   |        |file    |to package and distribute type information in Python.          |
   +--------+--------+---------------------------------------------------------------+

Special python package modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Overview
°°°°°°°°

  .. Special-Python-package-modules-label:
  .. table:: *Special Python package modules*

   +--------------+-----------+-----------------------------------------------------------------+
   |Name          |Type       |Description                                                      |
   +==============+===========+=================================================================+
   |__init__.py   |Package    |The dunder (double underscore) module ``__init__.py`` is used to |
   |              |directory  |execute initialisation code or mark the directory it contains as |
   |              |marker     |a package. The Module enforces explicit imports and thus clear   |
   |              |file       |namespace use and call them with the dot notation.               |
   +--------------+-----------+-----------------------------------------------------------------+
   |__main__.py   |entry point|The dunder module ``__main__.py`` serves as an entry point for   |
   |              |for the    |the package. The module is executed when the package is called by|
   |              |package    |the interpreter with the command **python -m <package name>**.   |
   +--------------+-----------+-----------------------------------------------------------------+
   |__version__.py|Version    |The dunder module ``__version__.py`` consist of assignment       |
   |              |file       |statements used in Versioning.                                   |
   +--------------+-----------+-----------------------------------------------------------------+

Python elements
---------------

Overview
°°°°°°°°

  .. Python elements-label:
  .. table:: *Python elements*

   +-------------------+---------------------------------------------+
   |Name               |Definition                                   |
   +===================+=============================================+
   |Python method      |Function defined in a python module.         |
   +-------------------+---------------------------------------------+
   |Special            |Python method with special name and          |
   |python method      |functionality like ``init``.                 |
   +-------------------+---------------------------------------------+
   |Python class       |Python classes are defined in python modules.|
   +-------------------+---------------------------------------------+
   |Python class method|Python method defined in a python class.     |
   +-------------------+---------------------------------------------+
   |Special            |Python class method with special name and    |
   |Python class method|functionality like ``init``.                 |
   +-------------------+---------------------------------------------+

Special python methods
^^^^^^^^^^^^^^^^^^^^^^

Overview
°°°°°°°°

  .. Special-python-methods-label:
  .. table:: *Special python methods*

   +--------+------------+----------------------------------------------------------+
   |Name    |Type        |Description                                               |
   +========+============+==========================================================+
   |__init__|class object|The special method ``__init__`` is called when an instance|
   |        |constructor |(object) of a class is created; instance attributes can be|
   |        |method      |defined and initalized in the method.                     |
   +--------+------------+----------------------------------------------------------+

Table of Contents
=================

.. contents:: **Table of Content**
