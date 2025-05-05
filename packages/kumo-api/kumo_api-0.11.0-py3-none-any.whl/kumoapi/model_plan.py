import copy
import dataclasses
import datetime
import types
from dataclasses import field, fields, make_dataclass
from typing import Any, Dict, Iterable, List, Literal, Optional, Tuple, Union

from kumoapi.common import StrEnum
from kumoapi.encoder import EncoderType
from kumoapi.graph import GraphDefinition
from kumoapi.pquery import QueryType
from kumoapi.task import TaskType
from kumoapi.train import TrainingTableSpec

try:
    from pydantic.v1 import (
        Field,
        confloat,
        conint,
        conlist,
        root_validator,
        validator,
    )
    from pydantic.v1.dataclasses import dataclass
except ImportError:
    from pydantic import (
        Field,
        confloat,
        conint,
        conlist,
        root_validator,
        validator,
    )
    from pydantic.dataclasses import dataclass


class RunMode(StrEnum):
    r"""Defines the run mode for AutoML. Please see the
    `Kumo documentation <https://docs.kumo.ai/docs/whats-the-recommended-way-to-cut-down-on-model-training-time>`_
    for more information."""  # noqa
    #: Speeds up the search process—typically about 4x faster than
    #: using the normal mode.
    FAST = 'fast'
    #: Default value.
    NORMAL = 'normal'
    #: Typically takes 4x the time used by the normal mode.
    BEST = 'best'
    DEBUG = 'debug'


class RHSEmbeddingMode(StrEnum):
    r"""Specifies how to incorporate shallow RHS representations in link
    prediction tasks."""
    # Use trainable look-up embeddings (transductive):
    LOOKUP = 'lookup'
    # Purely rely on shallow RHS input features (inductive):
    FEATURE = 'feature'
    # Rely on shallow/single layer RHS input features (inductive):
    SHALLOW_FEATURE = 'shallow_feature'
    # Fuse look-up embeddings and shallow RHS input features (transductive):
    FUSION = 'fusion'

    @property
    def use_rhs_lookup(self) -> bool:
        return self in [
            RHSEmbeddingMode.LOOKUP,
            RHSEmbeddingMode.FUSION,
        ]

    @property
    def use_rhs_feature(self) -> bool:
        return self in [
            RHSEmbeddingMode.FEATURE,
            RHSEmbeddingMode.SHALLOW_FEATURE,
            RHSEmbeddingMode.FUSION,
        ]

    @property
    def only_use_rhs_feature(self) -> bool:
        return self in [
            RHSEmbeddingMode.FEATURE,
            RHSEmbeddingMode.SHALLOW_FEATURE,
        ]


class WeightMode(StrEnum):
    r"""Specifies how to deal with imbalanced datasets or training tables that
    contain a weight column."""
    # Sample training examples with replacement:
    SAMPLE = 'sample'
    # Weight training examples in the loss function:
    WEIGHTED_LOSS = 'weighted_loss'

    @classmethod
    def _missing_(cls, value: str):
        if not isinstance(value, str):
            value = value.value
        if value.lower() == 'mix':
            return WeightMode.SAMPLE
        return None

    @property
    def use_sampling(self) -> bool:
        return self in [WeightMode.SAMPLE]

    @property
    def use_weighted_loss(self) -> bool:
        return self in [WeightMode.WEIGHTED_LOSS]


class LinkPredOutputType(StrEnum):
    RANKING = 'ranking'
    EMBEDDING = 'embedding'

    @classmethod
    def _missing_(cls, value: str):
        # Ensure backward compatibility:
        if not isinstance(value, str):
            value = value.value
        if value.lower() == 'default':
            return LinkPredOutputType.RANKING
        if value.lower() == 'link_prediction_ranking':
            return LinkPredOutputType.RANKING
        if value.lower() == 'link_prediction_embedding':
            return LinkPredOutputType.EMBEDDING
        if value.lower() == "embedding":
            return LinkPredOutputType.EMBEDDING
        if value.lower() == "ranking":
            return LinkPredOutputType.RANKING


class LossType(StrEnum):
    BINARY_CROSS_ENTROPY = 'binary_cross_entropy'
    CROSS_ENTROPY = 'cross_entropy'
    FOCAL_LOSS = 'focal'
    MAE = 'mae'
    MSE = 'mse'
    HUBER = 'huber'
    NORMAL_DISTRIBUTION = 'normal_distribution'
    NEGATIVE_BINOMIAL = 'negative_binomial_distribution'
    LOG_NORMAL_DISTRIBUTION = 'log_normal_distribution'


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class FocalLossConfig:
    name: Literal['focal']
    # Weighting factor to balance positive vs. negative examples.
    alpha: float = Field(default=0.25, gt=0, lt=1)
    # Balance easy vs. hard examples.
    gamma: float = Field(default=2.0, ge=1)

    def __repr__(self) -> str:
        return f'FocalLoss(alpha={self.alpha}, gamma={self.gamma})'


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class HuberLossConfig:
    name: Literal['huber']
    # The threshold at which to change between delta-scaled L1 and L2 loss.
    delta: float = Field(default=1.0, gt=0)

    def __repr__(self) -> str:
        return f'HuberLoss(delta={self.delta})'


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class QuantileLossConfig:
    name: Literal['quantile']
    # The quantile to be estimated.
    q: float = Field(ge=0.0, le=1.0)

    def __repr__(self) -> str:
        return f'QuantileLoss(q={self.q})'


class IntervalType(StrEnum):
    STEP = 'step'
    EPOCH = 'epoch'


class AggregationType(StrEnum):
    SUM = 'sum'
    MEAN = 'mean'
    MIN = 'min'
    MAX = 'max'
    STD = 'std'
    VAR = 'var'


