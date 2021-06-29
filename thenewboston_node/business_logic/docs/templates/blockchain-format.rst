thenewboston blockchain format
******************************

Directory structure
===================

+-------------------------------------+------------------------------------+
| Content                             | Path                               |
+=====================================+====================================+
| Blockchain root directory           | ``/path/to/blockchain/root/``      |
+-------------------------------------+------------------------------------+
| `Blockchain state files`_ directory | ``+---{{ (file_blockchain.account_root_file_subdir + '/``').ljust(28) }} |
+-------------------------------------+------------------------------------+
| `Block chunk files`_ directory      | ``+---{{ (file_blockchain.blocks_subdir + '/``').ljust(28) }} |
+-------------------------------------+------------------------------------+

Directory nesting
=================

For filesystem access optimization, files are saved to ``{{ file_blockchain.file_optimization_max_depth }}``
levels of nested directories. These store both blockchain state files and block chunk files.

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
- ``00012300000000000100-00012300000000000199-block-chunk.msgpack.xz`` to be saved to
  ``/path/to/blockchain/root/{{ file_blockchain.make_optimized_file_path('00012300000000000100-00012300000000000199-block-chunk.msgpack.xz', file_blockchain.file_optimization_max_depth) }}``

Files format
============
Although blockchain state files and block chunk files have the same format, their
business logic related structure is different. For details on their structure, see
sections `Blockchain state structure`_ and `Block chunk file structure`_.
This section describes the general technical format regardless of the actual data
stored in the files.

The general filename template is ``base-name.msgpack[.compressor]``:

- ``base-name`` is specific to file type and described in other sections.
- ``.msgpack`` denotes that data is stored in MessagePack_ format.
- ``.compressor`` represents compression algorithm, if present.

Supported compression algorithms:

{% for compressor in file_blockchain.compressors -%}
- {{ compressor }}
{% endfor %}

Deserialization
---------------

``base-name.msgpack[.({{ '|'.join(file_blockchain.compressors) }})]`` === `Decompress`_ ==>
MessagePack_ binary: ``base-name.msgpack`` === `Deserialize from MessagePack`_ ==>
In-memory MessagePack_ compacted object === `Uncompact`_ ==> In-memory MessagePack_ object

Decompress
^^^^^^^^^^

Use corresponding decompression algorithm. For example, in Python use::

    DECOMPRESSION_FUNCTIONS = {
        'gz': gzip.decompress,
        'bz2': bz2.decompress,
        'xz': lzma.decompress,
    }

Deserialize from MessagePack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Blockchain state contains a single serialized MessagePack_ object. For details, see `Block chunk file format`_.

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

All fields of `hexstr`_ type are the objects for such conversion.

Blockchain state files
======================

Blockchain state files directory
--------------------------------

Blockchain states are saved to ``/path/to/blockchain/root/{{ file_blockchain.account_root_file_subdir }}/``
in a nested directory structure, as described in section `Directory nesting`_.

For example, a file named ``0000100199-arf.msgpack.xz`` will be saved to
``/path/to/blockchain/root/{{ file_blockchain.make_optimized_file_path('0000100199-arf.msgpack.xz', file_blockchain.file_optimization_max_depth) }}``

Blockchain state structure
--------------------------

Blockchain state filename format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Filename template is "``{{ file_blockchain.account_root_file_template.format(last_block_number='x' *  file_blockchain.order_of_account_root_file) }}[.compressor]``"
where "``{{ 'x' *  file_blockchain.order_of_account_root_file }}``" is the last block number of the blockchain state file and "``.compressor``" represents compression algorithm, if present.

Filename example of last block number 199 compressed with LZMA compression: ``{{ file_blockchain.get_account_root_filename(199) }}.xz``.

**Note:** Initial root account file filename is ``{{ file_blockchain.get_account_root_filename(None) }}``.

Blockchain state format
^^^^^^^^^^^^^^^^^^^^^^^

Blockchain state example
""""""""""""""""""""""""

.. code-block:: JSON

    {{ sample_blockchain_state.serialize_to_dict() | tojson(indent=4) | indent }}

