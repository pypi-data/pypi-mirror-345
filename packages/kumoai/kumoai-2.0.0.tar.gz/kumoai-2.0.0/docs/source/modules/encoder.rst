kumoai.encoder
==============

.. currentmodule:: kumoai.encoder

While the Kumo platform intelligently infers encoders based on colum data and
semantic types, Kumo also supports custom encoder overrides for columns via the
:class:`~kumoai.trainer.ColumnProcessingPlan` specification when defining a
model plan. The following objects can be used as encoder overrides, bearing in
mind that the selected encoder must be supported on the semantic type of the
column that is being overridden.

Enums
--------

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   NAStrategy
   Scaler

Encoders
--------

.. autosummary::
   :nosignatures:
   :toctree: ../generated

   Null
   Numerical
   MaxLogNumerical
   MinLogNumerical
   Index
   Hash
   MultiCategorical
   GloVe
   NumericalList
   Datetime
