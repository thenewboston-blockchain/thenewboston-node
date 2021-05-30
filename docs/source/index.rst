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
''''''''''''''''''''''''''''''''
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
''''''''''''''''''''''''''''''''''''''''''''''''

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

{% for model_doc in models.blockchain_state.docs %}
{{ model_doc.model }}
{{ "'" * model_doc.model.__len__() }}

{{ model_doc.docstring }}

.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
     - Is mandatory

{% for attr in model_doc.attrs %}
   * - {{ attr.name }}
     - {% if attr.type in ('string', 'integer', 'datetime', 'object', 'bool', 'array') %}{{ attr.type }}{% else %}`{{ attr.type }}`_{% endif %}
     - {{ attr.docstring }}
     - {% if attr.is_optional %}No{% else %}Yes{% endif %}
{% endfor %}
{% endfor %}

Account root file example
'''''''''''''''''''''''''

.. code-block:: JSON

    {{ models.blockchain_state.sample.to_dict() | tojson(indent=4) | indent }}

Compacted account root file example
'''''''''''''''''''''''''''''''''''

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

{% for model_doc in models.block.docs %}
{{ model_doc.model }}
{{ "'" * model_doc.model.__len__() }}

{{ model_doc.docstring }}

.. list-table::
   :header-rows: 1

   * - Name
     - Type
     - Description
     - Is mandatory

{% for attr in model_doc.attrs %}
   * - {{ attr.name }}
     - {% if attr.type in ('string', 'integer', 'datetime', 'object', 'bool', 'array') %}{{ attr.type }}{% else %}`{{ attr.type }}`_{% endif %}
     - {{ attr.docstring }}
     - {% if attr.is_optional %}No{% else %}Yes{% endif %}
{% endfor %}
{% endfor %}

Block example
'''''''''''''

.. code-block:: JSON

    {{ models.block.sample.to_dict() | tojson(indent=4) | indent }}

Compacted block example
'''''''''''''''''''''''

Byte arrays are shown as hexadecimals for representation purposes:

.. code-block:: JSON

    {{ models.block.sample.to_compact_dict(compact_keys=True, compact_values=False) |
       tojson(indent=4) | indent }}

.. Links targets
.. _MessagePack: https://msgpack.org/
