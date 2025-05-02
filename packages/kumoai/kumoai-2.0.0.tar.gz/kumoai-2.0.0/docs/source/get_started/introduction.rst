.. _intro_by_example:

Introduction by Example
=======================

.. note::
  This tutorial is also available as a
  `Google Colab <https://colab.research.google.com/drive/1WOyMm8gdT1lwrmgRjJUSwb940sn6jUM4?usp=sharing>`__,
  which you can copy and run end-to-end with your API key.


**The Kumo platform makes machine learning on relational data simple, performant,
and scalable.** The Kumo SDK exposes an intuitive and composable interface atop
the Kumo platform, enabling you to easily integrate Kumo with your existing
iteration, testing, and production workflows.

Here, we shortly introduce the fundamental concepts of Kumo, and their use in
the Kumo SDK. We motivate this use-case with a simple and well-known business
use-case: predicting customer lifetime value from past behavior (represented
as a relational dataset of customers, product stock, and transactions). The
full dataset is located at ``s3://kumo-public-datasets/customerltv_mini/``;
please feel free to follow along.

.. contents::
    :local:

.. note::
    For a complete overview of the Kumo platform, please also read the `Kumo
    documentation <https://docs.kumo.ai/docs/welcome-to-kumo>`__ alongside this
    document.

Initializing the SDK
~~~~~~~~~~~~~~~~~~~~

Please refer to :ref:`installation` for information about installing the SDK,
and :ref:`key_management` to set up the SDK to work with your Kumo platform.
Once you have completed these sections, you should be able to run the
:meth:`~kumoai.init` method succesfully, which will look like either

.. code-block:: python

    import kumoai as kumo
    kumo.init(url="<url>/api", api_key="<api_key>")

for the Kumo SaaS and Databricks edition, or

.. code-block:: python

    import kumoai as kumo
    credentials = {
        "user": <your username>,
        "password": <your password>,
        "account": <your account>,
    }
    kumo.init(url="https://<kumo_spcs_deployment_url>/api", snowflake_credentials=credentials)

for the Kumo Snowpark Container Services edition.

Inspecting Source Tables
~~~~~~~~~~~~~~~~~~~~~~~~

Once you've initialized the SDK, the first step to working with your data is
defining a connector to your source tables. The Kumo SDK supports creating
connectors to data on Amazon S3 with a :class:`~kumoai.connector.S3Connector`,
Snowflake with a :class:`~kumoai.connector.SnowflakeConnector`, or Databricks
with a :class:`~kumoai.connector.DatabricksConnector`. Here, we
work with data on S3, but equivalent steps can be taken with other supported
data warehouses. Connecting multiple tables across multiple connectors is
supported (for example, you can use S3 and Snowflake together).

.. warning::
    If you are using the Kumo Snowpark Container Services edition, only
    :class:`~kumoai.connector.SnowflakeConnector` is supported.

Creating a connector to a dataset on S3 is as simple as specifying the root
directory of your data:

.. code-block::

    connector = kumo.S3Connector(root_dir="s3://kumo-public-datasets/customerltv_mini/")

after which tables can be accessed with Python indexing semantics, or with the
:meth:`~kumoai.connector.Connnector.table` method. The following code
represents three different ways to access the tables behind the
``customerltv_mini`` directory; all are equivalent.

.. code-block::

    # Access the 'customer' table by indexing into the connector:
    customer_src = connector['customer']

    # Access the 'transaction' table by explicitly calling the `.table`
    # method on the connector:
    transaction_src = connector.table('transaction')

    # Create a connector without a root directory, and obtain a table by
    # passing the full table path:
    stock_src = kumo.S3Connector().table('s3://kumo-public-datasets/customerltv_mini/stock')

The tables :obj:`customer_src`, :obj:`transaction_src` and :obj:`stock_src` are
objects of type :class:`~kumoai.connector.SourceTable`, which support basic
operations to verify the types and raw data you have connected to Kumo. While
the package reference provides a full set of details, some examples include
viewing a sample of the source data (as a :class:`~pandas.DataFrame`)
or viewing the source columns and their data types:

