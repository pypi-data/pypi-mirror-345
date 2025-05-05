##########
ka_uts_dfr
##########

Overview
********

.. start short_desc

**Dataframe 'Utilities'**

.. end short_desc

Installation
************

.. start installation

Package ``ka_uts_dfr`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ka_uts_dfr

To install with ``conda``:

.. code-block:: shell

	$ conda install -c conda-forge ka_uts_dfr

.. end installation

This requires that the ``readme`` extra is installed:

.. code-block:: shell

	$ python -m pip install ka_uts_dfr[readme]

Package Modules
***************

Classification
==============

The Modules of Package ``ka_uts_dfr`` could be classified into the following module classes:

#. *Modules for pandas dataframe*
#. *Modules for polars dataframe*

Modules for Pandas Dataframe    
****************************

  .. Modules-for-pandas-dataframe-label:
  .. table:: *Modules for Pandas Dataframe*

   +-------+----------------+
   |Name   |Type            |
   +=======+================+
   |pddf.py|Pandas Dataframe|
   +-------+----------------+

pddf.py
=======

The Module ``pddf.py`` contains a single static classes ``PdDf``.

pddf.py Class: PdDf
-------------------

The static Class ``PdDf`` is used to manage Pandas Dataframes;
it contains the subsequent methods.

PdDf Methods
^^^^^^^^^^^^

  .. Methods-of-static-class-PdDf-label:
  .. table:: *Methods of static class PdDf*

   +----------------------+--------------------------------------------------+
   |Name                  |Description                                       |
   +======================+==================================================+
   |sh_d_aod              |show dictionary of array of dictionaries.         |
   +----------------------+--------------------------------------------------+
   |sh_d_pddf             |show dictionary of pandas dataframes.             |
   +----------------------+--------------------------------------------------+
   |pivot_table           |create pandas dataframe pivot table.              |
   |                      |The pivot rules are defined by a pivot dictionary.|
   +----------------------+--------------------------------------------------+
   |filter                |Filter pandas dataframe.                          |
   |                      |The filteris defined by filter dictionary         |
   +----------------------+--------------------------------------------------+
   |set_ix_drop_col_filter|set index and drop column filter                  |
   +----------------------+--------------------------------------------------+
   |format-leading_zeros  |format pandas dataframe columns with leading zeros|         
   +----------------------+--------------------------------------------------+
   |format-as-date        |format pandas dataframe columns as date           |
   +----------------------+--------------------------------------------------+

PdDf Method: sh_d_aod
^^^^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PdDf-method-sh_d_aod-label:
  .. table:: **Parameter of PdDf method sh_d_aod**

   +----+------+-----------------+
   |Name|Type  |Description      |
   +====+======+=================+
   |df  |TyPdDf|Pandas Datafame  |
   +----+------+-----------------+
   |key |str   |Keyword arguments|
   +----+------+-----------------+

Return Value
""""""""""""

  .. Return-Value-of-PdDf-method-sh_d_aod-label:
  .. table:: **Return Value of PdDf method sh_d_aod**

   +-----+--------+-----------------------------------+
   |Name |Type    |Description                        |
   +=====+========+===================================+
   |d_aod|TyDoAoD |dictionary of array of dictionaries|
   +-----+--------+-----------------------------------+

PdDf Method: sh_d_pddf
^^^^^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PdDf-method-sh_d_pddf-label:
  .. table:: **Parameter of PdDf method sh_d_pddf**

   +----+------+-----------------+
   |Name|Type  |Description      |
   +====+======+=================+
   |cls |class |current class    |
   +----+------+-----------------+
   |df  |TyPdDf|Pandas Datafame  |
   +----+------+-----------------+
   |key |str   |keyword arguments|
   +----+------+-----------------+

Return Value
""""""""""""

  .. Return-Value-of-PdDf-method-sh_d_pddf-label:
  .. table:: **Return Value of PdDf method sh_d_pddf**

   +----+--------+-------------------------------+
   |Name|Type    |Description                    |
   +====+========+===============================+
   |d_df|TyDoPdDf|dictionary of pandas dataframes|
   +----+--------+-------------------------------+
   
PdDf Method: pivot_table
^^^^^^^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PdDf-method-pivot_table-label:
  .. table:: **Parameter of PdDf method pivot_table**

   +----+------+---------------------------------+
   |Name|Type  |Description                      |
   +====+======+=================================+
   |cls |class |current class                    |
   +----+------+---------------------------------+
   |df  |TyPdDf|pandas datafame                  |
   +----+------+---------------------------------+
   |d_pv|TyDic |pivot table definition dictionary|
   +----+------+---------------------------------+

Return Value
""""""""""""

  .. Return-Value-of-PdDf-method-pivot_table-label:
  .. table:: *Return Value of PdDf method pivot_table*

   +----+------+----------------------------+
   |Name|Type  |Description                 |
   +====+======+============================+
   |dfpv|TyPdDf|pandas dataframe pivot table|
   +----+------+----------------------------+

PdDf Method: filter
^^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PdDf-method-filter-label:
  .. table:: **Parameter of PdDf method filter**

   +--------+------+----------------------------+
   |Name    |Type  |Description                 |
   +========+======+============================+
   |cls     |class |current class               |
   +--------+------+----------------------------+
   |df      |TyPdDf|pandas datafame             |
   +--------+------+----------------------------+
   |d_filter|TyDic |filter definition dictionary|
   +--------+------++---------------------------+
   |relation|TyStr |filter relation             |
   +--------+------+----------------------------+

Return Value
""""""""""""

  .. Return-Value-of-PdDf-method-filter-label:
  .. table:: **Return Value of PdDf method filter**

   +------+------+------------------------+
   |Name  |Type  |Description             |
   +======+======+========================+
   |df_new|TyPdDf|filtered pandas datafame|
   +------+------+------------------------+

PdDf Method: set_ix_drop_col_filter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PdDf-method-set_ix_drop_col_filter-label:
  .. table:: *Parameter of PdDf method set_ix_drop_col_filter*

   +--------+------+----------------------------+
   |Name    |Type  |Description                 |
   +========+======+============================+
   |cls     |class |current class               |
   +--------+------+----------------------------+
   |df      |TyPdDf|pandas datafame             |
   +--------+------+----------------------------+
   |d_filter|TyDic |filter definition dictionary|
   +--------+------+----------------------------+
   |relation|str   |filter relation             |
   +--------+------+----------------------------+

Return Value
""""""""""""

  .. Return-Value-of-PdDf-method-set_ix_drop_col_filter-label:
  .. table:: *Return Value of PdDf method set_ix_drop_col_filter*

   +------+------+------------------------+
   |Name  |Type  |Description             |
   +======+======+========================+
   |df_new|TyPdDf|filtered pandas datafame|
   +------+------+------------------------+

PdDf Module: format_leading_zeros
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PdDf-method-format_leading_zeros-label:
  .. table:: **Parameter of PdDf method format_leading_zeros**

   +--------+------+----------------------------+
   |Name    |Type  |Description                 |
   +========+======+============================+
   |cls     |class |current class               |
   +--------+------+----------------------------+
   |df      |TyPdDf|pandas datafame             |
   +--------+------+----------------------------+
   |d_filter|TyDic |filter definition dictionary|
   +--------+------+----------------------------+
   |relation|str   |filter relation             |
   +--------+------+----------------------------+

Return Value
""""""""""""

  .. Return-Value-of-PdDf-method-format_leading_zeros-label:
  .. table:: **Return Value of PdDf method format_leading_zeros**

   +------+------+------------------------+
   |Name  |Type  |Description             |
   +======+======+========================+
   |df_new|TyPdDf|filtered pandas datafame|
   +------+------+------------------------+

PdDf Method: format_as_date
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PdDf-method-format_as_date-label:
  .. table:: **Parameter of PdDf method format_as_date**

   +--------+------+----------------------------+
   |Name    |Type  |Description                 |
   +========+======+============================+
   |cls     |class |current class               |
   +--------+------+----------------------------+
   |df      |TyPdDf|pandas datafame             |
   +--------+------+----------------------------+
   |d_filter|TyDic |filter definition dictionary|
   +--------+------+----------------------------+
   |relation|str   |filter relation             |
   +--------+------+----------------------------+

Return Value
""""""""""""

  .. Return Values-of-PdDf-method-format_as_date-label:
  .. table:: **Return Values of PdDf methodR ormat_as_date**

   +------+------+------------------------+
   |Name  |Type  |Description             |
   +======+======+========================+
   |df_new|TyPdDf|filtered pandas datafame|
   +------+------+------------------------+

Modules for Polars Dataframe    
****************************

  .. Modules-for-polars-dataframe-label:
  .. table:: *Modules for Polars Dataframe*

   +---------------------+------------------------------------+
   |Module               |Classes                             |
   +-----+---------------+----+------+------------------------+
   |Name|Type            |Name|Type  |Description             |
   +====+================+====+======+========================+
   |pldf|Polars Dataframe|PdDf|Static|Manage Polars Dataframes|
   +----+----------------+----+------+------------------------+

pldf.py
=======

The Module ``pldf`` contains a single static class ``PLDF``.

PlDf
----

The static Class ``PlDf`` contains the subsequent methods.

PlDf Methods
^^^^^^^^^^^^

  .. pldf-methods-label:
  .. table:: *pldf Methods*

   +------------+------------------------------------------------------------+
   |Name        |Description                                                 |
   +============+============================================================+
   |filter      |Filter polars dataframe using the given statement.          |
   +------------+------------------------------------------------------------+
   |pivot       |Create polars dataframe pivot table.                        |
   |            |The pivot rules are defined by the given pivot dictionary.  |
   +------------+------------------------------------------------------------+
   |pivot_filter|Filter polars dataframe using the given statement and       |
   |            |create polars dataframe pivot table from filtered dataframe.|
   |            |The pivot rules are defined by the given pivot dictionary.  |
   +------------+------------------------------------------------------------+
   |to_aod      |create pandas dataframe pivot table.                        |
   |            |The pivot rules are defined by pivot dictionary             |
   +------------+------------------------------------------------------------+
   |to_doa      |create pandas dataframe pivot table.                        |
   |            |The pivot rules are defined by pivot dictionary             |
   +------------+------------------------------------------------------------+

PlDf Method: filter
^^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PlDf-method-filter-label:
  .. table:: *Parameter of PlDf method filter*

   +----+------+----------------+
   |Name|Type  |Description     |
   +====+======+================+
   |cls |class |current class   |
   +----+------+----------------+
   |df  |TyPdDf|polars datafame |
   +----+------+----------------+
   |stmt|TyStmt|filter statement|
   +----+------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-PlDf-method-filter-label:
  .. table:: *Return Value of PlDf method filter*

   +------+------+------------------------+
   |Name  |Type  |Description             |
   +======+======+========================+
   |df_new|TyPlDf|filtered polars datafame|
   +------+------+------------------------+

PlDf Method: pivot
^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PlDf-method-pivot-label:
  .. table:: *Parameter of P.Df method pivot*

   +----+------+---------------------------------+
   |Name|Type  |Description                      |
   +====+======+=================================+
   |cls |class |current class                    |
   +----+------+---------------------------------+
   |df  |TyPlDf|polars datafame                  |
   +----+------+---------------------------------+
   |d_pv|TyDic |pivot table definition dictionary|
   +----+------+---------------------------------+

Return Value
""""""""""""

  .. Return-Value-of-PdDf-method-pivot_label:
  .. table:: *Return value of PdDf method pivot*

   +----+------+----------------------------+
   |Name|Type  |Description                 |
   +====+======+============================+
   |dfpv|TyPlDf|polars dataframe pivot table|
   +----+------+----------------------------+

PlDf Method: pivot_filter
^^^^^^^^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PdDf-method-pivot_filter-label:
  .. table:: *Parameter of PdDf method pivot_filter*

   +----+------+---------------------------------+
   |Name|Type  |Description                      |
   +====+======+=================================+
   |cls |class |current class                    |
   +----+------+---------------------------------+
   |df  |TyPlDf|polars datafame                  |
   +----+------+---------------------------------+
   |d_pv|TyDic |pivot table definition dictionary|
   +----+------+---------------------------------+
   |stmt|TyStmt|filter statement                 |
   +----+------+---------------------------------+

Return Value
""""""""""""

  .. Return-Value-of-PlDf-method-pivot_filter-label:
  .. table:: *Return value of PlDf method pivot_gilter*

   +----+------+----------------------------+
   |Name|Type  |Description                 |
   +====+======+============================+
   |dfpv|TyPlDf|polars dataframe pivot table|
   +----+------+----------------------------+

PlDf Method: to_aod
^^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PdDf-method-to_aod-label:
  .. table:: *Parameter of PdDf method to_aod*

   +----+------+---------------+
   |Name|Type  |Description    |
   +====+======+===============+
   |df  |TyPlDf|polars datafame|
   +----+------+---------------+

Return Value
""""""""""""

  .. Return-Value-of-PlDf-method-to_aod-label:
  .. table:: *Return value of PlDf method to_aod*

   +----+-----+---------------------+
   |Name|Type |Description          |
   +====+=====+=====================+
   |aod |TyAoD|Array of Dictionaries|
   +----+-----+---------------------+

PlDf Method: to_doa 
^^^^^^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-PdDf-method-to_doa-label:
  .. table:: *Parameter of PdDf method to_doa*

   +----+------+---------------+
   |Name|Type  |Description    |
   +====+======+===============+
   |df  |TyPlDf|polars datafame|
   +----+------+---------------+

Return Value
""""""""""""

  .. Return-Value-of-PlDf-method-to_doa-label:
  .. table:: *Return value of PlDf method to_doa*

   +----+-----+--------------------+
   |Name|Type |Description         |
   +====+=====+====================+
   |doa |TyDoA|Dictionary of Arrays|
   +----+-----+--------------------+

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
