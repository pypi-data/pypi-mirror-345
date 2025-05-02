kumoai.graph
============

.. currentmodule:: kumoai.graph

A Kumo :class:`~kumoai.graph.Graph` is a fundamental concept within the Kumo
SDK; it links multiple :class:`~kumoai.graph.Table` objects (created from
:class:`~kumoai.connector.SourceTable` objects). Graphs represent relationships
between tables that are useful for a specific business problem, and can be used
as input to predictive queries and training jobs.

.. image:: ../../assets/data_source.png

Column
------

The metadata information of each column in a Table is represented by the Column
object. A Column within a Table can be accessed with
:meth:`~kumoai.graph.Table.column`, and can be modified by adjusting its
properties.

Related: :class:`~kumoai.Dtype`, :class:`~kumoai.Stype`.

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   Column

Table
-----

A Table represents the metadata information of a table in your relational data
model; this includes information of each :class:`~kumoai.graph.Column`, and
table-level information including its primary key, time column, and end time
column, should they exist.

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   Table

Graph
-----

A Graph represents a full relational schema over a set of Tables; this includes
each table participating in the graph along with the primary key / foreign key
relationships between these tables.

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   Graph
   Edge
   GraphHealthStats