Compacted blockchain state example
""""""""""""""""""""""""""""""""""

.. code-block:: JSON

    {{ sample_blockchain_state.to_compact_dict(compact_keys=True, compact_values=False) |
       tojson(indent=4) | indent }}

Format description
""""""""""""""""""

{% for model in blockchain_state_models %}
{{ model.__name__ }}
{{ '"' * model.__name__.__len__() }}

{{ model.get_docstring() }}

{% if model.get_field_names() -%}
.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Type
     - Example value
     - Is mandatory
{% for field_name in model.get_field_names() %}
   * - {{ field_name }}
     - {{ model.get_field_docstring(field_name) }}
     - {{ model.get_field_type_representation(field_name) }}
     - {{ model.get_field_example_value(field_name)|default('', True) }}
     - {% if model.is_serialized_optional_field(field_name) %}No{% else %}Yes{% endif %}
{%- endfor %}
{% endif %}
{% endfor %}

Block chunk files
=================

Blockchain state files are saved to ``/path/to/blockchain/root/{{ file_blockchain.blocks_subdir }}/``
in a nested directory structure, as described in section `Directory nesting`_.

For example, a file named ``00012300000000000100-00012300000000000199-block-chunk.msgpack.xz`` will be saved to
``/path/to/blockchain/root/{{ file_blockchain.make_optimized_file_path('00012300000000000100-00012300000000000199-block-chunk.msgpack.xz', file_blockchain.file_optimization_max_depth) }}``

Block chunk file structure
--------------------------

Block chunk filename format
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Filename template is "``{{ file_blockchain.block_chunk_template.format(start='x' *  file_blockchain.order_of_block, end='y' *  file_blockchain.order_of_block) }}[.compressor]``"
where "``{{ 'x' *  file_blockchain.order_of_block }}``" is the first block number of the block chunk file,
"``{{ 'y' *  file_blockchain.order_of_block }}``" is the last block number of the block chunk file,
and "``.compressor``" represents compression algorithm, if present.

Filename example of block chunk file for block from 100 to 199 compressed with LZMA compression: ``{{ file_blockchain.get_block_chunk_filename(100, 199) }}``


Block chunk file format
^^^^^^^^^^^^^^^^^^^^^^^

Block chunk file contains multiple streamed serialized MessagePack objects. Each block is
serialized and the MessagePack_ binary appended to the file. It is NOT a serialized array
of blocks.

Block structure
^^^^^^^^^^^^^^^

Block types
"""""""""""

.. list-table::
   :header-rows: 1

   * - Type
     - Value
{% for key, name in block_types.items() %}
   * - {{ name }}
     - "{{ key }}"
{% endfor %}

{% for model in block_models %}
{{ model.__name__ }}
{{ '"' * model.__name__.__len__() }}

{{ model.get_docstring() }}

{% if model.get_field_names() -%}
.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Type
     - Example value
     - Is mandatory
{% for field_name in model.get_field_names() %}
   * - {{ field_name }}
     - {{ model.get_field_docstring(field_name) }}
     - {{ model.get_field_type_representation(field_name) }}
     - {{ model.get_field_example_value(field_name)|default('', True) }}
     - {% if model.is_serialized_optional_field(field_name) %}No{% else %}Yes{% endif %}
{%- endfor %}
{% endif %}
{% endfor %}

SignedChangeRequestMessage
""""""""""""""""""""""""""

SignedChangeRequestMessage is a base type for the following subtypes:

{% for model in signed_change_request_message_subtypes %}
- `{{ model.__name__ }}`_
{% endfor %}

{% for model in signed_change_request_message_models %}
{{ model.__name__ }}
{{ "'" * model.__name__.__len__() }}

{{ model.get_docstring() }}

{% if model in sample_block_map %}
**Block example**

.. code-block:: JSON

    {{ sample_block_map[model].serialize_to_dict() | tojson(indent=4) | indent }}

**Compacted block example**

Byte arrays are shown as hexadecimals for representation purposes:

.. code-block:: JSON

    {{ sample_block_map[model].to_compact_dict(compact_keys=True, compact_values=False) |
       tojson(indent=4) | indent }}

{% endif %}

**Format description**

{% if model.get_field_names() -%}
.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Type
     - Example value
     - Is mandatory
{% for field_name in model.get_field_names() %}
   * - {{ field_name }}
     - {{ model.get_field_docstring(field_name) }}
     - {{ model.get_field_type_representation(field_name) }}
     - {{ model.get_field_example_value(field_name)|default('', True) }}
     - {% if model.is_serialized_optional_field(field_name) %}No{% else %}Yes{% endif %}
{%- endfor %}
{% endif %}
{% endfor %}

Common types and models structure
=================================

hexstr
------
A string of hexadecimal characters

datetime
--------
A string of `ISO formatted <https://en.wikipedia.org/wiki/ISO_8601>`_ UTC datetime without timezone part.

{% for model in common_models %}
{{ model.__name__ }}
{{ "-" * model.__name__.__len__() }}

{{ model.get_docstring() }}

{% if model.get_field_names() -%}
.. list-table::
   :header-rows: 1

   * - Name
     - Description
     - Type
     - Example value
     - Is mandatory
{% for field_name in model.get_field_names() %}
   * - {{ field_name }}
     - {{ model.get_field_docstring(field_name) }}
     - {{ model.get_field_type_representation(field_name) }}
     - {{ model.get_field_example_value(field_name)|default('', True) }}
     - {% if model.is_serialized_optional_field(field_name) %}No{% else %}Yes{% endif %}
{%- endfor %}
{% endif %}
{% endfor %}

.. Links targets
.. _MessagePack: https://msgpack.org/