class ActivationType(StrEnum):
    RELU = 'relu'
    LEAKY_RELU = 'leaky_relu'
    ELU = 'elu'
    GELU = 'gelu'


class NormalizationType(StrEnum):
    LAYER_NORM = 'layer_norm'
    BATCH_NORM = 'batch_norm'


class PastEncoderType(StrEnum):
    DECOMPOSED = 'decomposed'
    NORMALIZED = 'normalized'
    MLP = 'mlp'
    TRANSFORMER = 'transformer'


class DistanceMeasureType(StrEnum):
    DOT_PRODUCT = 'dot_product'
    COSINE = 'cosine'


class PositionalEncodingType(StrEnum):
    HOP = 'hop'
    RANDOM_GNN = 'random_gnn'


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class PruningConfig:
    min_epochs: int = Field(ge=1)
    k: int = Field(ge=1)
    min_delta: float = Field(ge=0)
    patience: int = Field(gt=0)

    def __repr__(self) -> str:
        return (f'Pruning(min_epochs={self.min_epochs}, '
                f'k={self.k}, min_delta={self.min_delta}, '
                f'patience={self.patience})')


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class EarlyStoppingConfig:
    min_delta: float = Field(ge=0)
    patience: int = Field(gt=0)

    def __repr__(self) -> str:
        return (f'EarlyStopping(min_delta={self.min_delta}, '
                f'patience={self.patience})')


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class LRSchedulerConfig:
    name: str
    interval: IntervalType
    kwargs: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        if len(self.kwargs) == 0:
            return f'LRScheduler(name={self.name}, interval={self.interval})'

        kwargs_repr = ', '.join(
            [f'{key}={value}' for key, value in self.kwargs.items()])
        kwargs_repr = '{' + kwargs_repr + '}'

        return (f'LRScheduler(\n'
                f'  name={self.name},\n'
                f'  interval={self.interval},\n'
                f'  kwargs={kwargs_repr},\n'
                f')')


class MissingType(StrEnum):
    VALUE = '???'


class InferredType(StrEnum):
    VALUE = 'inferred'


@dataclass(
    config=dict(  # type: ignore
        validate_assignment=True,
        extra='allow',
    ),
    repr=False)
class HopConfig:
    default: conint(ge=-1, le=128)  # type: ignore

    def __getitem__(self, key: str) -> Union[int, InferredType]:
        return getattr(self, key)

    def __setitem__(
        self,
        key: str,
        value: Union[int, str, InferredType],
    ) -> None:
        if isinstance(value, str):
            assert value == 'inferred'
            value = InferredType.VALUE
        setattr(self, key, value)

    @property
    def __pydantic_extra__(self) -> Dict[str, Union[int, InferredType]]:
        extra = copy.copy(self.__dict__)
        extra.pop('default')
        extra.pop('__pydantic_initialised__')
        return extra

    @root_validator(skip_on_failure=True)
    def validate_extra(
        cls,
        values: Dict[str, Any],
    ) -> Dict[str, Union[int, InferredType]]:
        for key, value in values.items():
            if key == 'default':
                continue

            if '->' not in key:
                raise ValueError(f"'{key}' is not a valid edge definition. "
                                 f"Ensure that the edge points from a source "
                                 f"key to a destination key via "
                                 f"'source_key->destination_key' syntax")
            if value == 'inferred':
                values[key] = InferredType.VALUE
                continue
            if not isinstance(value, int):
                raise ValueError(f"Value of '{key}' is not a valid integer "
                                 f"(got {value})")
            if isinstance(value, int) and value < -1:
                raise ValueError(f"Ensure the value of '{key}' is greater "
                                 f"than or equal to -1 (got {value})")
            if isinstance(value, int) and value > 512:
                raise ValueError(f"Ensure the value of '{key}' is less than "
                                 f"or equal to 512 (got {value})")

        return values

    def __repr__(self) -> str:
        extra_repr = ',  '.join([
            f'{key}={value}' for key, value in self.__pydantic_extra__.items()
        ])
        if len(extra_repr) > 0:
            extra_repr = ', ' + extra_repr
        return f'{self.__class__.__name__}(default={self.default}{extra_repr})'


# NOTE We need to monkey-patch `dataclasses.asdict()` in order to correctly
# serialize pydantic extra fields in pydantic<2.0.
_asdict_inner_orig = dataclasses._asdict_inner  # type: ignore


def _asdict_inner(obj, dict_factory):
    if isinstance(obj, HopConfig):
        return {**dict(default=obj.default), **obj.__pydantic_extra__}
    return _asdict_inner_orig(obj, dict_factory)


dataclasses._asdict_inner = _asdict_inner  # type: ignore

MAX_NUM_HOPS = 6


def _to_dict(self) -> Dict[int, HopConfig]:
    return {
        int(f.name[len('hop'):]) - 1: getattr(self, f.name)
        for f in fields(self) if getattr(self, f.name) is not None
    }


def _validate_consecutive_hops(self) -> None:
    hops = list(self.to_dict().keys())
    if hops != list(range(len(hops))):
        raise ValueError(f"Found non-consecutive hop definition "
                         f"{[hop + 1 for hop in hops]}.")


def _num_hops(self) -> int:
    self._validate_consecutive_hops()
    return len(self.to_dict())


def _repr(self) -> str:
    self._validate_consecutive_hops()
    hops_repr = []
    for i in range(1, self.num_hops() + 1):
        hop = getattr(self, f'hop{i}')
        hop_dict = {**dict(default=hop.default), **hop.__pydantic_extra__}
        if len(hop_dict) == 1:
            hop_repr = str(hop.default)
        else:
            hop_info = [f'{key}={value}' for key, value in hop_dict.items()]
            hop_info = [' ' * 2 + x for x in hop_info]
            hop_repr = '{\n' + ',\n'.join(hop_info) + ',\n}'
        hop_repr = f'hop{i}={hop_repr},'
        hops_repr.append(hop_repr)

    if len(hops_repr) == 0:
        return 'NumNeighbors()'

    return 'NumNeighbors(\n' + _add_indent('\n'.join(hops_repr), 2) + '\n)'