.. code-block:: python

    print(customer_src.head())
    >>
        CustomerID
    428    16909.0
    312    14002.0
    306    17101.0
    141    13385.0
    273    14390.0

    print(len(transaction_src.columns))
    >> 8

.. note::

    For tables with semantically meaningful text columns, Kumo supports a
    language model integration that allows for modeling to utilize powerful
    large language model embeddings, *e.g.* from OpenAI's GPT. Please see
    :meth:`~kumoai.connector.SourceTable.add_llm` for more details.

Alongside viewing source table raw data, you can additionally perform data
transformations with your own data platform directly alongside the Kumo SDK.
For example, with ``pyspark``, it is possible to transform the transactions
table as follows:

.. code-block:: python

    from pyspark.sql.functions import col

    root_dir = "s3://kumo-public-datasets/customerltv_mini/"

    # An output directory (e.g. on S3) that you can write to, and Kumo can
    # read from:
    output_dir = ...

    # Perform transformation with Spark
    spark.read.parquet(f"{root_dir}/transaction") \
        .withColumn("TotalPrice", col("Quantity") * col("UnitPrice")) \
        .write.format("parquet").option("header","true").mode("Overwrite") \
        .save(f"{output_dir}/transaction_altered/")

    # Access the altered table from the same connector:
    assert S3Connector(output_dir).has_table("transaction_altered")
    print("Transaction price: ", connector["transaction_altered"].head(num_rows=2)["TotalPrice"])

Creating Kumo Tables
~~~~~~~~~~~~~~~~~~~~~

Once you've connected your source tables and applied any necessary
transformations, you can next construct a :class:`~kumoai.graph.Graph`
consisting of :class:`~kumoai.graph.Table` s.

A Kumo Graph represents a connected set of Tables, with each table fully
specifying the relevant metadata (including selected source columns, column
data type and semantic type, and relational constraint information) of
SourceTables for modeling purposes.

A :class:`~kumoai.graph.Table` can be constructed from a
:class:`~kumoai.connector.SourceTable` in multiple ways, and modified as
necessary. The simplest approach is to call
:meth:`~kumoai.graph.Table.from_source_table`, as follows:

.. code-block:: python

    # NOTE if `columns` is not specified, all source columns are included:
    customer = kumo.Table.from_source_table(
        source_table=customer_src,
        primary_key='CustomerID',
    ).infer_metadata()

    transaction = kumo.Table.from_source_table(
        source_table=transaction_src,
        time_column='InvoiceDate',
    ).infer_metadata()

Here, we ask Kumo to convert source tables to Kumo tables, and infer all
unspecified metadata. To verify the metadata that was inferred for these
tables, we can call the :py:attr:`~kumoai.graph.Table.metadata` property, which shows
a condensed view of the infromation associated with a table:

.. code-block:: python

    # Formatted with `tabulate`:
    >>> print(customer.metadata)

    +----+-----------+---------+---------+------------------+------------------+----------------------+
    |    | name      | dtype   | stype   | is_primary_key   | is_time_column   | is_end_time_column   |
    |----+-----------+---------+---------+------------------+------------------+----------------------|
    |  0 | StockCode | string  | ID      | True             | False            | False                |
    +----+-----------+---------+---------+------------------+------------------+----------------------+

If any column properties are not specified to your liking, you can additionally
edit these properties by accessing their names and modifying them in the table.

You can also choose to specify the table from the ground-up, optionally
inferring metadata for any non-fully-specified columns:

.. code-block:: python

    stock = kumo.Table(
        source_table=stock_src,
        columns=dict(name='StockCode', stype='ID'),  # will infer dtype='string'
        primary_key='StockCode',
    ).infer_metadata()

    # Validate the table's correctness:
    stock.validate(verbose=True)

No matter how you create your table, :class:`~kumoai.graph.Table` additionally
exposes methods to inspect a table's metadata and adjust included columns, data
types, semantic types, and other relevant metadata.

.. code-block:: python

    # Set and access a data type for a column ("StockCode") in the stock table;
    # this can be done for all properties of the table.
    stock.column("StockCode").dtype = "string"
    print(stock["StockCode"].dtype)

