.. _faq_tables:

Working With Tables
===================

Here, we discuss common patterns for working with tables in the Kumo
SDK. Tables are created from :class:`~kumoai.connector.SourceTable` objects;
while SourceTables simply represent a view of data behind a backing connector,
Tables contain additional metadata and information for the Kumo machine
learning platform. Concretely, this additional information includes:

* Each included column's ``name``, ``dtype`` (data type), and ``stype``
  (semantic type). For information about what types of columns to select, please
  reference `this guide <https://docs.kumo.ai/docs/column-selection>`__. For
  information on how to choose data and semantic types, please reference `this
  guide <https://docs.kumo.ai/docs/column-preprocessing>`__.
* The primary key of the table, if present
* The time column of the table, if present
* The end time column of the table, if present

.. contents:: FAQ
    :local:

How do I create a table?
------------------------

Creating tables requires a :class:`~kumoai.connector.SourceTable` object, which
can be obtained from any :class:`~kumoai.connector.Connector`, either with
Python indexing semantics (*e.g.* ``connector[table_name]``) or with
:meth:`~kumoai.connector.Connector.table`. After inspecting the source table
(*e.g.* with :meth:`~kumoai.connector.SourceTable.head`) to verify its data
matches your expectations, you can either create a table implicitly with
:meth:`~kumoai.graph.Table.from_source_table` or explicitly by
specifying each field in the :class:`~kumoai.graph.Table` constructor. We show
both methods below:

**Implicit Creation.** Implicit creation lets you create a
:class:`~kumoai.graph.Table` from a :class:`~kumoai.connector.SourceTable` in
one line:

.. code-block:: python

    table = kumoai.Table.from_source_table(source_table)

which will use all columns in the source table by default. You can customize
this and additionally specify any further metadata as part of this method
call; please see the documentation of
:meth:`~kumoai.graph.Table.from_source_table` for more details.

After this call, ``table`` will be of type :class:`~kumoai.graph.Table`, but
it will not have all metadata specified for its constituent columns (*e.g.*
``dtype`` and ``stype``). You can either explictly specify this metadata later
(see "How do I edit a table?", or let Kumo infer it with
:meth:`~kumoai.graph.Table.infer_metadata`).

**Explicit Creation.** If you want to be more precise about table creation,
you can choose to manually create a table with the :class:`~kumoai.graph.Table`
constructor. This lets you specify (partially or fully) any of the attributes
that a Table specifies:

.. code-block:: python

    table = kumoai.Table(
        source_table = source_table,
        columns = [
            kumoai.Column('string_col', 'string', 'text'),
            # Columns can also be specified as dictionaries. Note here that the
            # stype is left unspecified: this is OK, as long as we specify it
            # later before using the Table in a Predictive Query:
            dict(name='int_col', dtype='int')
        ],
        # The name of the primary key column, if it exists:
        primary_key = 'int_col',
    )

Similar to implicit creation, a table created this way may not fully specify
all of its consituent elements (*e.g.* the semantic type of ``int_col`` was
left unspecified above). You can either explictly specify this metadata later
(see "How do I edit a table?", or let Kumo infer it with
:meth:`~kumoai.graph.Table.infer_metadata`).

How do I view the metadata of a table?
--------------------------------------

:class:`~kumoai.graph.Table` provides a convenience property for you to view
its metadata: :py:attr:`~kumoai.graph.Table.metadata`, which outputs a
:class:`~pandas.DataFrame` object containing a summary of every included
column's name, type, and role.

Individual methods are also provided to access column and table-level metadata;
please see the package reference for more details.


How do I edit a table?
----------------------

Editing a :class:`~kumoai.graph.Table` is simple and Pythonic: every property
is modifiable with the typical Python style, for both column and table-level
attributes. We share some examples below:

Editing a table's primary key (*note*: the primary key must already be a column
of the table):

.. code-block:: python

    # Set the primary key:
    table.primary_key = 'new_primary_key'

    # Unset (remove) the primary key:
    table.primary_key = None

    # Check if a table has a primary key:
    print(f"Table has primary key? {table.has_primary_key()}"")


Adding a column to a table, and editing its metadata:

.. code-block:: python

    # Adding a new column named 'col':
    table.add_column(name="col", dtype="int")

    # Editing the column's semantic type:
    table.column("col").stype = "categorical"

    # Removing the column altogether:
    table.remove_column("col")


How do I save a table for future usage?
---------------------------------------

Tables do not have names in the Kumo SDK; a table is fully specified by its
configuration in code. That is, if you use the same table configuration in
two different notebooks, they will refer to the same table object in the
Kumo backend. And if you edit a table, it will refer to a new object in
the Kumo backend, independent of other tables.

.. note::

    We encourage users to fully specify their tables in production code,
    to avoid unexpected re-inferrals of metadata.
