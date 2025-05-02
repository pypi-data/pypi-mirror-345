kumoai.connector
================

.. currentmodule:: kumoai.connector

The Kumo Connector and SourceTable interfaces allow users to access and
inspect raw data behind backing connectors. These data can be used to create
:class:`~kumoai.graph.Table` and :class:`~kumoai.graph.Graph` objects, which
are for machine learning downstream.

.. image:: ../../assets/data_source.png

Uploading Your Own Data
-----------------------

Kumo supports uploading your own tables. Each table must be < 1 GB in size,
and must be a single Parquet or CSV file on your local machine. Uploaded
tables can be used in Kumo with :class:`~kumoai.connector.FileUploadConnector`,
and can be deleted with :meth:`~kumoai.connector.delete_uploaded_table`.

.. autosummary::
   :nosignatures:
   :toctree: ../generated

    upload_table
    delete_uploaded_table

Connector
---------

Connectors support connecting Kumo with data in a backing data store. The
Kumo SDK currently supports the Amazon S3 object store, the BigQuery
data warehouse, the Snowflake data warehouse, and the Databricks data
warehouse as stores for source tables.

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   S3Connector
   SnowflakeConnector
   DatabricksConnector
   BigQueryConnector
   FileUploadConnector

Source Data
-----------

Tables accessed from connectors are represented as
:class:`~kumoai.connector.SourceTable` objects,
with source columns represented as
:class:`~kumoai.connector.SourceColumn` objects.

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   SourceTable
   SourceTableFuture
   LLMSourceTableFuture
   SourceColumn