Note that :meth:`~kumoai.graph.Table.column` returns a
:class:`~kumoai.graph.Column` object, which contains the relevant metadata for
the column of a table.

Creating a Graph
~~~~~~~~~~~~~~~~

After defining all :class:`~kumoai.graph.Table` objects, we next construct a
:class:`~kumoai.graph.Graph` over these tables. A Graph connects the Tables
by their primary key / foreign key relationships, and can be constructed by
specifying the tables that partake in it along with these relationships.

.. code-block:: python

    graph = kumo.Graph(
        # These are the tables that participate in the graph: the keys of this
        # dictionary are the names of the tables, and the values are the Table
        # objects that correspond to these names:
        tables={
            'customer': customer,
            'stock': stock,
            'transaction': transaction,
        },

        # These are the edges that define the primary key / foreign key
        # relationships between the tables defined above. Here, `src_table`
        # is the table that has the foreign key `fkey`, which maps to the
        # table `dst_table`'s primary key:`
        edges=[
            dict(src_table='transaction', fkey='StockCode', dst_table='stock'),
            dict(src_table='transaction', fkey='CustomerID', dst_table='customer'),
        ],
    )

    # Validate the graph's correctness:
    graph.validate(verbose=True)

Writing a Predictive Query
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you've set up the Graph of your Tables, you can define a machine learning
problem as a Kumo :class:`~kumoai.pquery.PredictiveQuery` on your Graph.
Predictive queries are written using the predictive query language (PQL), a
concise SQL-like syntax that allows you to define a model for a new business
problem. For information on the construction of a query string, please visit the
Kumo `documentation <https://docs.kumo.ai/docs/pquery-structure/>`__.

In this example, we'll be predicting customer lifetime value, which can be
modeled as a regression problem to predict the maximum quantity of transactions
for each customer over the next 30 days, given that the customer has made
over 15 units worth of transactions in the past 7 days:

.. code-block:: python

    pquery = kumo.PredictiveQuery(
        graph=graph,
        query=(
            "PREDICT MAX(transaction.Quantity, 0, 30)\n"
            "FOR EACH customer.CustomerID\n"
            "ASSUMING SUM(transaction.UnitPrice, 0, 7, days) > 15"
        ),
    )

    # Validate the predictive query syntax:
    pquery.validate(verbose=True)

Training a Model and Generating Predictions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To recap: starting with raw data (in the form of
:class:`~kumoai.connector.SourceTable` objects), we created a
:class:`~kumoai.graph.Graph` consisting of Kumo :class:`~kumoai.graph.Table`
objects, with the graph specifying relationships between the tables and the
tables specifying machine learning metadata for each table. We next defined a
:class:`~kumoai.pquery.PredictiveQuery` to represent a machine learning problem
as a statement in Kumo's querying language.

We can now train a Kumo model with two simple steps:

.. code-block:: python

    model_plan = pquery.suggest_model_plan()
    trainer = kumo.Trainer(model_plan)
    training_job = trainer.fit(
        graph=graph,
        train_table=pquery.generate_training_table(non_blocking=True),
        non_blocking=False,
    )
    print(f"Training metrics: {training_job.metrics()}")

Let's step through each of these lines of code. Line 1 defines the Kumo modeling
plan that the predictive query suggests for use in training. You can either use
the default model plan directly (as is done above), or can adjust any of the
parameters to your liking. Line 2 creates a :class:`~kumoai.trainer.Trainer`
object initialized with the model plan, which manages the training of your
query. Line 3's call to :meth:`~kumoai.trainer.Trainer.fit` accepts a graph
(created above) and a training table (produced by the predicitve query), and
trains a model. Line 4 outputs metrics for the job -- that's it!

.. note::

    The Kumo SDK makes extensive use of ``non_blocking`` as an optional
    parameter for long-running operations. Setting this flag to ``True``
    lets a long-running operation return immediately, returning a ``Future``
    object that tracks the operation as it runs in the background. Setting this
    flag to ``False`` lets a long-running operation wait until its completion
    (success or failure) before returning. Please see the package reference
    for more detials.

