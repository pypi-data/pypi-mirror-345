kumoai.trainer
==============

.. currentmodule:: kumoai.trainer

A Kumo :class:`~kumoai.trainer.Trainer` supports training custom, highly
performant graph neural network models atop a :class:`~kumoai.graph.Graph`
and a :class:`~kumoai.pquery.TrainingTable`, and prediction of these models
with a :class:`~kumoai.pquery.PredictionTable`. Models can be completely
customized with detailed granularity with :class:`~kumoai.trainer.ModelPlan`,
although the default model plan suggested by predictive query is often suitable
for great performance out-of-the-box.

Model Plan
----------

A :class:`~kumoai.trainer.ModelPlan` defines the full parameter specification
for training a Kumo model. It is broken down into multiple individual plans for
different logical components of the training procedure: the
:class:`~kumoai.trainer.ColumnProcessingPlan` specifies any
:class:`~kumoai.encoder.Encoder` overrides for individual table columns, the
:class:`~kumoai.trainer.ModelArchitecturePlan` specifies graph neural network
model parameters, the :class:`~kumoai.trainer.NeighborSamplingPlan` specifies
graph neural network subgraph sampling parameters, the
:class:`~kumoai.trainer.OptimizationPlan` specifies machine learning
optimization parameters, and the :class:`~kumoai.trainer.TrainingJobPlan`
specifies training job-wide parameters for Kumo AutoML.

.. note::
   After generating a default model plan with the
   :meth:`~kumoai.pquery.PredictiveQuery.suggest_model_plan` method, no further
   changes are necessary to train your first model using Kumo-inferred
   parameters. These options are provided in case you would like to further
   fine-tune the modeling plan.

.. autosummary::
   :nosignatures:
   :toctree: ../generated
   :template: autosummary/model_plan.rst

   ModelPlan
   ColumnProcessingPlan
   ModelArchitecturePlan
   NeighborSamplingPlan
   OptimizationPlan
   TrainingJobPlan

Training
--------

Training a model requires constructing a :class:`~kumoai.trainer.Trainer`
object atop a  :class:`~kumoai.graph.Graph` and a
:class:`~kumoai.pquery.TrainingTable`. Fitting a model produces a
:class:`~kumoai.trainer.TrainingJobResult` or a
:class:`~kumoai.trainer.TrainingJob` that can be awaited at a later
point in time.

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   Trainer
   TrainingJob
   TrainingJobResult

Batch Prediction
----------------

Training a model requires constructing a :class:`~kumoai.trainer.Trainer`
object atop a :class:`~kumoai.graph.Graph`,
:class:`~kumoai.pquery.PredictionTable`, and a trained model (see the Trainer
``load`` method for more information). Predicting with a trained model produces
a :class:`~kumoai.trainer.BatchPredictionJobResult` or a
:class:`~kumoai.trainer.BatchPredictionJob` that can be awaited at a
later point in time.

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   BatchPredictionJob
   BatchPredictionJobResult
