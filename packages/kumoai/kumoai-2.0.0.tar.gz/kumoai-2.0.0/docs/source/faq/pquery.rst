.. _faq_pquery:

Writing Predictive Queries
==========================

Here, we discuss the :class:`~kumoai.pquery.PredictiveQuery` object, its usage,
and how to frame your business problem in Kumo's predictive query language
(PQL). Predictive queries can be created on a :class:`~kumoai.graph.Graph` and
a :obj:`query` string; the query should reference the names of tables in the
graph, and should represent a predictive problem over these tables.

.. note::

    For full documentation on the predictive query language and in-depth
    examples, please refer to `the predictive query
    tutorial <https://docs.kumo.ai/docs/tutorial>`__.

.. contents:: FAQ
    :local:

How do I start writing a predictive query?
------------------------------------------

You can start writing a predictive query in one line of code: simply create a
:class:`~kumoai.pquery.PredictiveQuery` object on a graph, and fill in the
:obj:`query` string as below:

.. code-block:: python

    graph = kumoai.Graph(...)
    pquery = kumoai.PredictiveQuery(graph=graph, query="<your query here>")

Please refer to `the predictive query tutorial
<https://docs.kumo.ai/docs/tutorial>`__ for more information on the query
language, to learn how to use PQL to solve your business problem.

How do I confirm my predictive query is correct?
------------------------------------------------

There are often many ways to represent the same business problem, each of which
translates to its own predictive query and machine learning task. With the
Kumo platform, you can experiment with all of these formulations, with
minimal changes to your end-to-end flow.

For any given predictive query, the SDK offers multiple quick ways to ensure
that the query matches your expectations.

* For syntax validation, :meth:`~kumoai.pquery.PredictiveQuery.validate` will
  return any errors with query formulation that can be used to guide your
  query writing.
* For functionality validation,
  :meth:`~kumoai.pquery.PredictiveQuery.get_task_type` will return the `task
  type <https://docs.kumo.ai/docs/task-types>`__ of a predictive query, to
  confirm that it matches the machine learning problem you are expecting to
  solve.

For a more in-depth look at the training and prediction data your query
produces, you can leverage the :meth:`kumoai.pquery.TrainingTable.data_df` and
the :meth:`kumoai.pquery.PredictionTable.data_df` methods after generating the
corresponding data (see below), which allow you to inspect the generated data
that Kumo will train its graph machine learning models on.

How do I use a predictive query for model training?
---------------------------------------------------

Once you've defined a predictive query, you can leverage two methods to
generate a training table associated with this predictive query, which
is used in :meth:`~kumoai.trainer.Trainer.fit` to fit a model.

First, you can (optionally) suggest a training table generation plan with
:meth:`~kumoai.pquery.PredictiveQuery.suggest_training_table_plan`, which
returns a training table generation plan that can be customized for
advanced use-cases (*e.g.* to change the split). Detailed documentation
for these options is
`here <https://docs.kumo.ai/docs/advanced-operations#training-table-generation>`__.
If you do not require a custom training table generation plan, the default
(Kumo intelligently inferred) will be used when generating a training table.

Next, you can generate a training table with
:meth:`~kumoai.pquery.PredictiveQuery.generate_training_table`. This method
can be called with ``non_blocking=True`` (in which case it produces a Future
object and schedules the task to run in the background), or
``non_blocking=False`` (in which case it waits until the training table is
generated). Once a training table is generated, it can be viewed with methods
on the :class:`~kumoai.pquery.TrainingTable` object.

Finally, you can train a model on this training dataset with
:meth:`~kumoai.trainer.Trainer.fit`; see :ref:`faq_training` for more details.

How do I use a predictive query for generating predictions?
-----------------------------------------------------------

A predictive query can generate a prediction table in an identical manner to
its use for generating training tables. A generated prediction table can be
used in :meth:`~kumoai.trainer.Trainer.fit` to predict on a fitted model.

First, you can (optionally) suggest a prediction table generation plan with
:meth:`~kumoai.pquery.PredictiveQuery.suggest_prediction_table_plan`, which
returns a prediction table generation plan that can be customized for
advanced use-cases (*e.g.* to change the anchor time).
If you do not require a custom prediction table generation plan, the default
(Kumo intelligently inferred) will be used when generating a prediction table.

Next, you can generate a prediction table with
:meth:`~kumoai.pquery.PredictiveQuery.generate_prediction_table`. This method
can be called with ``non_blocking=True`` (in which case it produces a Future
object and schedules the task to run in the background), or
``non_blocking=False`` (in which case it waits until the prediction table is
generated). Once a prediction table is generated, it can be viewed with methods
on the :class:`~kumoai.pquery.PredictionTable` object.

Finally, you can generate predictions on this prediction table with
:meth:`~kumoai.trainer.Trainer.predict`; see :ref:`faq_training` for more
details.