Once a model has been trained, we can use it to generate batch predictions that
we can write to an external data source. This can be achieved with the
following code:

.. code-block:: python

    # Predict on your trained model:
    # For v1.4 and above:
    from kumoai.artifact_export.config import OutputConfig
    # For v1.3 and below (backward compatible):
    # from kumoai.trainer.config import OutputConfig
    
    prediction_job = trainer.predict(
        graph=graph,
        prediction_table=pquery.generate_prediction_table(non_blocking=True),
        output_config=OutputConfig(
            output_types={'predictions', 'embeddings'},
            output_connector=connector,
            output_table_name='kumo_predictions',
        ),
        training_job_id=training_job.job_id,  # use our training job's model
        non_blocking=False,
    )
    print(f'Batch prediction job summary: {prediction_job.summary()}')

which will generate batch predictions to the same connector that contained our
source data.

Next Steps
~~~~~~~~~~

While this example covered many of the core concepts underpinning the Kumo
SDK, the SDK provides much more advanced functionality to help improve model
iteration speed, evaluate champion/challenger models in production use-cases,
integrate cleanly with upstream and downstream data pipelines, and more. Please
avail yourself of the full set of package documentation and reach out to your
sales engineer with any further questions, comments, and concerns.


Full Code Example
~~~~~~~~~~~~~~~~~

A full code example on the CustomerLTV dataset discussed above follows.

.. code-block:: python

    import kumoai as kumo

    # Initialize the SDK:
    kumo.init(url="https://<customer_id>.kumoai.cloud/api", api_key=API_KEY)

    # Create a Connector:
    connector = kumo.S3Connector("s3://kumo-public-datasets/customerltv_mini_integ_test/")

    # Create Tables from SourceTables:
    customer = kumo.Table.from_source_table(
        source_table=connector.table('customer'),
        primary_key='CustomerID,
    ).infer_metadata()

    stock = kumo.Table.from_source_table(
        source_table=connector.table('stock'),
        primary_key='StockCode,
    ).infer_metadata()

    transaction = kumo.Table.from_source_table(
        source_table=connector.table('transaction'),
        time_column='InvoiceDate',
    ).infer_metadata()

    # Create a Graph:
    graph = kumo.Graph(
        tables={
            'customer': customer,
            'stock': stock,
            'transaction': transaction,
        },
        edges=[
            dict(src_table='transaction', fkey='StockCode', dst_table='stock'),
            dict(src_table='transaction', fkey='CustomerID', dst_table='customer'),
        ],
    )

    # Validate the Graph:
    graph.validate(verbose=True)

    # Create a Predictive Query on the Graph:
    pquery = kumo.PredictiveQuery(
        graph=graph,
        query=(
            "PREDICT MAX(transaction.Quantity, 0, 30)\n"
            "FOR EACH customer.CustomerID\n"
            "ASSUMING SUM(transaction.UnitPrice, 0, 7, days) > 15"
        ),
    )

    # Validate the predictive query syntax:
    pquery.validate(verbose=True)

    # Create a modeling plan, and a Trainer object to train a model:
    model_plan = pquery.suggest_model_plan()
    trainer = kumo.Trainer(model_plan)

    # Train a model:
    training_job = trainer.fit(
        graph=graph,
        train_table=pquery.generate_training_table(non_blocking=True),
        non_blocking=False,
    )
    print(f"Training metrics: {training_job.metrics()}")

    # Predict on your trained model:
    # For v1.4 and above:
    from kumoai.artifact_export.config import OutputConfig
    # For v1.3 and below (backward compatible):
    # from kumoai.trainer.config import OutputConfig
    
    prediction_job = trainer.predict(
        graph=graph,
        prediction_table=pquery.generate_prediction_table(non_blocking=True),
        output_config=OutputConfig(
            output_types={'predictions', 'embeddings'},
            output_connector=connector,
            output_table_name='kumo_predictions',
        ),
        training_job_id=training_job.job_id,  # use our training job's model
        non_blocking=False,
    )
    print(f'Batch prediction job summary: {prediction_job.summary()}')