_NumNeighborsConfig = make_dataclass(
    '_NumNeighborsConfig',
    fields=[
        (f'hop{i}', Optional[HopConfig], None)  # type: ignore
        for i in range(1, MAX_NUM_HOPS + 1)
    ],
    namespace={
        'to_dict': _to_dict,
        '_validate_consecutive_hops': _validate_consecutive_hops,
        'num_hops': _num_hops,
        '__repr__': _repr,
        '__len__': lambda self: self.num_hops(),
    },
)

types._NumNeighborsConfig = _NumNeighborsConfig  # type: ignore
NumNeighborsConfig = dataclass(
    config=dict(validate_assignment=True),  # type: ignore
    repr=False,
)(_NumNeighborsConfig)


@dataclasses.dataclass
class Metadata:
    tunable: bool = False  # Tunable during AutoML search.
    hidden: bool = False
    valid_task_types: List[TaskType] = field(  # all by default.
        default_factory=lambda: list(TaskType))
    valid_query_types: List[QueryType] = field(  # all by default.
        default_factory=lambda: list(QueryType))


class PlanMixin:
    def items(self) -> Iterable[Tuple[str, Any, Metadata]]:
        r"""Iterates over all attributes of this dataclass."""
        schema = self.__pydantic_model__.schema()  # type: ignore
        for key in self.__dataclass_fields__:  # type: ignore
            value = getattr(self, key)
            metadata = schema['properties'][key]['metadata']
            yield key, value, metadata

    def is_valid_option(
        self,
        name: str,
        metadata: Metadata,
        task_type: TaskType,
        query_type: QueryType,
        has_train_table_weight_col: bool = False,
    ) -> bool:
        """
        Whether the option is valid, given its task and query type.

        Args:
            name (str): The name of the field to check.
            metadata (Metadata): The metadata associated with the option.
            task_type (TaskType): The task type.
            query_type (QueryType): The query type.
        """
        return (task_type in metadata.valid_task_types
                and query_type in metadata.valid_query_types)

    def __repr__(self) -> str:
        field_reprs = []
        for key, value, metadata in self.items():
            if metadata.hidden:
                continue

            if metadata.tunable and isinstance(value, list):
                value_repr = '\n'.join(
                    [f'{_add_indent(repr(v), 2)},' for v in value])
                value_repr = '[\n' + value_repr + '\n]'
            else:
                value_repr = repr(value)
            field_reprs.append(f'{key}={value_repr},')

        field_repr = '\n'.join(field_reprs)
        reprs = _add_indent(field_repr, num_spaces=2)
        return f'{self.__class__.__name__}(\n{reprs}\n)'


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class TrainingTableGenerationPlan(PlanMixin):
    r"""Configuration parameters that define the construction of a Kumo
    training table from a predictive query. Please see the
    `Kumo documentation <https://docs.kumo.ai/docs/advanced-operations
    #training-table-generation>`_ for more information.

    :ivar split: (``str``) A custom split that is used to generate a training,
        validation, and test set in the training table
        (*default:* ``"inferred"``).
        **Supported Task Types:** All

    :ivar train_start_offset: (``int`` | ``"inferred``") Defines the numerical
        offset from the most recent entry to use to generate training data
        labels. Unless a custom time unit is specified in the aggregation, this
        value is in days (*default:* ``"inferred"``). Eventually we would
        like to migrate this parameter to start_time.
        **Supported Task Types:** Temporal

    :ivar train_end_offset: (``int`` | ``"inferred"``) Defines the numerical
        offset from the most recent entry to not use to generate training data
        labels. Unless a custom time unit is specified in the aggregation, this
        value is in days (*default:* ``"inferred"``). Eventually we would
        like to migrate this parameter to end_time.
        **Supported Task Types:** Temporal

    :ivar start_time: (``int`` | ``"inferred"`` | ``str``) Defines the absolute
        start time to use for generating training data. Can be specified
        either as a pandas Timestamp compatible string (e.g. '2024-04-01') or
        as a non-positive integer offset in days from the current time
        (e.g. -30 for 30 days ago) (*default:* ``"inferred"``).
        **Supported Task Types:** Temporal

    :ivar end_time: (``int`` | ``"inferred"`` | ``str``) Defines the absolute
        end time to use for generating training data. Can be specified either
        as a pandas Timestamp compatible string (e.g. '2024-04-01') or as a
        non-positive integer offset in days from the current time
        (e.g. -30 for 30 days ago) (*default:* ``"inferred"``).
        **Supported Task Types:** Temporal

    :ivar timeframe_step: (``int`` | ``"inferred"``) Defines the step size of
        generating time intervals for training table generation
        (*default:* ``"inferred"``).
        **Supported Task Types:** Temporal

    :ivar forecast_length: (``int``) Turns a node regression problem into a
        forecasting problem (*default:* ``"missing"``).
        **Supported Task Types:** Temporal Regression

    :ivar lag_timesteps: (``int``) For forecasting problems,
        leverage the auto-regressive labels as inputs. This parameter controls
        the number of previous values that should be considered as
        auto-regressive labels (*default:* ``"missing"``).
        **Supported Task Types:** Temporal Regression

    :ivar year_over_year: (``bool``) For forecasting problems, integrate
        Year-Over-Year features as inputs to give more attention to the data
        from the previous year when making a prediction.
        (*default:* ``"missing"``)
    """  # noqa
    # General Options =========================================================

    # Respect resolution order by first trying to map strings to `InferredType`
    split: Union[InferredType, str] = Field(
        default=InferredType.VALUE,
        metadata=Metadata(),
    )

    train_start_offset: Union[int, InferredType, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(valid_query_types=[QueryType.TEMPORAL]),
        ge=0,
    )

    train_end_offset: Union[int, InferredType, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(valid_query_types=[QueryType.TEMPORAL]),
        ge=0,
    )

    start_time: Union[int, InferredType, MissingType, str] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(valid_query_types=[QueryType.TEMPORAL]),
    )

    end_time: Union[int, InferredType, MissingType, str] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(valid_query_types=[QueryType.TEMPORAL]),
    )

    timeframe_step: Union[int, InferredType, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(valid_query_types=[QueryType.TEMPORAL]),
        ge=1,
    )

    # Forecasting =============================================================

    forecast_length: Optional[Union[int, MissingType]] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(
            valid_task_types=[TaskType.REGRESSION, TaskType.FORECASTING],
            valid_query_types=[QueryType.TEMPORAL],
        ),
        ge=1,
    )

    lag_timesteps: Optional[Union[int, MissingType]] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(
            valid_task_types=[TaskType.REGRESSION, TaskType.FORECASTING],
            valid_query_types=[QueryType.TEMPORAL],
        ),
        ge=0,
    )

    year_over_year: Union[bool, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(
            valid_task_types=[TaskType.REGRESSION, TaskType.FORECASTING],
            valid_query_types=[QueryType.TEMPORAL],
        ),
    )

    # Entity Candidate Generation =============================================

    entity_candidate: Optional[str] = Field(
        default=None,
        metadata=Metadata(
            hidden=True,
            valid_query_types=[QueryType.TEMPORAL],
        ),
    )

    entity_candidate_aggregation: Optional[str] = Field(
        default=None,
        metadata=Metadata(
            hidden=True,
            valid_query_types=[QueryType.TEMPORAL],
        ),
    )

    # Overriding Predictive Queries ===========================================

    task_path_override: Optional[str] = Field(
        default=None,
        metadata=Metadata(hidden=True),
    )

    train_table_path_override: Optional[str] = Field(
        default=None,
        metadata=Metadata(hidden=True),
    )


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class PredictionTableGenerationPlan(PlanMixin):
    r"""Configuration parameters that define the construction of a Kumo
    prediction table from a predictive query.

    :ivar anchor_time: (``int`` | ``"inferred"`` | ``datetime.datetime``) The
        time that a prediction horizon start time of "zero" refers to. If not
        set, will be inferred to be the latest timestamp in the target fact
        table. Note that this value can either be provided as an integer,
        representing the number of nanoseconds from the Unix epoch, or as a
        ``datetime.datetime`` object (*default:* ``"inferred"``).
        **Supported Task Types:** Temporal

    :ivar forecast_length: (``int``) Turns a node regression problem into a
        forecasting problem (*default:* ``"missing"``). Must be provided if the
        model was trained using this parameter.
        **Supported Task Types:** Temporal Regression

    :ivar lag_timesteps: (``int``) For forecasting problems,
        leverage the auto-regressive labels as inputs. This parameter controls
        the number of previous values that should be considered as
        auto-regressive labels (*default:* ``"missing"``). Must be provided if
        the model was trained using this parameter.
        **Supported Task Types:** Temporal Regression

    :ivar year_over_year: (``bool``) For forecasting problems, integrate
        Year-Over-Year features as inputs to give more attention to the data
        from the previous year when making a prediction. Must be provided if
        the model was trained using this parameter.
        (*default:* ``"missing"``)
    """
    # General Options =========================================================

    anchor_time: Union[int, InferredType, datetime.datetime] = Field(
        default=InferredType.VALUE,
        metadata=Metadata(valid_query_types=[QueryType.TEMPORAL]),
    )

    @validator('anchor_time')
    def is_nanosecond_timestamp(
        cls,
        value: Union[int, InferredType, datetime.datetime],
    ) -> Union[int, InferredType]:
        if isinstance(value, (InferredType, int)):
            return value

        # Convert datetime to timestmap in nanoseconds, note that this
        # incorporates whatever timezone the `datetime` object is
        # represented in:
        return int(int(value.strftime('%s')) * 1e9)

    # Forecasting Options =====================================================

    lag_timesteps: Optional[Union[int, MissingType]] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(
            valid_task_types=[TaskType.REGRESSION, TaskType.FORECASTING],
            valid_query_types=[QueryType.TEMPORAL],
        ),
        ge=0,
    )

    forecast_length: Optional[Union[int, MissingType]] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(
            valid_task_types=[TaskType.REGRESSION, TaskType.FORECASTING],
            valid_query_types=[QueryType.TEMPORAL],
        ),
        ge=1,
    )

    year_over_year: Union[bool, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(
            valid_task_types=[TaskType.REGRESSION, TaskType.FORECASTING],
            valid_query_types=[QueryType.TEMPORAL],
        ),
    )


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class TrainingJobPlan(PlanMixin):
    r"""Configuration parameters that define the general execution of a Kumo
    AutoML search. Please see the
    `Kumo documentation <https://docs.kumo.ai/docs/advanced-operations
    #training-job-plan>`_ for more information.

    :ivar num_experiments: (``int``) The number of experiments to run
        (*default:* ``run_mode``-dependent).
        **Supported Task Types:** All

    :ivar metrics: (``list[str]``) The metrics to compute for the run
        (*default:* ``task_type``-dependent).
        **Supported Task Types:** All

    :ivar tune_metric: (``str``) The metric to judge performance on
        (*default:* ``task_type``-dependent).
        **Supported Task Types:** All

    :ivar pruning: (``PruningConfig | None``) A pruning strategy to early stop
        unpromising AutoML trials based on the performance of previous trials
        to speed-up the AutoML search process.
        (*default:* ``{min_epochs=2, k=3, min_delta=0.0, patience=1}``).
        **Supported Task Types:** All

    :ivar refit_trainval: (``bool``) Whether to refit the model after training
        on the training and validation splits (*default:* ``True``).
        **Supported Task Types:** All

    :ivar refit_full: (``bool``) Whether to refit the model after training
        on the training, validation and test splits (*default:* ``False``).
        **Supported Task Types:** All
    """
    # General Options =========================================================

    num_experiments: Union[int, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(),
        ge=1,
    )

    metrics: Union[List[str], MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(),
    )

    # Respect resolution order by first trying to map strings to `MissingType`.
    tune_metric: Union[MissingType, str] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(),
    )

    pruning: Union[
        PruningConfig,
        MissingType,
        None,
    ] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(),
    )

    disable_compilation: bool = Field(
        default=True,
        metadata=Metadata(hidden=True),
    )

    # Refitting ===============================================================

    refit_trainval: bool = Field(
        default=True,
        metadata=Metadata(),
    )

    refit_full: bool = Field(
        default=False,
        metadata=Metadata(),
    )

    # Debugging ===============================================================

    disable_explain: bool = Field(
        default=False,
        metadata=Metadata(hidden=True),
    )

    manual_seed: Optional[int] = Field(
        default=None,
        metadata=Metadata(hidden=True),
    )

    # Deprecated Options ======================================================

    enable_baselines: bool = Field(
        default=False,
        metadata=Metadata(hidden=True),
    )

    # =========================================================================


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class ColumnProcessingPlan(PlanMixin):
    r"""Configuration parameters that define how columns are encoded in the
    training and batch prediction pipelines. Please see the
    `Kumo documentation <https://docs.kumo.ai/docs/advanced-operations
    #column-processing>`_ for more information.

    :ivar encoder_overrides: (``dict[str, Encoder] | None``) A dictionary of
        encoder overrides, which maps the ``{table_name}.{column name}`` to an
        :class:`~kumoapi.encoder.Encoder` (*default:* ``None``).
        **Supported Task Types:** All
    """
    # General Options =========================================================

    encoder_overrides: Optional[Dict[str, Union[EncoderType, str]]] = Field(
        default=None,
        metadata=Metadata(),
    )


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class NeighborSamplingPlan(PlanMixin):
    r"""Configuration parameters that define how subgraphs are sampled in the
    training and batch prediction pipelines. Please see the
    `Kumo documentation <https://docs.kumo.ai/docs/advanced-operations
    #neighbor-sampling>`_ for more information.

    :ivar num_neighbors: (``list[NumNeighborsConfig]``) Determines the number
        of neighbors to sample for each hop when sampling subgraphs for
        training and prediction (*default:* ``run_mode``-dependent).
        **Supported Task Types:** All

    :ivar sample_from_entity_table: (``bool``) Whether to include the entity
        table in sampling (*default:* ``True``).
        **Supported Task Types:** Static

    :ivar adaptive_sampling: (``bool``) Whether to use the MetapathAware
        adaptive sampling algorithm. If ``True``, sampler will oversample
        nodes in later hops whenever it samples more than the specified number
        of neighbors in a hop. Generally improves performance at the cost of
        longer runtime. (*default:* ``False``).
        **Supported Task Types:** All
    """
    # General Options =========================================================

    max_target_neighbors_per_entity: Union[
        conlist(  # type: ignore
            Union[conint(ge=-1, le=512), InferredType],
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(hidden=True, tunable=True),
        )

    num_neighbors: Union[
        conlist(NumNeighborsConfig, min_items=1),  # type: ignore
        conlist(  # type: ignore
            conlist(conint(ge=-1, le=128), max_items=6),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    sample_from_entity_table: Union[bool, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(
            valid_task_types=TaskType.get_node_pred_tasks(),
            valid_query_types=[QueryType.STATIC],
        ),
    )

    adaptive_sampling: bool = Field(
        default=False,
        metadata=Metadata(hidden=True),
    )

    # =========================================================================

    def is_valid_option(
        self,
        name: str,
        metadata: Metadata,
        task_type: TaskType,
        query_type: QueryType,
        has_train_table_weight_col: bool = False,
    ) -> bool:
        if name == 'max_target_neighbors_per_entity':
            return (query_type == QueryType.TEMPORAL
                    or task_type == TaskType.STATIC_LINK_PREDICTION)
        return super().is_valid_option(name, metadata, task_type, query_type,
                                       has_train_table_weight_col)


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class OptimizationPlan(PlanMixin):
    r"""Configuration parameters that define how columns are encoded in the
    training and batch prediction pipelines. Please see the
    `Kumo documentation <https://docs.kumo.ai/docs/advanced-operations
    #optimization>`_ for more information.

    :ivar max_epochs: (``int``) The maximum number of epochs to train a model
        for (*default:* ``run_mode``-dependent).
        **Supported Task Types:** All

    :ivar min_steps_per_epoch: (``int``) The minimum number of steps to be
        included in an epoch; one step corresponds to one forward pass of a
        mini-batch (*default:* ``30``).
        **Supported Task Types:** All

    :ivar max_steps_per_epoch: (``int``) The maximum number of steps to be
        included in an epoch; one step corresponds to one forward pass of a
        mini-batch (*default:* ``run_mode``-dependent).
        **Supported Task Types:** All

    :ivar max_val_steps: (``int``) The maximum number of steps to be included
        in a validation pass; one step corresponds to one forward pass of a
        mini-batch (*default:* ``run_mode``-dependent).
        **Supported Task Types:** All

    :ivar max_test_steps: (``int``) The maximum number of steps to be included
        in a test pass; one step corresponds to one forward pass of a
        mini-batch (*default:* ``run_mode``-dependent).
        **Supported Task Types:** All

    :ivar loss: (``list[str]``) The loss type to use in the model optimizer
        (*default:* ``task_type``-dependent).
        **Supported Task Types:** All

    :ivar base_lr: (``list[float]``) The base learning rate (pre-decay) to be
        used in the model optimizer.
        (*default:* ``[1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2]``).
        **Supported Task Types:** All

    :ivar weight_decay: (``list[float]``) A list of potential weight decay
        options in the model optimizer.
        (*default:* ``[0.0, 5e-8, 5e-7, 5e-6]``).
        **Supported Task Types:** All

    :ivar batch_size: (``list[int]``) The number of examples to be included in
        one mini-batch. (*default:* ``[512, 1024]``).
        **Supported Task Types:** All

    :ivar early_stopping: (``list[EarlyStoppingConfig]``) A list of potential
        early stopping strategies
        :class:`~kumoapi.model_plan.EarlyStoppingConfig` for model optimization
        (*default:* ``[{min_delta=0.0, patience=3}]``).
        **Supported Task Types:** All

    :ivar lr_scheduler: (``list[LRSchedulerConfig]``) A list of potential
        learning rate schedulers
        :class:`~kumoapi.model_plan.LRSchedulerConfig` for model optimization
        (*default:* ``[
        {name="cosine_with_warmup_restarts", interval="step"},
        {name="constant_with_warmup", interval="step"},
        {name="linear_with_warmup", interval="step"},
        {name="csoine_with_warmup", interval="step"}]``).
        **Supported Task Types:** All

    :ivar majority_sampling_ratio: (``list[float | None]``) A ratio to specify
        how examples are sampled from the majority class
        (*default:* ``[None]``).
        **Supported Task Types:** Binary Classification

    :ivar weight_mode: (``list[WeightMode | None]``) Defines how to use
        the weight column in the training table (if present) in the model
        training process. If `[None]` weight column will not be used
        for training even if present. It could still be used for metrics
        computation.
    """
    # General Options =========================================================

    max_epochs: Union[int, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(),
        ge=1,
    )

    min_steps_per_epoch: Union[int, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(),
        ge=1,
        le=4000,
    )

    max_steps_per_epoch: Union[int, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(),
        ge=1,
    )

    max_val_steps: Union[int, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(),
        ge=1,
        le=8000,
    )

    max_test_steps: Union[int, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(),
        ge=1,
        le=8000,
    )

    loss: Union[
        conlist(  # type: ignore
            Union[
                LossType,
                FocalLossConfig,
                HuberLossConfig,
                QuantileLossConfig,
            ],
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    base_lr: Union[
        conlist(  # type: ignore
            confloat(gt=0.0),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    weight_decay: Union[
        conlist(  # type: ignore
            confloat(ge=0.0),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    batch_size: Union[
        conlist(  # type: ignore
            conint(ge=1, le=2048),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    early_stopping: Union[
        conlist(  # type: ignore
            Optional[EarlyStoppingConfig],
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    lr_scheduler: Union[
        conlist(  # type: ignore
            Optional[LRSchedulerConfig],
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    # Task-specific Options ===================================================

    majority_sampling_ratio: Union[
        conlist(  # type: ignore
            Optional[confloat(gt=0.0)],
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    weight_mode: Union[
        conlist(  # type: ignore
            Optional[WeightMode],
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    # =========================================================================

    def is_valid_option(
        self,
        name: str,
        metadata: Metadata,
        task_type: TaskType,
        query_type: QueryType,
        has_train_table_weight_col: bool = False,
    ) -> bool:
        if name == 'weight_mode':
            if task_type == TaskType.BINARY_CLASSIFICATION:
                return True  # Support for majority sampling ratio.

            return (has_train_table_weight_col
                    and task_type != TaskType.FORECASTING)

        if name == 'majority_sampling_ratio':
            return (task_type == TaskType.BINARY_CLASSIFICATION
                    and not has_train_table_weight_col)

        return super().is_valid_option(name, metadata, task_type, query_type,
                                       has_train_table_weight_col)


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class MessagePassingModelPlan(PlanMixin):
    r"""Common configuration parameters for Kumo Message Passing models.

    :ivar channels: (``list[int]``) A list of potential dimension of layers in
        the Message Passing model
        (*default:* ``[64, 128, 256]``).
        **Supported Task Types:** All
    """
    name: str

    channels: Union[
        conlist(  # type: ignore
            conint(ge=1, le=512),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    @validator('channels')
    def is_even_channel(
        cls,
        values: Union[List[int], MissingType],
    ) -> Union[List[int], MissingType]:
        if isinstance(values, list):
            for value in values:
                if value % 2 != 0:
                    raise ValueError(f"'channels' requires an even number "
                                     f"(got {value})")
        return values


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class GNNModelPlan(MessagePassingModelPlan):
    r"""Configuration parameters that define how the Kumo graph neural network
    is architected.

    :ivar aggregation: (``list[list["sum" | "mean" | "min" | "max" | "std"]]``)
        A nested list of aggregation operators in the Graph Neural Network
        aggregation process
        (*default:* ``[
        ["sum", "mean", "max"],
        ["sum", "mean", "min", "max", "std"]]``).
        **Supported Task Types:** All
    """
    name: Literal['GNN'] = Field(
        default='GNN',
        metadata=Metadata(tunable=False),
    )

    aggregation: Union[
        conlist(  # type: ignore
            List[AggregationType],
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class GraphTransformerModelPlan(MessagePassingModelPlan):
    r"""Configuration parameters that define how the Kumo graph neural network
    is architected.

    :ivar num_layers: (``list[int]``) A list of potential
        number of transformer layers in the Graph Transformer model
        (*default:* ``[4, 6, 8]``).
        **Supported Task Types:** Node Prediction

    :ivar num_heads: (``list[int]``) A list of potential number of attention
        heads in the Graph Transformer model
        (*default:* ``[8, 16]``).
        **Supported Task Types:** Node Prediction

    :ivar dropout: (``list[float]``) A list of potential dropout rates in the
        Graph Transformer model
        (*default:* ``[0.1, 0.5]``).
        **Supported Task Types:** Node Prediction

    :ivar positional_encodings: (``list[PositionalEncodingType]``) A list of
        potential positional encodings to use in the Graph Transformer model
        (*default:* ``[None]``).
        **Supported Task Types:** Node Prediction
    """
    name: Literal['GraphTransformer'] = Field(
        default='GraphTransformer',
        metadata=Metadata(tunable=False),
    )

    num_layers: Union[
        conlist(  # type: ignore
            conint(ge=1, le=12),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    num_heads: Union[
        conlist(  # type: ignore
            conint(ge=1, le=32),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    dropout: Union[
        conlist(confloat(ge=0.0, lt=1.0)),  # type: ignore
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    positional_encodings: Union[
        conlist(List[PositionalEncodingType], min_items=1),  # type: ignore
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class ModelArchitecturePlan(PlanMixin):
    r"""Configuration parameters that define how the Kumo graph neural network
    is architected. Please see the
    `Kumo documentation <https://docs.kumo.ai/docs/advanced-operations
    #model-architecture>`_ for more information.

    :ivar channels: (``list[int]``) A list of potential dimension of layers in
        the Graph Neural Network model
        (*default:* ``[64, 128, 256]``).
        **Supported Task Types:** All

    :ivar num_pre_message_passing_layers: (``list[int]``) A list of potential
        number of multi-layer perceptron layers *before* message passing layers
        in the Graph Neural Network model
        (*default:* ``[0, 1, 2]``).
        **Supported Task Types:** All

    :ivar num_post_message_passing_layers: (``list[int]``) A list of potential
        number of multi-layer perceptron layers *after* message passing layers
        in the Graph Neural Network model
        (*default:* ``[1, 2]``).
        **Supported Task Types:** All

    :ivar aggregation: (``list[list["sum" | "mean" | "min" | "max" | "std"]]``)
        A nested list of aggregation operators in the Graph Neural Network
        aggregation process
        (*default:* ``[
        ["sum", "mean", "max"],
        ["sum", "mean", "min", "max", "std"]]``).
        **Supported Task Types:** All

    :ivar activation: (``list["relu" | "leaky_relu" | "elu" | "gelu"]``) A list
        of activation functions to use during AutoML
        (*default:* ``["relu", "leaky_relu", "elu", "gelu"]``).
        **Supported Task Types:** All

    :ivar normalization: (``list[None | "layer_norm" | "batch_norm"]``) The
        normalization layer to apply (*default:* ``["layer_norm"]``).
        **Supported Task Types:** All

    :ivar module: (``"ranking"`` | ``"embedding"``) The link prediction module
        to use (*default:* ``["ranking"]``).
        **Supported Task Types:** Link Prediction

    :ivar handle_new_target_entities: (``bool``) Whether to make link
        prediction models be able to handle predictions on new target entities
        at batch prediction time (*default:* ``False``).
        **Supported Task Types:** Link Prediction

    :ivar target_embedding_mode: (``["lookup" | "feature" | "shallow_feature" |
        fusion]``) Specifies how target node embeddings are embedded
        (*default:* ``["lookup"]``).
        **Supported Task Types:** Link Prediction

    :ivar output_embedding_dim: (``[int]``) The output embedding dimension for
        link prediction models (*default:* ``[32]``).
        **Supported Task Types:** Link Prediction

    :ivar ranking_embedding_loss_coeff: (``[float]``) The coefficient of the
        embedding loss applied to train ranking-based link prediction models
        link prediction models (*default:* ``[0.0]``).
        **Supported Task Types:** Temporal Link Prediction

    :ivar distance_measure: (``["dot_product" | "cosine"]``) Specifies the
        distance measure between node embeddings to use in the final link
        prediction calculation (*default:* ``["dot_product"]``).
        **Supported Task Types:** Link Prediction

    :ivar use_seq_id: (``[bool]``) Specifies whether to use postional encodings
        of the sequence order of facts as an additional model feature
        (*default:* ``[False]``).
        **Supported Task Types:** All

    :ivar prediction_time_encodings: (``[bool]``) Specifies whether to encode
        the absolute prediction time as an additional model feature
        (*default:* ``[False]``).
        **Supported Task Types:** Temporal Node Prediction

    :ivar past_encoder: (``["decomposed" | "normalized" | "mlp" |
        "transformer"]``) Specifies how to encode auto-regressive labels if
        present (*default:* ``["decomposed"]``).
        **Supported Task Types:** Temporal Regression

    :ivar handle_new_entities: (``bool``) Whether to make forecasting models
        transductive by learning entity-specific heads. This can improve
        performance in case entities stay static over time, but will decrease
        performance on new entities arising during batch prediction time
        (*default:* ``True``).
        **Supported Task Types:** Forecasting
    """
    # General Options =========================================================

    model: Union[
        conlist(  # type: ignore
            Union[GNNModelPlan, GraphTransformerModelPlan],
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    channels: Union[
        conlist(  # type: ignore
            conint(ge=1, le=512),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True, hidden=True),
        )

    num_pre_message_passing_layers: Union[
        conlist(  # type: ignore
            conint(ge=0, le=4),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    num_post_message_passing_layers: Union[
        conlist(  # type: ignore
            conint(ge=1, le=8),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    aggregation: Union[
        conlist(  # type: ignore
            List[AggregationType],
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True, hidden=True),
        )

    activation: Union[
        conlist(  # type: ignore
            ActivationType,
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    normalization: Union[
        conlist(  # type: ignore
            Optional[NormalizationType],
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    # Link Prediction =========================================================

    module: Union[LinkPredOutputType, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(valid_task_types=TaskType.get_link_pred_tasks()),
    )

    handle_new_target_entities: Union[bool, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(valid_task_types=TaskType.get_link_pred_tasks()),
    )

    target_embedding_mode: Union[
        conlist(  # type: ignore
            RHSEmbeddingMode,
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(
                tunable=True,
                valid_task_types=TaskType.get_link_pred_tasks(),
            ),
        )

    output_embedding_dim: Union[
        conlist(  # type: ignore
            conint(ge=1, le=256),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(
                tunable=True,
                valid_task_types=TaskType.get_link_pred_tasks(),
            ),
        )

    ranking_embedding_loss_coeff: Union[
        conlist(  # type: ignore
            confloat(ge=0.0),
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(
                tunable=True,
                valid_task_types=[TaskType.TEMPORAL_LINK_PREDICTION],
            ),
        )

    distance_measure: Union[
        conlist(  # type: ignore
            DistanceMeasureType,
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(
                tunable=True,
                valid_task_types=TaskType.get_link_pred_tasks(),
            ),
        )

    # Private Preview Options =================================================

    use_seq_id: Union[
        conlist(  # type: ignore
            bool,
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(tunable=True),
        )

    prediction_time_encodings: Union[
        conlist(  # type: ignore
            bool,
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(
                tunable=True,
                valid_task_types=[
                    TaskType.REGRESSION,
                    TaskType.FORECASTING,
                    TaskType.BINARY_CLASSIFICATION,
                    TaskType.MULTICLASS_CLASSIFICATION,
                    TaskType.MULTILABEL_CLASSIFICATION,
                    TaskType.MULTILABEL_RANKING,
                ],
                valid_query_types=[QueryType.TEMPORAL],
            ),
        )

    past_encoder: Union[
        conlist(  # type: ignore
            Optional[PastEncoderType],
            min_items=1,
        ),
        MissingType] = Field(
            default=MissingType.VALUE,
            metadata=Metadata(
                tunable=True,
                valid_task_types=[TaskType.REGRESSION, TaskType.FORECASTING],
                valid_query_types=[QueryType.TEMPORAL],
            ),
        )

    handle_new_entities: Union[bool, MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(
            valid_task_types=[TaskType.REGRESSION, TaskType.FORECASTING],
            valid_query_types=[QueryType.TEMPORAL],
        ),
    )

    # Deprecated Options ======================================================

    forecast_type: Union[List[str], MissingType] = Field(
        default=MissingType.VALUE,
        metadata=Metadata(
            hidden=True,
            valid_task_types=[TaskType.REGRESSION, TaskType.FORECASTING],
            valid_query_types=[QueryType.TEMPORAL],
        ),
    )

    # =========================================================================

    @validator('channels')
    def is_even_channel(
        cls,
        values: Union[List[int], MissingType],
    ) -> Union[List[int], MissingType]:
        if isinstance(values, list):
            for value in values:
                if value % 2 != 0:
                    raise ValueError(f"'channels' requires an even number "
                                     f"(got {value})")
        return values


@dataclass(config=dict(validate_assignment=True), repr=False)  # type: ignore
class ModelPlan:
    r"""A complete definition of a Kumo model plan, encompassing a
    :class:`~kumoapi.model_plan.TrainingJobPlan`,
    :class:`~kumoapi.model_plan.ColumnProcessingPlan`,
    :class:`~kumoapi.model_plan.NeighborSamplingPlan`,
    :class:`~kumoapi.model_plan.OptimizationPlan`, and a
    :class:`~kumoapi.model_plan.ModelArchitecturePlan`. Please see the
    `Kumo documentation <https://docs.kumo.ai/docs/advanced-operations>`_
    for more information."""

    #: The training job plan.
    training_job: TrainingJobPlan = field(default_factory=TrainingJobPlan)

    # The column processing plan.
    column_processing: ColumnProcessingPlan = field(
        default_factory=ColumnProcessingPlan)

    #: The neighbor sampling plan.
    neighbor_sampling: NeighborSamplingPlan = field(
        default_factory=NeighborSamplingPlan)

    #: The model optimization plan.
    optimization: OptimizationPlan = field(default_factory=OptimizationPlan)

    #: The model architecture plan.
    model_architecture: ModelArchitecturePlan = field(
        default_factory=ModelArchitecturePlan)

    def __repr__(self) -> str:
        field_repr = '\n'.join(
            [f'{f.name}={getattr(self, f.name)},' for f in fields(self)])
        reprs = _add_indent(field_repr, num_spaces=2)
        return f'{self.__class__.__name__}(\n{reprs}\n)'


@dataclass
class ModelPlanInfo:
    model_plan: ModelPlan
    task_type: TaskType
    query_type: QueryType
    has_train_table_weight_col: bool = False


# =============================================================================


@dataclass
class SuggestModelPlanRequest:
    r"""A request to infer model plan based on `query_string`,
    `graph_id` , `run_mode`, and optionally `train_table_spec`
    if the original training table has been modified.
    """
    query_string: str
    graph_id: str
    run_mode: RunMode
    train_table_spec: Optional[TrainingTableSpec] = None
    graph_definition: Optional[GraphDefinition] = None


@dataclass
class SuggestModelPlanResponse:
    r"""A response containing metadata for a Kumo table."""
    model_plan: ModelPlan


def _add_indent(text: str, num_spaces: int) -> str:
    lines = text.split('\n')
    return '\n'.join([' ' * num_spaces + line for line in lines])
