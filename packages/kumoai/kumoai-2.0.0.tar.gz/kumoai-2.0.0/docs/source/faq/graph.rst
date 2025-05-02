.. _faq_graphs:

Working With Graphs
===================

Here, we discuss common patterns for working with graphs in the Kumo
SDK. Graphs are created from :class:`~kumoai.graph.Table` objects, and
represent the relational (primary key / foreign key) connections between
their constituent tables. These specified relationships are used by Kumo
to learn across multiple tables, in a way that derives optimal cross-table
representations for your specified task and avoids manual feature engineering.
The metadata required for graph creation is simple:

* Each constituent :class:`~kumoai.graph.Table`, with a corresponding name
  to be used within the Graph.
* The relationships between the Tables, specifying the
  source table (table with the foreign key), name of the foreign key, and
  destination table (table with the primary key corresponding to the foreign
  key).

.. contents:: FAQ
    :local:

How do I create a graph?
------------------------

Creating a graph requires creating all of the :class:`~kumoai.graph.Table`
objects that participate in the graph; see :ref:`faq_tables` for answers to
frequently asked questions for table creation.

Once you have created all of your tables, you can create a
:class:`~kumoai.graph.Graph` explicitly by passing the relevant arguments to
the constructor:

.. code-block:: python

    table_1 = kumoai.Table(...)
    table_2 = kumoai.Table(...)  # assume this table has a primary key.
    table_3 = kumoai.Table(...)

    graph = kumoai.Graph(
        # A dictionary mapping the names of the tables to the table objects:
        tables = {
            'table_1_name': table_1,
            'table_2_name': table_2,
            'table_3_name': table_3,
        },

        # A list of edges, either specified as kumoai.Edge objects or as
        # dictionaries, that describe the relationships between the tables.
        # Note that edges are always bidirectional:
        edges = [
            kumoai.Edge('table_1_name', 'table_1_fkey', 'table_2_name'),
            dict(src_table='table_3_name', fkey='table_3_fkey', dst_table='table_2_name'),
        ]
    )

In the above graph, we have included three tables, and two primary/foreign key
relationships between them: one from a foreign key in table 1 to the primary
key in table 2, and another from a foreign key in table 3 to the primary key
in table 2.

How do I edit a graph?
----------------------

Multiple methods exist to support adding/removing tables and edges in a graph.
Concretely:

* :meth:`~kumoai.graph.Graph.add_table` adds a table to a Graph
* :meth:`~kumoai.graph.Graph.remove_table` removes a table from a Graph
* :meth:`~kumoai.graph.Graph.link` adds an edge between two tables in a Graph
* :meth:`~kumoai.graph.Graph.unlink` removes an edge from a Graph

What does it mean to snapshot a graph?
--------------------------------------

The :meth:`~kumoai.graph.Graph.snapshot` method allows you to ingest all of the
tables in a graph, so that multiple calls to train a model will use the same
version of data even while the data in the source connector changes.
Snapshotting a graph is also required to view that graph's edge health
statistics, which contain information about the number of matches between
primary and foreign keys across all edges in the graph.
