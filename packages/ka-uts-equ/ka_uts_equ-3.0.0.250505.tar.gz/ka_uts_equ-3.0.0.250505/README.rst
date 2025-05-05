##########
ka_uts_arr
##########

Overview
********

.. start short_desc

**Array Utilities**

.. end short_desc

Installation
************

.. start installation

Package ``ka_uts_array`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ka_uts_arr

To install with ``conda``:

.. code-block:: shell

	$ conda install -c conda-forge ka_uts_arr

.. end installation

Package logging
***************

(c.f.: **Appendix**: `Package Logging`)

Package files
*************

Classification
==============

The Files of Package ``ka_uts_arr`` could be classified into the follwing file types
(c.f.: **Appendix**: `Python Terminology`):

#. **Special files**

   a. *py.typed*

#. **Special modules**

   a. *__init__.py* 
   #. *__version__.py*

#. **Modules**

   #. **Modules for dictionaries**

      a. *dic.py*

   #. **Modules for dictionaries of arrays**

      a. *doaod.py*
      #. *doa.py*

   #. **Modules for dictionaries of callables**

      a. *doc.py**

   #. **Modules for dictionaries of dataframes**

      a. *dopddf.py*


Package Modules
===============

Overview
--------

The Modules of Package ``ka_uts_arr`` could be classified into the follwing module types:

#. *Modules for arrays*
#. *Modules for arrays of arrays*
#. *Modules for arrays of dictionaries*
#. *Modules for arrays of basic objects*

Modules for arrays
******************

The Module type ``Modules for arrays`` contains only the module ``arr.py``.


Module: arr.py
==============

The Module ``arr.py`` contains only the static class ``Arr``.

Class: Arr
----------

The Class ``Arr`` contains the following methods:

Methods
^^^^^^^

The Module ``arr.py`` contains only the static class ``Arr``;

arr.py class: Arr
  .. Arr-methods-label:
  .. table:: *Arr methods*

   +-----------------------+---------------------------------------------------+
   |Name                   |Short description                                  |
   +=======================+===================================================+
   |append                 |Append item to the array                           |
   +-----------------------+---------------------------------------------------+
   |append_unique          |Append item to the array if the item is not in the |
   |                       |array.                                             |
   +-----------------------+---------------------------------------------------+
   |apply_function         |Apply function with the keyword arguments to all   |
   |                       |non empty array elements.                          |
   +-----------------------+---------------------------------------------------+
   |apply_replace          |Replace source by target to all array elements.    |
   +-----------------------+---------------------------------------------------+
   |apply_str              |Apply function str to all non empty array elements.|
   +-----------------------+---------------------------------------------------+
   |encode                 |Join array elements with blank separator and encode|
   |                       |result string.                                     |
   +-----------------------+---------------------------------------------------+
   |ex_intersection        |Intersection of first array with second array.     |
   +-----------------------+---------------------------------------------------+
   |extend                 |Extend first array with second array.              |
   +-----------------------+---------------------------------------------------+
   |get_key_value          |Get next array item value without line feed for the|
   |                       |given index or the given default value if the item |
   |                       |value is identical to the given value without line |
   |                       |feeds.                                             |
   +-----------------------+---------------------------------------------------+
   |get_item               |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |get_text               |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |get_text_spli          |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |intersection           |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |is_empty               |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |is_not_empty           |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |join_not_none          |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |length                 |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |merge                  |Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |sh_dic_from_keys_values|Extend array of dicts. with non empty dict.        |
   +-----------------------+---------------------------------------------------+
   |sh_dic_zip             |Join elements of array of dicts.                   |
   +-----------------------+---------------------------------------------------+
   |sh_item                |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item_if             |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item_lower          |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item_str            |Show True if an element exists in the array        |
   +-----------------------+---------------------------------------------------+
   |sh_item0               |Deduplicate array of dicts.                        |
   +-----------------------+---------------------------------------------------+
   |sh_item0_if            |Deduplicate array of dicts.                        |
   +-----------------------+---------------------------------------------------+
   |sh_subarray            |Deduplicate array of dicts.                        |
   +-----------------------+---------------------------------------------------+
   |to_dic                 |Show arr. of arrays created from arr. of dict.     |
   |                       |by using any key- and all value-arrays             |
   +-----------------------+---------------------------------------------------+
   |yield_items            |Convert array of dictionaries to array of          |
   |                       |arrays controlled by key- and value-switch.        |
   +-----------------------+---------------------------------------------------+

Modules for array of arrays
***************************

The Module type ``Modules for array of arrays`` contains only the module ``aoa.py``.

Module: aoa.py
==============

The Module ``aoa.py`` contains only the static class ``AoA``.

Class: AoA
----------

The static Class ``AoA`` contains the subsequent methods.

Methods
^^^^^^^

  .. Methods-of-class-AoA-label:
  .. table:: *Methods of class AoA*

   +-----------------+-----------------------------------------+
   |Name             |Short description                        |
   +=================+=========================================+
   |concatinate      |Concatinate all arrays of array of arrays|
   +-----------------+-----------------------------------------+
   |csv_writerows    |Write array of arrays to csv file        |
   +-----------------+-----------------------------------------+
   |nvl              |Replace empty array of arrays            |
   +-----------------+-----------------------------------------+
   |to_aod           |Convert array of arrays to array of      |
   |                 |dictionaries using an array of keys      |
   +-----------------+-----------------------------------------+
   |to_arr_from_2cols|Convert array of arrays to array using   |
   |                 |a 2-dimensional index array              |
   +-----------------+-----------------------------------------+
   |to_doa_from_2cols|Convert array of arrays to dictionary of |
   |                 |arrays using a 2-dimensionl index array  |
   +-----------------+-----------------------------------------+
   |to_dic_from_2cols|Convert array of arrays to dictionary by |
   |                 |using a 2-dimensional index array        |
   +-----------------+-----------------------------------------+

Method: AoA.concatinate
^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Concatinate all arrays of array of arrays.

Parameter
"""""""""

  .. Parameter-of-method-AoA.concatinate-label:
  .. table:: *Parameter of method AoA.concatinate*

   +-------+-----+-------+---------------+
   |Name   |Type |Default|Description    |
   +=======+=====+=======+===============+
   |aoa    |TyAoA|       |Array of arrays|
   +-------+-----+-------+---------------+

Return Value
""""""""""""

  .. Return-Value-method-AoA.concatinate-label:
  .. table:: *Return Value of method AoA.concatinate*

   +-------+-----+-----------+
   |Name   |Type |Description|
   +=======+=====+===========+
   |arr_new|TyArr|new array  |
   +-------+-----+-----------+

Method: csv_writerows
^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Write Array of Arrays to Csv file defined by the path string 
using the function "writerows" of module "csv".

Parameter
"""""""""

  .. Parameter-of-method-AoA.csv_writerows-label:
  .. table:: *Parameter of method AoA.csv_writerows*

   +------+------+----------------+
   |Name  |Type  |Description     |
   +======+======+================+
   |aoa   |TyAoA |Array of arrays |
   +------+------+----------------+
   |path  |TyPath|Path string     |
   +------+------+----------------+
   |kwargs|TyDic |Keyword aruments|
   +------+------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-method-AoA.csv_writerows-label:
  .. table:: *Parameter/Return Value of method AoA.csv_writerows*

   +------+------+----------------+
   |Name  |Type  |Description     |
   +======+======+================+
   |      |None  |                |
   +------+------+----------------+

Method: AoA.nvl
^^^^^^^^^^^^^^^

Description
"""""""""""

Return the empty array if the Array of Arrays is None.

Parameter
"""""""""

  .. Parameter-of-method-AoA.nvl-label:
  .. table:: *Parameter of method AoA.nvl*

   +-------+-----+-------+-------------------+
   |Name   |Type |Default|Description        |
   +=======+=====+=======+===================+
   |aoa    |TyAoA|       |Array of arrays    |
   +-------+-----+-------+-------------------+

Return Value
""""""""""""

  .. Return-Value-of-method-AoA.nvl-label:
  .. table:: *Return Value of method AoA.nvl*

   +-------+-----+-------------------+
   |Name   |Type |Description        |
   +=======+=====+===================+
   |aoa_new|TyAoA|new Array of arrays|
   +-------+-----+-------------------+

Method: AoA.to_aod
^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert array of arrays to array of Dictionaries.

Parameter
"""""""""

  .. Parameter-of-method-AoA.to_aod-label:
  .. table:: *Parameter of method AoA.to_aod*

   +----+-----+-------+---------------+
   |Name|Type |Default|Description    |
   +====+=====+=======+===============+
   |aoa |TyAoA|       |Array of arrays|
   +----+-----+-------+---------------+
   |keys|TyArr|       |Array of keys  |
   +----+-----+-------+---------------+

Return Value
""""""""""""

  .. Return-Value-of-method-AoA.to_aod-label:
  .. table:: *Return Value of method AoA.to_aod*

   +----+-----+---------------------+
   |Name|Type |Description          |
   +====+=====+=====================+
   |aod |TyAoD|array of dictionaries|
   +----+-----+---------------------+

Method: AoA.to_arr_from_2cols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert Array of Arrays to unique array with distinct elements by
selecting 2 columns of each Array as elements of the new array using a
2-dimensional index-array.

Parameter
"""""""""

  .. Parameter-of-method-AoA.to_arr_from_2cols-label:
  .. table:: *Parameter of method AoA.to_arr_from_2cols*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoa |TyAoA|       |Array of arrays |
   +----+-----+-------+----------------+
   |a_ix|TyAoI|       |Array of integer|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-method-AoA.to_arr_from_2cols-label:
  .. table:: *Return Value of method AoA.to_arr_from_2cols*

   +----+-----+-------------------+
   |Name|Type |Description        |
   +====+=====+===================+
   |arr |TyArr|Array              |
   +----+-----+-------------------+

Method: AoA.to_doa_from_2cols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert array of arrays to dictionary of unique arrays (array with distinct elements)

#. Select 2 columns of each array as key-, value-candidates of the new dictionary
   using a 2-dimensional index-array. 

#. If the new key exists then 
   the new value extends the key value as unique array, 
   
# otherwise
   the new value is assigned as unique array to the key.

Parameter
"""""""""

  .. Parameter-of-method-AoA.to_doa_from_2cols-label:
  .. table:: *Parameter of method AoA.to_doa_from_2cols*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoa |TyAoA|       |Array of arrays |
   +----+-----+-------+----------------+
   |a_ix|TyAoI|       |Array of integer|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-method-AoA.to_doa_from_2cols-label:
  .. table:: *Return Value of method AoA.to_doa_from_2cols*

   +----+-----+-------------------+
   |Name|Type |Description        |
   +====+=====+===================+
   |doa |TyDoA|Dictionry of arrays|
   +----+-----+-------------------+

Method: AoA.to_dic_from_2cols
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Convert array of arrays to dictionary by selecting 2 columns of each array as
key-, value-candidates of the new dictionary if the key is not none using a
2-dimensional index-array.

Parameter
"""""""""

  .. Parameter-of-method-AoA.to_dic_from_2cols-label:
  .. table:: *Parameter of method AoA.to_dic_from_2cols*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoa |TyAoA|       |Array of arrays |
   +----+-----+-------+----------------+
   |a_ix|TyAoI|       |Array of integer|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return-Value-of-method-AoA.to_dic_from_2cols-label:
  .. table:: **Return Value of method AoA.to_dic_from_2cols**

   +----+-----+-----------+
   |Name|Type |Description|
   +====+=====+===========+
   |dic |TyDic|Dictionary |
   +----+-----+-----------+

Modules for array of dictionaries
*********************************

  .. Modules-for-array-of-dictionaries-label:
  .. table:: **Modules-for-array-of-dictionaries**

   +--------+-----------------------------------+
   |Name    |Description                        |
   +========+===================================+
   |aod2p.py|Array of 2-dimensional dictionaries|
   +--------+-----------------------------------+
   |aod.py  |Array of dictionaries              |
   +--------+-----------------------------------+

aod.py
======

The Module ``aod.py`` contains only the static class ``AoD``;

Class: AoD
----------

Methods
^^^^^^^

  .. Methods-of-class-AoD-label:
  .. table:: *Methods of class AoD*

   +------------------------------------+----------------------------------------------+
   |Name                                |Short description                             |
   +====================================+==============================================+
   |add                                 |Add object to array of dictionaries.          |
   +------------------------------------+----------------------------------------------+
   |apply_function                      |Apply function to array of dictionaries       |
   +------------------------------------+----------------------------------------------+
   |csv_dictwriterows                   |Write array of dictionaries to csv file       |
   |                                    |with function dictwriterows.                  |
   +------------------------------------+----------------------------------------------+
   |dic_found_with_empty_value          |Return True or raise an exception if the arr. |
   |                                    |of dicts. contains a dict. with empty value   |
   |                                    |and the execption switch is True.             |
   +------------------------------------+----------------------------------------------+
   |extend_if_not_empty                 |Extend array of dicts. with non empty dict.   |
   +------------------------------------+----------------------------------------------+
   |join_aod                            |Join elements of array of dicts.              |
   +------------------------------------+----------------------------------------------+
   |merge_dic                           |Merge elements of array of dicts.             |
   +------------------------------------+----------------------------------------------+
   |nvl                                 |Replace empty array of dicts.                 |
   +------------------------------------+----------------------------------------------+
   |pd_to_csv                           |Write array of dicts. to csv file with pandas.|
   +------------------------------------+----------------------------------------------+
   |pl_to_csv                           |Write array of dicts. to csv file with polars.|
   +------------------------------------+----------------------------------------------+
   |put                                 |Write transformed array of dicts. to a csv    |
   |                                    |file with a selected I/O function.            |
   +------------------------------------+----------------------------------------------+
   |sh_doaod_split_by_value_is_not_empty|Converted array of dicts. to array of arrays  |
   |                                    |dict. by using conditional split              |
   +------------------------------------+----------------------------------------------+
   |sh_dod                              |Convert array of dicts. to dict. of dicts.    |
   +------------------------------------+----------------------------------------------+
   |sh_key_value_found                  |Show True if an element exists in the array of|
   |                                    |dicts. which contains the key, value pair     |
   +------------------------------------+----------------------------------------------+
   |sh_unique                           |Deduplicate arr.  of dicts.                   |
   +------------------------------------+----------------------------------------------+
   |split_by_value_is_not_empty         |Split arr. of dicts. by the condition "the    |
   |                                    |given key value is not empty".                |
   +------------------------------------+----------------------------------------------+
   |to_aoa                              |Convert array of dictionaries to array of     |
   |                                    |arrays controlled by key- and value-switch.   |
   +------------------------------------+----------------------------------------------+
   |to_aoa of_keys_values               |Convert arr. of dicts. to arr. of arrays usin |
   |                                    |keys of any dict. and values of all dict.     |
   +------------------------------------+----------------------------------------------+
   |to_aoa of_values                    |Convert arr. of dicts. to arr. of arrays      |
   |                                    |using values of all dict.                     |
   +------------------------------------+----------------------------------------------+
   |to_aoa of_key_values                |Convert array of dicts. to array using dict.  |
   |                                    |values with given key.                        |
   +------------------------------------+----------------------------------------------+
   |to_doaod_by_key                     |Convert array of dics. to dict. of arrays of  |
   |                                    |dicts. using a key.                           |
   +------------------------------------+----------------------------------------------+
   |to_dic_by_key                       |Convert array of dicts. to dict. of dicts     |
   |                                    |using a key                                   |
   +------------------------------------+----------------------------------------------+
   |to_dic_by_lc_keys                   |Convert array of dicts. to dict. of arrays    |
   |                                    |using 2 lowercase keys.                       |
   +------------------------------------+----------------------------------------------+
   |to_unique_by_key                    |Convert array of dicts. to array of dicts by  |
   +------------------------------------+----------------------------------------------+
   |sh_unique                           |by selecting dictionaries with ke.            |
   +------------------------------------+----------------------------------------------+
   |write_xlsx_wb                       |Write array of dicts. to xlsx workbook.       |
   +------------------------------------+----------------------------------------------+

Method: AoD.add
^^^^^^^^^^^^^^^

Description
"""""""""""

Add object to array of dictionaries.

#. If the objects is a dictionary:

   * the object is appended to the array of dictionaries
  
#. If the objects is an array of dictionaries:

   * the object extends the array of dictionaries

Parameter
"""""""""

  .. Parameter-of-method-AoD.add-label:
  .. table:: *Parameter of method AoD.add*

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |Array of dictionaries|
   +----+-----+-------+---------------------+
   |obj |TyAny|       |Object               |
   +----+-----+-------+---------------------+

Return Value
""""""""""""

  .. Return-Value-of-method-AoD.add-label:
  .. table:: **Return Value of AoD.add**

   +----+----+---------------------+
   |Name|Type|Description          |
   +====+====+=====================+
   |    |None|                     |
   +----+----+---------------------+

Method: AoD.apply_function
^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Create a new array of dictionaries by applying the function to each element
of the array of dictionaries.

Parameter
"""""""""

  .. Parameter-of-method-AoD.apply_function-label:
  .. table:: **Parameter of method AoD.apply_function**

   +------+-------+---------------------+
   |Name  |Type   |Description          |
   +======+=======+=====================+
   |aod   |TyAoD  |Array of dictionaries|
   +------+-------+---------------------+
   |fnc   |TN_Call|Object               |
   +------+-------+---------------------+
   |kwargs|TN_Dic |Keyword arguments    |
   +------+-------+---------------------+

Return Value
""""""""""""

  .. Return-Value-of-method-AoD.apply_function-label:
  .. table:: **Return Value of method AoD.apply_function**

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyAoD|new array of dictionaries|
   +-------+-----+-------------------------+

Method: AoD.csv_dictwriterows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^          

Description
"""""""""""

Write given array of dictionaries (1.argument) to a csv file with the given path
name (2.argument) using the function "dictwriter" of the builtin path module "csv"

Parameter
"""""""""

  .. Parameter-of-method-AoD.csc_dictwriterows-label:
  .. table:: **Parameter of method AoD.csc_dictwriterows**

   +----+------+---------------------+
   |Name|Type  |Description          |
   +====+======+=====================+
   |aod |TyAoD |Array of dictionaries|
   +----+------+---------------------+
   |path|TyPath|Path                 |
   +----+------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.csc_dictwriterows-label:
  .. table:: **Return Value of method AoD.csc_dictwriterows**

   +----+------+---------------------+
   |Name|Type  |Description          |
   +====+======+=====================+
   |    |None  |                     |
   +----+------+---------------------+
   
Method: AoD.dic_found_with_empty_value
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^       
   
Description
"""""""""""

#. Set the switch sw_found to True if a dictionary with an empty value for the key is found
   in the given array of dictionaries (1.argument). 

#. If the Argument "sw_raise" is True and the switch "sw_found" is True, then an Exception is raised,
   otherwise the value of "sw_found" is returned.                  

Parameter
"""""""""

  .. Parameter-of-method-AoD.dic_found_with_empty_value-label:
  .. table:: **Parameter of method AoD.dic_found_with_empty_value**

   +--------+------+-------+---------------------+
   |Name    |Type  |Default|Description          |
   +========+======+=======+=====================+
   |aod     |TyAoD |       |array of dictionaries|
   +--------+------+-------+---------------------+
   |key     |TyStr |       |Key                  |
   +--------+------+-------+---------------------+
   |sw_raise|TyBool|False  |                     |
   +--------+------+-------+---------------------+

Return Value
""""""""""""

  .. Return-Value-of-method-AoD.dic_found_with_empty_value-label:
  .. table:: **Return Value of method AoD.dic_found_with_empty_value**

   +--------+------+----------------------------+
   |Name    |Type  |Description                 |
   +========+======+============================+
   |sw_found|TyBool|key is found in a dictionary|
   +--------+------+----------------------------+
   
Method: AoD.extend_if_not_empty
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

#. Apply the given function (4.argument) to the value of the given dictionary (2.argument) for
   the key (3.argument).

#. The result is used to extend the given array of dictionaries (1.argument).

Parameter
"""""""""

  .. Parameter-of-method-AoD.extend_if_not_empty-label:
  .. table:: **Parameter of method AoD.extend_if_not_empty**

   +--------+------+-------+---------------------+
   |Name    |Type  |Default|Description          |
   +========+======+=======+=====================+
   |aod     |TyAoD |       |Array of dictionaries|
   +--------+------+-------+---------------------+
   |dic     |TyDic |       |Dictionary           |
   +--------+------+-------+---------------------+
   |key     |TN_Any|       |Key                  |
   +--------+------+-------+---------------------+
   |function|TyCall|       |Function             |
   +--------+------+-------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.extend_if_not_empty-label:
  .. table:: **Return Value of method AoD.extend_if_not_empty**

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyAoD|New array of dictionaries|
   +-------+-----+-------------------------+
   
Method: AoD.join_aod
^^^^^^^^^^^^^^^^^^^^
  
Description
"""""""""""

join 2 arrays of dictionaries

Parameter
"""""""""

  .. Parameter-of-method-AoD.join_aod-label:
  .. table:: **Parameter of method AoD.join_aod**

   +----+-----+-------+----------------------------+
   |Name|Type |Default|Description                 |
   +====+=====+=======+============================+
   |aod0|TyAoD|       |First array of dictionaries |
   +----+-----+-------+----------------------------+
   |aod1|TyAoD|       |Second array of dictionaries|
   +----+-----+-------+----------------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.join_aod-label:
  .. table:: **Return Value of method AoD.join_aod**

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyAoD|New array of dictionaries|
   +-------+-----+-------------------------+
   
Method: AoD.merge_dic
^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

Merge array of dictionaries (1.argument) with the dictionary (2.argument).

#. Each element of the new array of dictionaries is created by merging an element
   of the given array of dictionaries with the given dictionary.
   
Parameter
"""""""""

  .. Parameter-of-method-AoD.merge_dic-label:
  .. table:: **Parameter of method AoD.merge_dic**

   +----+------+-------+---------------------+
   |Name|Type  |Default|Description          |
   +====+======+=======+=====================+
   |aod |TN_AoD|       |Array of dictionaries|
   +----+------+-------+---------------------+
   |dic |TN_Dic|       |Dictionary           |
   +----+------+-------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.merge_new-label:
  .. table:: *Return Value of method AoD.merge_new*

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyAoD|New array of dictionaries|
   +-------+-----+-------------------------+
   
Method: AoD.nvl
^^^^^^^^^^^^^^^
   
Description
"""""""""""

Replace a none value of the first argument with the emty array. 

Parameter
"""""""""

  .. Parameter-of-method-AoD.nvl-label:
  .. table:: *Parameter of method AoD.nvl*

   +----+------+-------+---------------------+
   |Name|Type  |Default|Description          |
   +====+======+=======+=====================+
   |aod |TN_AoD|       |Array of dictionaries|
   +----+------+-------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.nvl-label:
  .. table:: *Return Value of method AoD.nvl*

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyArr|New array of dictionaries|
   +-------+-----+-------------------------+
   
Method: AoD.pd_to_csv
^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

#. Convert the given array of dictionaries (1.argument) to a panda dataframe using the panda function "from_dict".

#. Write the result to a csv file with the given path name (2.argument using the panda function "to_csv".

Parameter
"""""""""

  .. Parameter-of-method-AoD.pd_to_csv-label:
  .. table:: *Parameter of method AoD.pd_to_csv*

   +------+------+-------+---------------------+
   |Name  |Type  |Default|Description          |
   +======+======+=======+=====================+
   |aod   |TyAoD |       |Array of dictionaries|
   +------+------+-------+---------------------+
   |path  |TyPath|       |Csv file psth        |
   +------+------+-------+---------------------+
   |fnc_pd|TyCall|       |Panda function       |
   +------+------+-------+---------------------+
   
Method: AoD.pl_to_csv
^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

#. Convert the given array of dictionaries (1.argument) to a panda dataframe with the panda function "from_dict". 

#. Convert the result to a polars dataframe using the polars function "to_pandas".
  
#. Apply the given function (3. argument) to the polars dataframe.
  
#. Write the result to a csv file with the given name (2.argument) using the polars function "to_csv".

Parameter
"""""""""

  .. Parameter-of-method-AoD.pl_to_csv-label:
  .. table:: *Parameter of method AoD.pl_to_csv*

   +------+------+-------+---------------------+
   |Name  |Type  |Default|Description          |
   +======+======+=======+=====================+
   |aod   |TyAoD |       |Array of dictionaries|
   +------+------+-------+---------------------+
   |path  |TyPath|       |Csv file path        |
   +------+------+-------+---------------------+
   |fnc_pd|TyCall|       |Polars function      |
   +------+------+-------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-AoD-method-AoD.pl_to_csv-label:
  .. table:: *Return Value of AoD method AoD.pl_to_csv*

   +----+----+---------------------+
   |Name|Type|Description          |
   +====+====+=====================+
   |    |None|                     |
   +----+----+---------------------+
   
Method: AoD.put
^^^^^^^^^^^^^^^
   
Description
"""""""""""

#. Transform array of dictionaries (1.argument) with a transformer function (3.argument)

#. If the I/O function is defined for the given dataframe type (4.argument).

   #. write result to a csv file with the given path name (2.argument).

Parameter
"""""""""

  .. Parameter-of-method-AoD.put-label:
  .. table:: *Parameter of method AoD.put*

   +-------+------+-------+---------------------+
   |Name   |Type  |Default|Description          |
   +=======+======+=======+=====================+
   |aod    |TyAoD |       |Array of dictionaries|
   +-------+------+-------+---------------------+
   |path   |TyPath|       |Csv file path        |
   +-------+------+-------+---------------------+
   |fnc_aod|TyAoD |       |AoD function         |
   +-------+------+-------+---------------------+
   |df_type|TyStr |       |Dataframe type       |
   +-------+------+-------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.put-label:
  .. table:: *Return Value of method AoD.put*

   +----+----+--------------------+
   |Name|Type|Description         |
   +====+====+====================+
   |    |None|                    |
   +----+----+--------------------+
   
Method: AoD.sh_doaod_split_by_value_is_not_empty
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

#. Create 2-dimensional dict. of array of dictionaries from given array of dict. (1.argument)
and key (2.argument) to split the array of dictionaries into 2 array of dictionaries by
the two conditions

   #. "the key is contained in the dictionary and the value empty".

   #. "the key is contained in the dictionary and the value is not empty".

#. The first array of dictionaries is created by the condition and is assigned to 
   the new dictionary of array of dictionaries using the given key (3.argument).

#. The second array of dictionaries is created by the negation of the condition 
   and is assigned to the new dictionary of array of dictionaries using the given
   key (4.argument).

Parameter
"""""""""

  .. Parameter-of-method-AoD.join_aod-label:
  .. table:: *Parameter of method AoD.join_aod*

   +-----+-----+-------+--------------------------------------+
   |Name |Type |Default|Description                           |
   +=====+=====+=======+======================================+
   |aod  |TyAoD|       |Array of dictionaries                 |
   +-----+-----+-------+--------------------------------------+
   |key  |Any  |       |Key                                   |
   +-----+-----+-------+--------------------------------------+
   |key_n|Any  |       |key of the array of dictionaries      |
   |     |     |       |wich satisfies the condition.         |
   +-----+-----+-------+--------------------------------------+
   |key_y|Any  |       |key of the array of dictionaries which|
   |     |     |       |does not satisfies the condition.     |
   +-----+-----+-------+--------------------------------------+
   
  .. Return-Value-of-method-AoD.join_aod-label:
  .. table:: *Return Value of method AoD.join_aod*

   +-----+-------+-----------------------------------+
   |Name |Type   |Description                        |
   +=====+=======+===================================+
   |doaod|TyDoAoD|Dictionary of array of dictionaries|
   +-----+-------+-----------------------------------+
   
Method: AoD.sh_dod
^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

Create dictionary of dicionaries from the array of dictionaries (1.argument) and the key (2.argument).       

Parameter
"""""""""

  .. Parameter-of-method-AoD.sh_dod-label:
  .. table:: *Parameter of method AoD.sh_dod*

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |Array of dictionaries|
   +----+-----+-------+---------------------+
   |key |Any  |       |Key                  |
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.sh_dod-label:
  .. table:: *Return Value of method AoD.sh_dod*

   +----+-----+--------------------------+
   |Name|Type |Description               |
   +====+=====+==========================+
   |dod |TyDoD|Dictionary of dictionaries|
   +----+-----+--------------------------+
   
Method: AoD.sh_unique
^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Deduplicate array of dictionaries (1.argument).
   
Parameter
"""""""""

  .. Parameter-of-method-AoD.sh_unique-label:
  .. table:: *Parameter of method AoD.sh_unique*

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |Array of dictionaries|
   +----+-----+-------+---------------------+
   |key |Any  |       |Key                  |
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.sh_unique-label:
  .. table:: *Return Value of method AoD.sh_unique*

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyAoD|New array of dictionaties|
   +-------+-----+-------------------------+
   
Method: AoD.split_by_value_is_not_empty
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^      
   
Description
"""""""""""

Split the given array of dictionary into 2 arrays of dictionary by the condition 
"the key is contained in the dictionary and the value is not empty"

Parameter
"""""""""

  .. Parameter-of-method-AoD.split_by_value_is_not_empty-label:
  .. table:: *Parameter of method AoD.split_by_value_is_not_empty*

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |array of dictionaries|
   +----+-----+-------+---------------------+
   |key |Any. |       |Key                  |
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.split_by_value_is_not_empty-label:
  .. table:: *Return Value of method AoD.split_by_value_is_not_empty*

   +--------------+--------+---------------------------------+
   |Name          |Type    |Description                      |
   +==============+========+=================================+
   |(aod_n, aod_y)|Ty2ToAoD|Tuple of 2 arrays of dictionaries|
   +--------------+--------+---------------------------------+
   
Method: AoD.sw_key_value_found
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

Set the condition to True if:

* the key is contained in a dictionary of the array of dictionaries and

* the key value is not empty"

Parameter
"""""""""

  .. Parameter-of-method-AoD.sw_key_value_found-label:
  .. table:: **Parameter of method AoD.sw_key_value_found**

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |Array of dictionaries|
   +----+-----+-------+---------------------+
   |key |Any  |       |Key                  |
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. Parameter-of-method-AoD.sw_key_value_found-label:
  .. table:: **Parameter/Return Value of method AoD.sw_key_value_found**

   +----+------+-------+--------------------------------+
   |Name|Type  |Default|Description                     |
   +====+======+=======+================================+
   |sw  |TyBool|       |key is contained in a dictionary|
   |    |      |       |of the array of dictionaries    |
   +----+------+-------+--------------------------------+
   
Method: AoD.to_aoa
^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

Create array of arrays from given array of dictionaries (1.argument).

#. If switch sw_keys (2.argument) is True:

   Create the first element of the array of arrays as the list of dict. keys of the
   first elements of the array of dictionaries.

#. If the switch sw_values (3. argument) is True:

   Create the other elemens of the array of dictionries as list of dict. values of the
   elements of the array of dictionaries.

Parameter
"""""""""

  .. Parameter-of-method-AoD.to_aoa-label:
  .. table:: **Parameter of method AoD.to_aoa**

   +---------+------+-------+---------------------+
   |Name     |Type  |Default|Description          |
   +=========+======+=======+=====================+
   |aod      |TyAoD |       |array of dictionaries|
   +---------+------+-------+---------------------+
   |sw_keys  |TyBool|       |keys switch          |
   +---------+------+-------+---------------------+
   |sw_values|TyBool|       |values switch        |
   +---------+------+-------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.to_aoa-label:
  .. table:: **Return Value of method AoD.to_aoa**

   +----+-----+---------------+
   |Name|Type |Description    |
   +====+=====+===============+
   |aoa |TyAoA|array of arrays|
   +----+-----+---------------+
   
Method: AoD.to_aoa of_key_values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

Convert the given array of dictionary (1.argument) into an array of arrays.
#. Create first element of the new array of arrays as the keys-list of the first dictionary.
#. Create other elements as the values-lists of the dictionaries of the array of dictionaries.

Parameter
"""""""""

  .. Parameter-of-method-to_aoa_of_key_values-label:
  .. table:: **Parameter of method to_aoa_of_key_values**

   +----+-----+--------+---------------------+
   |Name|Type |Default |Description          |
   +====+=====+========+=====================+
   |aod |TyAoD|        |Array of dictionaries|
   +----+-----+--------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.to_aoa_of_key_values-label:
  .. table:: **Return Value of method AoD.to_aoa_of_key_values**

   +----+-----+---------------+
   |Name|Type |Description    |
   +====+=====+===============+
   |aoa |TyAoA|Array of arrays|
   +----+-----+---------------+
   
Method: AoD.to_aoa_of_values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  
Description
"""""""""""

Convert the given array of dictionaries (1.argument) into an array of arrays.
The elements of the new array of arrays are the values-lists of the dictionaries
of the array of dictionaries.

Parameter
"""""""""

  .. Parameter-of-method-AoD.to_aoa_of_values-label:
  .. table:: **Parameter of method AoD.to_aoa_of_values**

   +----+-----+--------+---------------------+
   |Name|Type |Default |Description          |
   +====+=====+========+=====================+
   |aod |TyAoD|        |Array of dictionaries|
   +----+-----+--------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.to_aoa_of_values-label:
  .. table:: **Return Value of method AoD.to_aoa_of_values**

   +----+-----+--------+---------------+
   |Name|Type |Default |Description    |
   +====+=====+========+===============+
   |aoa |TyAoA|        |Array of arrays|
   +----+-----+--------+---------------+
   
Method: AoD.to_arr of_key_values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

Convert the given array of dictionaries (1.argument) to an array. The elements of the new
array are the selected values of each dictionary of the array of dictionaries with the 
given key (2.argument).

Parameter
"""""""""

  .. Parameter-of-method-AoD.to_arr_of_key_values-label:
  .. table:: **Parameter of method AoD.to_arr_of_key_values**

   +----+-----+--------+---------------------+
   |Name|Type |Default |Description          |
   +====+=====+========+=====================+
   |aod |TyAoD|        |Array of dictionaries|
   +----+-----+--------+---------------------+
   |key |Any  |        |Key                  |
   +----+-----+--------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.to_arr_of_key_values-label:
  .. table:: **Return Value of method AoD.to_arr_of_key_values**

   +----+-----+-----------+
   |Name|Type |Description|
   +====+=====+===========+
   |arr |TyAoD|New array  |
   +----+-----+-----------+
   
Method: AoD.to_doaod_by_key
^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. Parameter-of-method-AoD.to_doaod_by_key-label:
  .. table:: **Parameter of method AoD.to_doaod_by_key**

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |Array of dictionaries|
   +----+-----+-------+---------------------+
   |key |Any  |       |Key                  |
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.to_doaod_by_key-label:
  .. table:: **Return Value of method AoD.to_doaod_by_key**

   +-----+-----+-----------------------------------+
   |Name |Type |Description                        |
   +=====+=====+===================================+
   |doaod|TyAoD|Dictionary of array of dictionaries|
   +-----+-----+-----------------------------------+
   
Method: AoD.to_dod_by_key
^^^^^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. Parameter-of-method-AoD.to_dod_by_key-label:
  .. table:: **Parameter of method AoD.to_dod_by_key**

   +----+-----+-------+-------------+
   |Name|Type |Default|Description  |
   +====+=====+=======+=============+
   |aod |TyAoD|       |             |
   +----+-----+-------+-------------+
   |key |Any  |       |             |
   +----+-----+-------+-------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.to_dod_by_key-label:
  .. table:: **Return Value of method AoD.to_dod_by_key**

   +----+-----+-------------+
   |Name|Type |Description  |
   +====+=====+=============+
   |dic |TyDic|             |
   +----+-----+-------------+
   
   
Method: AoD.to_doa_by_lc_keys
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. Parameter-of-method-AoD.to_doa_by_lc_keys-label:
  .. table:: **Parameter of method AoD.to_doa_by_lc_keys**

   +----+-----+-------+-------------+
   |Name|Type |Default|Description  |
   +====+=====+=======+=============+
   |aod |TyAoD|       |             |
   +----+-----+-------+-------------+
   |key |Any  |       |             |
   +----+-----+-------+-------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.to_doa_by_lc_keys-label:
  .. table:: **Return Value of method AoD.to_doa_by_lc_keys**

   +----+-----+-------------+
   |Name|Type |Description  |
   +====+=====+=============+
   |doa |TyDoA|             |
   +----+-----+-------------+
   
method: AoD.to_unique_by_key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. Parameter-of-method-AoD.to_unique_by_key-label:
  .. table:: **Parameter of method AoD.to_unique_by_key**

   +----+-----+-------+-------------+
   |Name|Type |Default|Description  |
   +====+=====+=======+=============+
   |aod |TyAoD|       |             |
   +----+-----+-------+-------------+
   |key |Any  |       |             |
   +----+-----+-------+-------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoD.to_unique_by_key-label:
  .. table:: **Return Value of method AoD.to_unique_by_key**

   +-------+-----+-------+-------------+
   |Name   |Type |Default|Description  |
   +=======+=====+=======+=============+
   |aod_new|TyAoD|       |             |
   +-------+-----+-------+-------------+
   
AoD method: write_xlsx_wb
^^^^^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. Parameter-of-method-AoD.write_xlsx_wb-label:
  .. table:: **Parameter of method AoD.write_xlsx_wb**

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |array of dictionaries|
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-AoD-method-write_xlsx_wb-label:
  .. table:: **Return Value of AoD method write_xlsx_wb**

   +----+-----+-----------+
   |Name|Type |Description|
   +====+=====+===========+
   |    |None |           |
   +----+-----+-----------+
   
Modules for array of basic objects
**********************************

  .. Modules-for-arrays-of-basic-objects-label:
  .. table:: **Modules for arrays of basic objects**

   +---------+----------------+
   |Name     |Description     |
   +=========+================+
   |aoo.py   |Array of objects|
   +---------+----------------+
   |aopath.py|Array of paths  |
   +---------+----------------+
   |aos.py   |Array of strings|
   +---------+----------------+

Module: aoo.py
==============

The Module ``aoo.py`` contains the single static class ``AoO``;

Class: AoO
----------

Methods
^^^^^^^

  .. AoO-methods-label:
  .. table:: *AoO methods*

   +---------+------------------------+
   |Name     |short Description       |
   +=========+========================+
   |to_unique|Concatinate array arrays|
   +---------+------------------------+

Method: to_unique
^^^^^^^^^^^^^^^^^
   
Deduplicate array of objects

Parameter
"""""""""

  .. Parameter-of-Method-AoO.to_unique-label:
  .. table:: **Parameter of Method AoO.to_unique**

   +----+-----+----------------+
   |Name|Type |Description     |
   +====+=====+================+
   |aoo |TyAoO|Array of objects|
   +----+-----+----------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoO.to_unique-label:
  .. table:: **Return Value of method AoOR.to_unique**

   +-------+-----+--------------------+
   |Name   |Type |Description         |
   +=======+=====+====================+
   |aoo_new|TyAoO|New array of objects|
   +-------+-----+--------------------+
   
Module: aopath.py
=================

The Module ``aopath.py`` contains only thestatic class ``AoPath``;

Class: AoPath
-------------

Methods
^^^^^^^

  .. AoPath-methods-label:
  .. table:: *AoPath methods*

   +--------------------------+-------------------------------------------------+
   |Name                      |short Description                                |
   +==========================+=================================================+
   |join                      |Join array of paths using the os separator       |
   +--------------------------+-------------------------------------------------+
   |sh_a_path                 |Show array of paths for path template.           |
   +--------------------------+-------------------------------------------------+
   |sh_a_path_by_tmpl         |Convert array of path template keys and kwargs   |
   |                          |to array of paths.                               |
   +--------------------------+-------------------------------------------------+
   |sh_path_tmpl              |Convert array of path templates to path template.|
   +--------------------------+-------------------------------------------------+
   |yield_path_kwargs         |yield path for path-array and kwargs.            |
   +--------------------------+-------------------------------------------------+
   |yield_path_kwargs_new     |yield path from dictionary- and path-array and   |
   |                          |modified kwargs by dictionary item               |
   +--------------------------+-------------------------------------------------+
   |yield_path_item_kwargs    |yield path from path-array, item from array and  |
   |                          |kwargs.                                          |
   +--------------------------+-------------------------------------------------+
   |yield_path_item_kwargs_new|yield path from path-array, item from array and  |
   |                          |modified kwargs by dictionary item.              |
   +--------------------------+-------------------------------------------------+

Method: join
^^^^^^^^^^^^
   
#. Convert array of paths (1.argument) by striping the leading or trailing os separator.

#. join the converted array of paths.

Parameter
"""""""""

  .. Parameter-of-Method-AoPath.joinbel:
  .. table:: **Parameter of Method AoPath.join**

   +------+--------+-------+--------------+
   |Name  |Type    |Default|Description   |
   +======+========+=======+==============+
   |aopath|TyAoPath|       |array of paths|
   +------+--------+-------+--------------+
   
Return Value
""""""""""""

  .. Return-Value-of-Method-AoPath.join-label:
  .. table:: **Return Value of Method AoPath.join**

   +----+------+-----------+
   |Name|Type  |Description|
   +====+======+===========+
   |path|TyPath|Path       |
   +----+------+-----------+
   
Method: sh_a_path
^^^^^^^^^^^^^^^^^

Convert path template to array of paths using glob function of module glob.py.

Parameter
"""""""""

  .. Parameter-of-method-AoPath.sh_a_path-label:
  .. table:: **Parameter of method AoPath.sh_a_path**

   +----+------+-------+-----------+
   |Name|Type  |Default|Description|
   +====+======+=======+===========+
   |path|TyPath|       |Path       |
   +----+------+-------+-----------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoPath.sh_a_path-label:
  .. table:: **Return Value of method AoPath.sh_a_path**

   +------+--------+--------------+
   |Name  |Type    |Description   |
   +======+========+==============+
   |a_path|TyAoPath|Array of paths|
   +------+--------+--------------+
   
Method: AoPath.sh_a_path_by_tmpl
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
#. Select array of path templates from keyword arguments (1.arguments) using the parameter

   * array of path template keys (1.argument);

#. join the array of path templates with the os separator

#. convert the created final path template to an array of paths.

Parameter
"""""""""

  .. Parameter-of-method-AoPath.sh_a_path_by_tmpl-label:
  .. table:: *Parameter of method AoPath.sh_a_path_by_tmpl*

   +---------------+--------+-------+---------------------------+
   |Name           |Type    |Default|Description                |
   +===============+========+=======+===========================+
   |a_path_tmpl_key|TyAoPath|       |array of path template keys|
   +---------------+--------+-------+---------------------------+
   |kwargs         |TyDic   |       |keyword arguments          |
   +---------------+--------+-------+---------------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoPath.sh_a_path_by_tmpl-label:
  .. table:: *Return Value of method AoPath.sh_a_path_by_tmpl*

   +------+--------+-------+-----------+
   |Name  |Type    |Default|Description|
   +======+========+=======+===========+
   |a_path|TyAoPath|       |Path       |
   +------+--------+-------+-----------+
   
Method: AoPath.yield_path_kwargs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
#. Create array of paths by executing the function sh_a_path_by_tmpl with the parameter:

   * array of path template keys (2.argument).
    
#. Loop over array of paths to yield:

   #. yield path, kwargs (3. argument)

Parameter
"""""""""

  .. Parameter-of-method-AoPath.yield_path_kwargs-label:
  .. table:: **Parameter of method AoPath.yield_path_kwargs**

   +---------------+--------+-------+---------------------------+
   |Name           |Type    |Default|Description                |
   +===============+========+=======+===========================+
   |cls            |Tyclass |       |current class              |
   +---------------+--------+-------+---------------------------+
   |a_path_tmpl_key|TyAoPath|       |array of path template keys|
   +---------------+--------+-------+---------------------------+
   |kwargs         |TyDic   |       |keyword arguments          |
   +---------------+--------+-------+---------------------------+

Return Value
""""""""""""

  .. Return-Value-of-method-AoPath.yield_path_kwargs-label:
  .. table:: **Return Value of method AoPath.yield_path_kwargs**

   +--------------+--------+-----------+
   |Name          |Type    |Description|
   +==============+========+===========+
   |(path, kwargs)|TyAoPath|Path       |
   +--------------+--------+-----------+
   
Method: AoPath.yield_path_kwargs_new
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Synopsis
""""""""

sh_a_path_by_tmpl(a_path_tmpl_key, kwargs)


Description
"""""""""""

#. Create array of directories by executing the function sh_a_path_by_tmpl with the arguments:

   * array of directory template keys (2.argument).

#. Loop over array of directories to:

   #. create kwargs_new by executing ths given function sh_kwargs_new (4. argument) with the arguments:

      * directory, given kwargs (5. argument) 

   #. create array of paths by executing the function sh_a_oath_by_tmpl with the arguments:

      * given array of path template keys (3. argument), kwargs_new

#. Loop over array of paths within the outer loop to:

   #. yield path, kwargs_new

Parameter
"""""""""

  .. Parameter-of-method-AoPath.yield_path_kwargs-new-label:
  .. table:: **Parameter of method AoPath.yield_path_kwarg-news**

   +---------------+--------+-------+-----------------------------------+
   |Name           |Type    |Default|Description                        |
   +===============+========+=======+===================================+
   |cls            |Tyclass |       |Current class                      |
   +---------------+--------+-------+-----------------------------------+
   |a_dir_tmpl_key |TyAoPath|       |Array of path template keys        |
   +---------------+--------+-------+-----------------------------------+
   |a_path_tmpl_key|TyAoPath|       |Array of path template keys        |
   +---------------+--------+-------+-----------------------------------+
   |sh_kwargs_new  |TyAoPath|       |Show new keyword arguments function|
   +---------------+--------+-------+-----------------------------------+
   |kwargs         |TyDic   |       |Keyword arguments                  |
   +---------------+--------+-------+-----------------------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoPath.yield_path_kwargs-new-label:
  .. table:: **Return Value of method AoPath.yield_path_kwarg-news**

   +------------------+--------+---------------------------+
   |Name              |Type    |Description                |
   +==================+========+===========================+
   |(path, kwargs_new)|TyAoPath|Path, new keyword arguments|
   +------------------+--------+---------------------------+
   
Method: AoPath.yield_path_item_kwargs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
#. Create array of paths by executing the function sh_a_path_by_tmpl with the arguments:

   * array of path template keys (2.argument).

#. Create array of items by selecting the value in the directory kwargs (4. argument) for
   the kwargs key (3. argument)

#. Loop over array of path and array of items to:

   #. yield path, item, kwargs (4. argument)

Parameter
"""""""""

  .. Parameter-of-method-AoPath.yield_path_item_kwargs-label:
  .. table:: **Parameter of method AoPath.yield_path_item_kwargs**

   +---------------+--------+-------+---------------------------+
   |Name           |Type    |Default|Description                |
   +===============+========+=======+===========================+
   |cls            |Tyclass |       |current class              |
   +---------------+--------+-------+---------------------------+
   |a_path_tmpl_key|TyAoPath|       |array of path template keys|
   +---------------+--------+-------+---------------------------+
   |a_arr_key      |TyAoPath|       |array of path template keys|
   +---------------+--------+-------+---------------------------+
   |kwargs         |TyDic   |       |keyword arguments          |
   +---------------+--------+-------+---------------------------+
   
Return Value
""""""""""""

  .. Return Value-of-method-AoPath.yield_path_item_kwargs-label:
  .. table:: **Return Value of method AoPath.yield_path_item_kwargs**

   +--------------------+--------+-----------------------------+
   |Name                |Type    |Description                  |
   +====================+========+=============================+
   |(path, item, kwargs)|TyAoPath|Path, Item, keyword arguments|
   +--------------------+--------+-----------------------------+
   
Method: AoPath.yield_path_item_kwargs_new
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
#. Create array of directories by executing the function sh_a_path_by_tmpl with the parameter:

   * a_dir_tmpl_key (2.argument).

#. Create  array of items by selecting the value in the directory kwargs (4. argument) for
   the key arr_key (3. argument)

#. Loop over the array of directories to:

   #. create kwargs_new by executing ths function sh_kwargs_new (4. argument) with the arguments:

      * directory, given kwargs (5. argument) 

   #. create array of paths by executing the function sh_a_oath_by_tmpl with the arguments:

      * given array of path template keys (3. argument), kwargs_new

   #. Loop over array of path and array of items within the outer loop to:

      #. yield path, item, kwargs_new

Parameter
"""""""""

  .. Parameter-of-method-AoPath.yield_path_item_kwargs_new-label:
  .. table:: **Parameter of method AoPath.yield_path_item_kwargs_new**

   +---------------+--------+-------+-----------------------------------+
   |Name           |Type    |Default|Description                        |
   +===============+========+=======+===================================+
   |cls            |Tyclass |       |current class                      |
   +---------------+--------+-------+-----------------------------------+
   |a_dir_tmpl_key |TyAoPath|       |array of path template keys        |
   +---------------+--------+-------+-----------------------------------+
   |a_path_tmpl_key|TyAoPath|       |array of path template keys        |
   +---------------+--------+-------+-----------------------------------+
   |sh_kwargs_new  |TyAoPath|       |show new keyword arguments function|
   +---------------+--------+-------+-----------------------------------+
   |kwargs         |TyDic   |       |keyword arguments                  |
   +---------------+--------+-------+-----------------------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-AoPath.yield_path_item_kwargs_new-label:
  .. table:: *Return Value of method AoPath.yield_path_item_kwargs_new**

   +------------------------+--------+---------------------------------+
   |Name                    |Type    |Description                      |
   +========================+========+=================================+
   |(path, item, kwargs_new)|TyAoPath|Path, Item, new keyword arguments|
   +------------------------+--------+---------------------------------+
   
Module: aos.py
**************

Classes
=======

The Module ``aos.py`` contains the single static class ``AoS``;

Class: AoS
----------

Methods
^^^^^^^

  .. AoS-methods-label:
  .. table:: *AoS methods*

   +-------------------------+------------------------------------------+
   |Name                     |short Description                         |
   +=========================+==========================================+
   |nvl                      |Replace empty array of strings            |
   +-------------------------+------------------------------------------+
   |sh_a_date                |Convert array of strings to array of dates|
   +-------------------------+------------------------------------------+
   |to_lower                 |Convert array of strings to array of      |
   |                         |lowered strings.                          |
   +-------------------------+------------------------------------------+
   |to_unique                |Deduplicate array of arrays               |
   +-------------------------+------------------------------------------+
   |to_unique_lower          |Convert array of strings to deduplicted   |
   |                         |array of lowered strings.                 |
   +-------------------------+------------------------------------------+
   |to_unique_lower_invariant|Convert array of arrays to array of arrays|
   +-------------------------+------------------------------------------+

Method: AoS.to_unique
^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. Parameter-of-method-AoS.to_unique-label:
  .. table:: *Parameter of method AoS.to_unique*

   +----+-----+-------+----------------+
   |Name|Type |Default|Description     |
   +====+=====+=======+================+
   |aoo |TyAoO|       |array of objects|
   +----+-----+-------+----------------+

Return Value
""""""""""""

  .. Return Value-of-method-AoS.to_unique-label:
  .. table:: *Return Value of method AoS.to_unique*

   +-------+-----+--------------------+
   |Name   |Type |Description         |
   +=======+=====+====================+
   |aoo_new|TyAoO|new array of objects|
   +-------+-----+--------------------+

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
