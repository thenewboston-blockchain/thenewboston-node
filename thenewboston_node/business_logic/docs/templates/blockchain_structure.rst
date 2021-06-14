thenewboston blockchain format
******************************

Directory structure
===================

+------------------------------------+------------------------------------+
| Content                            | Path                               |
+====================================+====================================+
| Blockchain root directory          | ``/path/to/blockchain/root/``      |
+------------------------------------+------------------------------------+
| `Account root files`_ directory    | ``+---{{ (file_blockchain.account_root_file_subdir + '/``').ljust(28) }} |
+------------------------------------+------------------------------------+
| `Block chunk files`_ directory     | ``+---{{ (file_blockchain.blocks_subdir + '/``').ljust(28) }} |
+------------------------------------+------------------------------------+

Directory nesting
=================

For filesystem access optimization files are saved to nested directories of
``{{ file_blockchain.file_optimization_max_depth }}`` levels. It is used for storing both
account root files and block chunk files.

+---------------------------------+---------------------------------------------------------------+
| Content                         | Path                                                          |
+=================================+===============================================================+
| A root directory                | ``/path/to/blockchain/root/file-type-specific-directory``     |
+---------------------------------+---------------------------------------------------------------+
{% for level in range(file_blockchain.file_optimization_max_depth) -%}
| {{ level }} level subdirectory            | ``{{ ((('.  ' + '   ' * (level - 1)) if level else '') + '+---' + level.__str__() + '-th character of filename``').ljust(59) }} |
+---------------------------------+---------------------------------------------------------------+
{% endfor %}

Examples:

- ``0000100199-arf.msgpack.xz`` to be saved to ``/path/to/blockchain/root/{{ file_blockchain.make_optimized_file_path('0000100199-arf.msgpack.xz', file_blockchain.file_optimization_max_depth) }}``
- ``00012300000000000100-00012300000000000199-block-chunk.msgpack.xz`` to be saved to as
  ``/path/to/blockchain/root/{{ file_blockchain.make_optimized_file_path('00012300000000000100-00012300000000000199-block-chunk.msgpack.xz', file_blockchain.file_optimization_max_depth) }}``

Files format
============

Both account root files and block chunk files have the same format, but different business logic
related structure. Latter is described in sections `Account root file structure`_ and
`Block chunk file structure`_. This section describes general technical format regardless to
the actual data being stored in the files.

General filename template is ``base-name.msgpack[.compressor]``:

- ``base-name`` is specific to file type and described in other sections
- ``.msgpack`` denotes that data is stored in MessagePack_ format
- ``.compressor`` represents compression algorithm if present

Supported compression algorithms:

{% for compressor in file_blockchain.compressors -%}
- {{ compressor }}
{% endfor %}

Deserialization
---------------

+-----------------------------------------+------------------------------------+-------------------------------------------------+
| Source                                  | Deserialization step               | Result                                          |
+=========================================+====================================+=================================================+
| ``base-name.msgpack{{ ('[.' + '|'.join(file_blockchain.compressors) + ']``').ljust(20) }} | `Decompress`_                      | MessagePack_ binary: ``base-name.msgpack``      |
+-----------------------------------------+------------------------------------+-------------------------------------------------+
| ``base-name.msgpack``                   | `Deserialize from MessagePack`_    | In-memory MessagePack_ compacted object         |
+-----------------------------------------+------------------------------------+-------------------------------------------------+
| In-memory MessagePack_ compacted object | `Uncompact`_                       | In-memory MessagePack_ object                   |
+-----------------------------------------+------------------------------------+-------------------------------------------------+

Decompress
^^^^^^^^^^

Just use corresponding decompression algorithm. Here is how we do it in Python::

    DECOMPRESSION_FUNCTIONS = {
        'gz': gzip.decompress,
        'bz2': bz2.decompress,
        'xz': lzma.decompress,
    }

Deserialize from MessagePack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Account root file contains a single serialized MessagePack object.
- See `Block chunk file format`_

Uncompact
^^^^^^^^^

Restore human readable key names
""""""""""""""""""""""""""""""""
.. list-table::
   :header-rows: 1

   * - Compact (short) key name
     - Rename
     - Humanized (long) key name

{% for long_key, short_key in compact_key_map %}
   * - {{ short_key }}
     - ->
     - {{ long_key }}
{% endfor %}

Convert byte array to hexadecimal representation
""""""""""""""""""""""""""""""""""""""""""""""""

TODO(dmu) HIGH: Get information from code which values to be converted

Account root files
==================

Account root files directory
----------------------------

Account root files are saved to ``/path/to/blockchain/root/{{ file_blockchain.account_root_file_subdir }}/``
in a nested directory structure as described in `Directory nesting`_ section

For example, file named ``0000100199-arf.msgpack.xz`` will be saved to as
``/path/to/blockchain/root/{{ file_blockchain.make_optimized_file_path('0000100199-arf.msgpack.xz', file_blockchain.file_optimization_max_depth) }}``

Account root file structure
---------------------------

Account root filename format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Filename template is "``{{ file_blockchain.account_root_file_template.format(last_block_number='x' *  file_blockchain.order_of_account_root_file) }}[.compressor]``"
where "``{{ 'x' *  file_blockchain.order_of_account_root_file }}``" is the last block number of the account root file and "``.compressor``" represents compression algorithm
if present.

Filename example of last block number 199 compressed with LZMA compression: ``{{ file_blockchain.get_account_root_filename(199) }}.xz``.

NOTE: Initial root account file filename is ``{{ file_blockchain.get_account_root_filename(None) }}``.

Account root file format
^^^^^^^^^^^^^^^^^^^^^^^^

