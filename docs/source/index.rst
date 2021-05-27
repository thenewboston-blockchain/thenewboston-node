Thenewboston blockchain documentation
=====================================


1. File system general structure
--------------------------------

Blockchain and root account files are stored on the filesystem
in two separate subdirectories:

- *"{{ file_blockchain.blocks_subdir }}"* for blockchain
- *"{{ file_blockchain.account_root_file_subdir }}"* for root account files

Blocks and root account files are serialized to MessagePack_ format and
saved as *.msgpack* files. The files can also be compressed using algorithms:

{% for compressor in file_blockchain.compressors %}
- {{ compressor }}
{% endfor %}

In this case, the corresponding extension is added to file like
*example.msgpack.gz*. The exact compression method is chosen to get the best
compression in each case.


2. File path optimization
---------------------------

When the number of block files or root account files is too high it gets
inefficient to keep them in one
directory because it requires O(n) operations to look for a file in that
directory. To overcome this issue all the files are stored in a tree-like file
structure so that every file is stored inside
*{{ file_blockchain.file_optimization_max_depth }}* subdirectories.
Directory names are taken from the file name parts.

Example:
    A file named *0123456789.msgpack.xz* will be saved to
    *{{ file_blockchain.make_optimized_file_path('0123456789.msgpack.xz',
    file_blockchain.file_optimization_max_depth) }}*


3. Blockchain file structure
------------------------------

Validated blocks are stored in chunks of *{{ file_blockchain.block_chunk_size }}*
blocks. Block numeration starts with *0* and each subsequent block number is
incremented by *1*. Every block chunk is stored in a file named according to
the first block and the last block. To get a valid block chunk file name:

#. The first and last block numbers are converted to a string and filled with leading
   zeros to get a string *{{ file_blockchain.order_of_block }}* characters long.
#. The results are used to format the template
   *"{{ file_blockchain.block_chunk_template }}"*


Example:
    Blocks from *100* till *199* will be saved to
    *{{ file_blockchain.get_block_chunk_filename(100, 199) }}*

The steps needed to extract block data from the file:

#. *(OPTIONAL)* Decompress file if it's compressed
#. Make sequential read block by block using MessagePack_ tools

Block structure in MessagePack_ format can be translated to JSON.
Coin transfer block example in JSON looks like this:

.. code-block:: JSON

    {{ models.block.sample.to_compact_dict(compact_keys=True, compact_values=False) |
       tojson(indent=4) | indent }}

Keys are in a non human-readable format in this example. This is done to free
up file system space as much as possible. To make it more convenient let's
substitute short keys to full-size keys (See `Appendix A. Data structures short key map`_):

.. code-block:: JSON

    {{ models.block.sample.to_dict() | tojson(indent=4) | indent }}


4. Block schema
---------------

{% for model_doc in models.block.docs %}
.. _{{ model_doc.model }}:

**{{ model_doc.model }}**

{{ model_doc.docstring }}

{% for attr in model_doc.attrs %}

- *{{ attr.name }}*: {{ attr.type }}{% if attr.is_optional %}, *optional* {% endif %}
    {{ attr.docstring }}

{% endfor %}

{% endfor %}


5. Root account file structure
--------------------------------

Root account file is a snapshot of all account balances at any point in time.
At the snapshot root account a file is serialized to MessagePack_
and saved to file named as block number at which the snapshot is taken.
Then filename is prepended with *0* to correspond to the length of
*{{ file_blockchain.order_of_account_root_file }}*. Then it's used to format
the string *{{ file_blockchain.account_root_file_template }}*.

Example:
    Root account file at block number 5100 will be saved to
    *{{ file_blockchain.get_account_root_filename(5100) }}*.

There must be an initial root account file on the network startup. It's named
*{{ file_blockchain.get_account_root_filename(None) }}*.

Root account files can be converted to JSON the same way it's done for block
files. Let's see an example root account file:

.. code-block:: JSON

    {{ models.root_account_file.sample.to_compact_dict(compact_keys=True, compact_values=False) |
       tojson(indent=4) | indent }}


With expanded keys (See `Appendix A. Data structures short key map`_):

.. code-block:: JSON

    {{ models.root_account_file.sample.to_dict() | tojson(indent=4) | indent }}


6. Root account file schema
---------------------------

{% for model_doc in models.root_account_file.docs %}
.. _{{ model_doc.model }}:

**{{ model_doc.model }}**

{{ model_doc.docstring }}

{% for attr in model_doc.attrs %}

- *{{ attr.name }}*: {{ attr.type }}{% if attr.is_optional %}, *optional* {% endif %}
    {{ attr.docstring }}

{% endfor %}

{% endfor %}


Appendix A. Data structures short key map
-----------------------------------------

.. list-table::
   :header-rows: 1

   * - Long key
     - Short key

{% for long_key, short_key in compact_key_map %}
   * - {{ long_key }}
     - {{ short_key }}
{% endfor %}
.. Links targets
.. _MessagePack: https://msgpack.org/
