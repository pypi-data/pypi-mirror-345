kumoai.pquery
=============

.. currentmodule:: kumoai.pquery

A Kumo :class:`~kumoai.pquery.PredictiveQuery` is a fundamental concept within
the Kumo SDK; it is used to write a query predicting the future atop data
represented in a :class:`~kumoai.graph.Graph`. Predictive queries generate
training and prediction tables, which (together with a graph) can be passed to
fit or predict a model.

Enums
-----

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   RunMode


Predictive Query
----------------

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   PredictiveQuery

.. autosummary::
   :nosignatures:
   :toctree: ../generated
   :template: autosummary/model_plan.rst

   TrainingTableGenerationPlan
   PredictionTableGenerationPlan

Training Table
--------------

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   TrainingTableJob
   TrainingTable

Prediction Table
----------------

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   PredictionTableJob
   PredictionTable
