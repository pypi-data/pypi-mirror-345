from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from pydantic import Field
from pydantic.dataclasses import dataclass

from kumoapi.common import StrEnum
from kumoapi.data_snapshot import GraphSnapshotID
from kumoapi.graph import Edge, TableName
from kumoapi.task import TaskType


@dataclass
class OnlinePredictionOptions:
    # Required if prediction task is to perform binary classification.
    binary_classification_threshold: Optional[float] = None

    # On classification tasks, for each entity, we will only return predictions
    # for the K classes with the highest predicted values for the entity.
    # If empty, predict all class. This field is ignored for regression tasks.
    num_classes_to_return: Optional[int] = None


# Request body for either launch or patch(update) an online serving endpoint:
#
# To launch one:
#    POST /online_serving_endpoints {OnlineServingEndpointRequest body}
#      => return {OnlineServingEndpointResource} + 200 (upon success)
# To update one:
#    PATCH /online_serving_endpoints/{id} {OnlineServingEndpointRequest body}
#      => return {OnlineServingEndpointResource} + 200 (upon success)
@dataclass
class OnlineServingEndpointRequest:
    """POST request body to create an Online Serving endpoint."""
    # ID of a (successful) model training job.
    model_training_job_id: str

    predict_options: OnlinePredictionOptions

    # Optional, a specific Graph data snapshot to be loaded for online
    # prediction. If this field is absent in the launch or update request,
    # this instructs Kumo to refresh the graph data and load the most
    # recently refreshed graph data snapshot for online serving.
    graph_snapshot_id: Optional[GraphSnapshotID] = None

    # Estimated max # of requests per second. This field can be useful for Kumo
    # to provision sufficient serving capacity and to configure rate limiting
    # and/or load shedding.
    max_qps: int = 50


class OnlineServingStatusCode(StrEnum):
    # Online serving endpoint is alive and ready to accept traffic
    READY = 'ready'
    # We are still in progress to materialize data, provision resources,
    # or starting up server replicas.
    IN_PROGRESS = 'in_progress'

    # Failed to launch online serving endpoint, likely due to reasons such as
    # using an old model incompatible with online serving, insufficient
    # resources to launch too many replicas, etc.
    FAILED = 'failed'


@dataclass
class OnlineServingStatus:
    status_code: OnlineServingStatusCode

    # Most recently updated timestamp of current status.
    last_updated_at: datetime

    # Current stage while status_code is IN_PROGRESS.
    stage: Optional[str] = None
    # Message if status_code is FAILED.
    failure_message: Optional[str] = None


@dataclass
class OnlineServingUpdate:
    """
    Information/status about an update (PATCH) operation on an existing
    online serving endpoint.
    """
    prev_config: OnlineServingEndpointRequest
    target_config: OnlineServingEndpointRequest

    update_started_at: datetime
    update_status: OnlineServingStatus


@dataclass
class OnlineServingEndpointResource:
    id: str

    # Endpoint url would formatted as "<kumo cloud hostname>/gira/{id}"
    # where <kumo cloud hostname> is typical the your Kumo cloud web url such
    # as "https://<customer_id>.kumoai.cloud"
    endpoint_url: str

    config: OnlineServingEndpointRequest

    # Timestamp of when this endpoint resoruce was create.
    launched_at: datetime

    # Current status. The endpoint_url will be ready to serve traffic only if
    # status.status_code is READY
    status: OnlineServingStatus

    # The info/status about the most recent UPDATE operation on this endpoint,
    # if any.  Note that if the last update status is READY,
    # `update.target_config` would be identical to the `config` field,
    # otherwise `update.prev_config` would be identical to the `config` field.
    update: Optional[OnlineServingUpdate] = None


NodeId = Union[int, float, str]
TimestampNanos = int
NewNodeList = List[Tuple[NodeId, TimestampNanos]]
NewEdgeList = List[Tuple[NodeId, NodeId]]
# Row-oriented pandas dataframe for node features.
FeaturesDataframe = List[Dict[str, Any]]


@dataclass
class RealtimeFeatures:
    # TODO(siyang): the fields are used for testing now.

    # We are using List[Tuple] instead of Dict because TableInfo
    # as a key is not well supported when we serialize the object
    # before sending the request.
    # New nodes are represented as list of pairs of table info and
    # a list of tuples (node idx, time).
    # This field is only needed when the the node types have
    # timestamp columns.
    new_nodes: Optional[Dict[TableName, NewNodeList]] = None

    # New edges are represented as list of pairs of table info
    # and a list of tuples (node idx of table 1, node idx of table 2).
    new_edges: Optional[List[Tuple[Edge, NewEdgeList]]] = None

    # New features are represented as dict of table and row-oriented dataframe
    # node features in that table, where each row represents features of node.
    new_features: Optional[Dict[TableName, FeaturesDataframe]] = None


@dataclass
class OnlinePredictionRequest:
    fkey: NodeId
    time: Optional[TimestampNanos] = None
    realtime_features: Optional[RealtimeFeatures] = None


@dataclass
class BinaryClassificationResult:
    pred: bool
    true_prob: float
    type: Literal[
        TaskType.BINARY_CLASSIFICATION] = TaskType.BINARY_CLASSIFICATION

    @property
    def pred_prob(self) -> float:
        return self.true_prob if self.pred else self.false_prob

    @property
    def false_prob(self) -> float:
        return 1 - self.true_prob

    @property
    def prob(self) -> Dict[bool, float]:
        return {True: self.true_prob, False: self.false_prob}


@dataclass
class MulticlassClassificationResult:
    pred: str
    prob: Dict[str, float]
    type: Literal[
        TaskType.
        MULTICLASS_CLASSIFICATION] = TaskType.MULTICLASS_CLASSIFICATION

    @property
    def pred_prob(self) -> float:
        return self.prob[self.pred]


@dataclass
class MultilabelClassificationResult:
    pred: List[str]
    prob: Dict[str, float]
    type: Literal[
        TaskType.
        MULTILABEL_CLASSIFICATION] = TaskType.MULTILABEL_CLASSIFICATION

    @property
    def pred_prob(self) -> List[float]:
        return [self.prob[p] for p in self.pred]


@dataclass
class RegressionResult:
    pred: float
    type: Literal[TaskType.REGRESSION] = TaskType.REGRESSION


OnlinePredictionResult = Union[BinaryClassificationResult,
                               MulticlassClassificationResult,
                               MultilabelClassificationResult,
                               RegressionResult]


@dataclass
class OnlinePredictionResponse:
    result: OnlinePredictionResult = Field(discriminator='type')
