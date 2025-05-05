##########
ka_uts_xls
##########

Overview
********

.. start short_desc

**Excel 'Utilities'**

.. end short_desc

.. start long_desc

**The package ka_uts_xls ís a collection of interface modules to the following 'Python Excel Utilities'**

.. end long_desc

#. *openpyxl*
#. *pyexcelerate*
#. *pandas dataframe excel functions*
#. *polars dataframe excel functions*

Installation
************

.. start installation

The package ``ka_uts_xls`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ka_uts_xls

To install with ``conda``:

.. code-block:: shell

	$ conda install -c conda-forge ka_uts_xls

.. end installation

Package files
*************

Classification
==============

The Files of Package ``ka_uts_xls`` could be classified into the following file types:

#. *Special files*
#. *Dunder modules*
#. *Package modules*
#. *Data files*

Modules
*******

Overview
========

The Modules of Package ``ka_uts_xls`` could be classified into the 
following module file types:

#. **I/O modules**

   a. *I/O Control module*
   #. *I/O Input modules*
   #. *I/O Output modules*
   #. *I/O Update modules*

#. **Workbook modules**

   a. *Workbook modules using openpyxl*
   #. *Workbook modules using pyexcelerate*

#. **Worksheet modules**

#. **Cell (Row) modules**


I/O Control Module
******************

Overview
========

  .. I/O-Control-Module-label:
  .. table:: *I/O Control Module*

   +------+--------------------------------------+
   |Name  |Description                           |
   +======+======================================+
   |ioc.py|I/O Control processing for excel files|
   +------+--------------------------------------+

ioc.py
======

Static classes
--------------

The I/O Control Module ``ioc.py`` contains the following static classes.

  .. Static-classes-of-I/O-Control-module-ioc.py-label:
  .. table:: *Static Classes of I/O Control Module ioc.py*

   +-------+-----------------------------------------------------------------+
   |Name   |Description                                                      |
   +=======+=================================================================+
   |IocWbOp|Manage I/O control for excel workbooks using openpyxl package    |
   +-------+-----------------------------------------------------------------+
   |IocWbPe|Manage I/O control for excel workbooks using pyexcelerate package|
   +-------+-----------------------------------------------------------------+

IocWbOp
-------

Methods
^^^^^^^

  .. Methods-of-static-class-IocWbOp-label:
  .. table:: *Methods of static class IocWbOp Com*

   +----+----------------------------------------+
   |Name|Description                             |
   +====+========================================+
   |get |get Workbook using the openpyxel package|
   +----+----------------------------------------+

get
^^^

  .. Parameter-of-IocWbOp-method-get-label:
  .. table:: *Parameter of Com method sh_kwargs*

   +---------+-----+--------------------+
   |Name     |Type |Description         |
   +=========+=====+====================+
   |\**kwargs|TyAny|current class       |
   +---------+-----+--------------------+

  .. Return-value-of-IocWPep-method-get-label:
  .. table:: *Return value of IocWbPe method get*

   +----+------+---------------------+
   |Name|Type  |Description          |
   +====+======+=====================+
   |    |TyWbpP|pyexcelerate Workbook|
   +----+------+---------------------+

IocWbPe
-------

Methods
^^^^^^^

  .. Methods-of-static-class-IocWbPe-label:
  .. table:: *Methods of static class IocWbPe Com*

   +----+-------------------------------------------+
   |Name|Description                                |
   +====+===========================================+
   |get |get Workbook using the pyexcelerate package|
   +----+-------------------------------------------+

get
^^^

  .. Parameter-of-static-class-IocWbPe-method-get-label:
  .. table:: *Parameter of.static.class.IocWbPe.method.get*

   +---------+-----+--------------------+
   |Name     |Type |Description         |
   +=========+=====+====================+
   |\**kwargs|TyAny|current class       |
   +---------+-----+--------------------+

  .. Return-value-of-IocWbPe-method-get-label:
  .. table:: *Return value of IocWbPe method get*

   +----+------+---------------------+
   |Name|Type  |Description          |
   +====+======+=====================+
   |    |TyWbPe|pyexcelerate Workbook|
   +----+------+---------------------+

Input I/O Modules
*****************

Overview
========

  .. Input I/O-Modules-label:
  .. table:: *Input I/O Modules*

   +------------+-------------------------------------------------------+
   |Name        |Description                                            |
   +============+=======================================================+
   |ioipath.py  |Run Input I/O for excel workbooks accessed by path     |
   +------------+-------------------------------------------------------+
   |ioipathnm.py|Run Input I/O for excel workbooks accessed by path name|
   +------------+-------------------------------------------------------+

ioipath.py
==========

Static classes
--------------

The Input I/O Module ``ioipath.py`` contains the following static classes.

  .. Static-classes-of-Input-I/O-module-ioipath.py-label:
  .. table:: *Static Classes of Input I/O Module ioipath.py*

   +-----------+----------------------------------------+
   |Name       |Description                             |
   +===========+========================================+
   |IoiPathWbPd|Run Input I/O for excel workbooks       |
   |           |accessed by path using pandas package   |
   +-----------+----------------------------------------+
   |IoiPathWbPl|Run Input I/O for excel workbooks       |
   |           |accessed by path using polaris package  |
   +-----------+----------------------------------------+
   |IoiPathWbOp|Run Input I/O for excel workbooks       |
   |           |accessed by path using openpyxel package|
   +-----------+----------------------------------------+
   |IoiPathWsOp|Run Input I/O for excel worksheets      |
   |           |accessed by path using openpyxel package|
   +-----------+----------------------------------------+

ioipathnm.py
============

Static classes
--------------

The I/O Input Module ``ioipathnm.py`` contains the following static classes.

  .. Static-classes-of-I/O-Input-module-ioipathnm.py-label:
  .. table:: *Static Classes of I/O Input Module ioipathnm.py*

   +-------------+---------------------------------------------+
   |Name         |Description                                  |
   +=============+=============================================+
   |IoiPathnmWbPd|Run Input I/O for excel workbooks            |
   |             |accessed by path name using pandas package   |
   +-------------+---------------------------------------------+
   |IoiPathnmWbPl|Run Input I/O for excel workbooks            |
   |             |accessed by path name using polaris package  |
   +-------------+---------------------------------------------+
   |IoiPathnmWbOp|Run Input I/O for excel workbooks            |
   |             |accessed by path name using openpyxel package|
   +-------------+---------------------------------------------+
   |IoiPathnmWsOp|Run Input I/O for excel worksheets           |
   |             |accessed by path name using openpyxel package|
   +-------------+---------------------------------------------+

Output I/O Modules
******************

Overview
========

  .. Output-I/O-Modules-label:
  .. table:: *Output I/O Modules*

   +----------+-----------------------------------------------------------------+
   |Name      |Description                                                      |
   +==========+=================================================================+
   |ioowbop.py|Run Output I/O for excel workbooks using the openpyxel package   |
   +----------+-----------------------------------------------------------------+
   |ioowbpd.py|Run Output I/O for excel workbooks using the pandas package      |
   +----------+-----------------------------------------------------------------+
   |ioowbpe.py|Run Output I/O for excel workbooks using the pyexcelerate package|
   +----------+-----------------------------------------------------------------+

ioowbop.py
==========

Static classes
--------------

The Output I/O Module ``ioowbop.py`` contains the following static classes.

  .. Static-classes-of-Output-I/O-module-ioowbop.py-label:
  .. table:: *Static Classes of Output I/O Module ioowbop.py*

   +-------------+---------------------------------------------------+
   |Name         |Description                                        |
   +=============+===================================================+
   |IooPathWbOp  |Run Output I/O for excel workbook to file          |
   |             |referenced by path using the openpyxel package     |
   +-------------+---------------------------------------------------+
   |IooPathnmWbOp|Run Output I/O for excel workbook to file          |
   |             |referenced by path name using the openpyxel package|
   +-------------+---------------------------------------------------+

ioowbpd.py
==========

Static classes
--------------

The Output I/O Module ``ioowbpd.py`` contains the following static classes.

  .. Static-classes-of-Output-I/O--module-ioowbpd.py-label:
  .. table:: *Static Classes of Output I/O Module ioowbpd.py*

   +-----------+-------------------------------------------------+
   |Name       |Description                                      |
   +===========+=================================================+
   |IooPathPdDf|Run Output I/O for pandas dataframe to excel file|
   |           |referenced by path using the pandas writer       |
   +-----------+-------------------------------------------------+

ioowbpe.py
==========

Static classes
--------------

The I/O Output Module ``ioowbpe.py`` contains the following static classes.

  .. Static-classes-of-Output-I/O-module-ioowbpe.py-label:
  .. table:: *Static Classes of Output I/O Module ioowbpe.py*

   +-------------+------------------------------------------------------+
   |Name         |Description                                           |
   +=============+======================================================+
   |IooPathWbPe  |Run Output I/O for excel workbook to file             |
   |             |referenced by path using the pyexcelerate package     |
   +-------------+------------------------------------------------------+
   |IooPathnmWbPe|Run Output I/O for excel workbook to file             |
   |             |referenced by path name using the pyexcelerate package|
   +-------------+------------------------------------------------------+

ioupath.py
==========

Static classes
--------------

The I/O Update Module ``ioupath.py`` contains the following static class.

  .. Static-class-of-Update-I/O-module-ioupath.py-label:
  .. table:: *Static Class of Update I/O Module ioupath.py*

   +-----------+---------------------------------------------------+
   |Name       |Description                                        |
   +===========+===================================================+
   |IouPathWbOp|Run Update I/O of Excel template referenced by path|
   |           |by object using the openpyxel package              |
   +-----------+---------------------------------------------------+

Workbook Modules using the package openpyxel 
============================================

Overview
========

  .. Workbook-Module-using-the-package-openpyxel-label:
  .. table:: **Workbook Module using the package openpyxel**

   +-------+-----------------------------------------------------+
   |Name   |Description                                          |
   +=======+=====================================================+
   |wbop.py|Excel Workbook management using the openpyxel package|
   +-------+-----------------------------------------------------+

wbop.py
=======

Classes
-------

The Workbook Module ``wbop.py`` contains the following static class.

  .. Static-class-of-Workbook-module-wbop.py-label:
  .. table:: *Static class of Workbook Module wbop.py*

   +----+-----------------------------------------------------+
   |Name|Description                                          |
   +====+=====================================================+
   |WbOp|Excel Workbook processing using the openpyxel package|
   +----+-----------------------------------------------------+

Workbook Modules using the package pyexcelerate
***********************************************

Overview
========

  .. Workbook-Module-using-the-package-pyexcelerate-label:
  .. table:: **Workbook Module using the package pyexcelerate**

   +-------+--------------------------------------------------------+
   |Name   |Description                                             |
   +=======+========================================================+
   |wbpe.py|Excel Workbook management using the pyexcelerate package|
   +-------+--------------------------------------------------------+

wbpe.py
=======

Classes
-------

The Workbook Module ``wbpe.py`` contains the following static class.

  .. Static-class-of-Workbook-module-wbpe.py-label:
  .. table:: *Static class of Workbook Module wbpe.py*

   +----+--------------------------------------------------------+
   |Name|Description                                             |
   +====+========================================================+
   |WbPe|Excel Workbook processing using the pyexcelerate package|
   +----+--------------------------------------------------------+

Worksheet Modules using the package openpyxel
*********************************************

Overview
========

  .. Worksheet-Module-using-the-package-openpyxel-label:
  .. table:: **Worksheet-Module-using-the-package-openpyxel**

   +-------+-----------------------------------------------------+
   |Name   |Description                                          |
   +=======+=====================================================+
   |wbpe.py|Excel Worksheet management using the openpyxl package|
   +-------+-----------------------------------------------------+

wsop.py
=======

Classes
-------

The Worksheet Module ``wsop.py`` contains the following static class.

  .. Static-class-of-Worksheet-module-wsop.py-label:
  .. table:: *Static class of Worksheet Module wsop.py*

   +----+------------------------------------------------------+
   |Name|Description                                           |
   +====+======================================================+
   |WsOp|Excel Worksheet processing using the openpyxel package|
   +----+------------------------------------------------------+

Cell Modules using the package openpyxel
****************************************

Overview
========

  .. Cell-Module-using-the-package-openpyxel-label:
  .. table:: **Cell-Module-using-the-package-openpyxel**

   +-------+----------------------------------------------------+
   |Name   |Description                                         |
   +=======+====================================================+
   |rwop.py|Excel Cell management using the pyexcelerate package|
   +-------+----------------------------------------------------+

rwop.py
=======

Classes
-------

The Cell Module ``rwop.py`` contains the following static class.

  .. Static-class-of-Cell-module-wsop.py-label:
  .. table:: *Static class of Cell Module wsop.py*

   +----+-------------------------------------------------+
   |Name|Description                                      |
   +====+=================================================+
   |RwOp|Excel Cell processing using the openpyxel package|
   +----+-------------------------------------------------+

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