{% for model in blockchain_models %}
{{ model.__name__ }}
{{ '"' * model.__name__.__len__() }}

{{ model.get_docstring() }}

{% if model.get_field_names() -%}
.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
     - Is mandatory
{% for field_name in model.get_field_names() -%}
{%- set field_type = model.get_field_type(field_name) %}
{%- set field_type_name = field_type.__name__ %}
   * - {{ field_name }}
     - {% if f.is_model(field_type) %}`{{ field_type_name }}`_{% else %}{{ f.get_mapped_type_name(field_type_name) }}{% endif %}
     - {{ model.get_field_docstring(field_name) }}
     - {% if model.is_optional_field(field_name) %}No{% else %}Yes{% endif %}
{%- endfor %}
{% endif %}
{% endfor %}


Account root file example
"""""""""""""""""""""""""

.. code-block:: JSON

    {{ models.blockchain_state.sample.serialize_to_dict() | tojson(indent=4) | indent }}

Compacted account root file example
"""""""""""""""""""""""""""""""""""

.. code-block:: JSON

    {{ models.blockchain_state.sample.to_compact_dict(compact_keys=True, compact_values=False) |
       tojson(indent=4) | indent }}

Block chunk files
=================

Account root files are saved to ``/path/to/blockchain/root/{{ file_blockchain.blocks_subdir }}/``
in a nested directory structure as described in `Directory nesting`_ section

For example, file named ``00012300000000000100-00012300000000000199-block-chunk.msgpack.xz`` will be saved to as
``/path/to/blockchain/root/{{ file_blockchain.make_optimized_file_path('00012300000000000100-00012300000000000199-block-chunk.msgpack.xz', file_blockchain.file_optimization_max_depth) }}``

Block chunk file structure
--------------------------

Block chunk filename format
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Filename template is "``{{ file_blockchain.block_chunk_template.format(start='x' *  file_blockchain.order_of_block, end='y' *  file_blockchain.order_of_block) }}[.compressor]``"
where "``{{ 'x' *  file_blockchain.order_of_block }}``" is the first block number of the block chunk file,
"``{{ 'y' *  file_blockchain.order_of_block }}``" is the last block number of the block chunk file
and "``.compressor``" represents compression algorithm if present.

Filename example of block chunk file for block from 100 to 199 compressed with LZMA compression: ``{{ file_blockchain.get_block_chunk_filename(100, 199) }}``


Block chunk file format
^^^^^^^^^^^^^^^^^^^^^^^

Block chunk file contains multiple streamed serialized MessagePack objects: each block is
serialized and the MessagePack_ binary appended to the file (it is NOT a serializes array
of blocks).

Block structure
^^^^^^^^^^^^^^^

{% for model in block_models %}
{{ model.__name__ }}
{{ '"' * model.__name__.__len__() }}

{{ model.get_docstring() }}

{% if model.get_field_names() -%}
.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
     - Is mandatory
{% for field_name in model.get_field_names() -%}
{%- set field_type = model.get_field_type(field_name) %}
{%- set field_type_name = field_type.__name__ %}
   * - {{ field_name }}
     - {% if f.is_model(field_type) %}`{{ field_type_name }}`_{% else %}{{ f.get_mapped_type_name(field_type_name) }}{% endif %}
     - {{ model.get_field_docstring(field_name) }}
     - {% if model.is_optional_field(field_name) %}No{% else %}Yes{% endif %}
{%- endfor %}
{% endif %}
{% endfor %}

SignedChangeRequestMessage
""""""""""""""""""""""""""

SignedChangeRequestMessage is a base type for the following subtypes.

{% for model in signed_change_request_message_models %}
{{ model.__name__ }}
{{ "'" * model.__name__.__len__() }}

{{ model.get_docstring() }}

{% if model.get_field_names() -%}
.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
     - Is mandatory
{% for field_name in model.get_field_names() -%}
{%- set field_type = model.get_field_type(field_name) %}
{%- set field_type_name = field_type.__name__ %}
   * - {{ field_name }}
     - {% if f.is_model(field_type) %}`{{ field_type_name }}`_{% else %}{{ f.get_mapped_type_name(field_type_name) }}{% endif %}
     - {{ model.get_field_docstring(field_name) }}
     - {% if model.is_optional_field(field_name) %}No{% else %}Yes{% endif %}
{%- endfor %}
{% endif %}
{% endfor %}

Block example
"""""""""""""

.. code-block:: JSON

    {{ models.block.sample.serialize_to_dict() | tojson(indent=4) | indent }}

Compacted block example
"""""""""""""""""""""""

Byte arrays are shown as hexadecimals for representation purposes:

.. code-block:: JSON

    {{ models.block.sample.to_compact_dict(compact_keys=True, compact_values=False) |
       tojson(indent=4) | indent }}

.. Links targets
.. _MessagePack: https://msgpack.org/


Common models structure
=======================

{% for model in common_models %}
{{ model.__name__ }}
{{ "-" * model.__name__.__len__() }}

{{ model.get_docstring() }}

{% if model.get_field_names() -%}
.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
     - Is mandatory
{% for field_name in model.get_field_names() -%}
{%- set field_type = model.get_field_type(field_name) %}
{%- set field_type_name = field_type.__name__ %}
   * - {{ field_name }}
     - {% if f.is_model(field_type) %}`{{ field_type_name }}`_{% else %}{{ f.get_mapped_type_name(field_type_name) }}{% endif %}
     - {{ model.get_field_docstring(field_name) }}
     - {% if model.is_optional_field(field_name) %}No{% else %}Yes{% endif %}
{%- endfor %}
{% endif %}
{% endfor %}
