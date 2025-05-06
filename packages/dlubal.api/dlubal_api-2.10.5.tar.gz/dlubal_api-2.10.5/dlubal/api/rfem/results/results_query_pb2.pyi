from dlubal.api.common import model_id_pb2 as _model_id_pb2
from dlubal.api.rfem.results import results_id_pb2 as _results_id_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ResultsQuery(_message.Message):
    __slots__ = ("model_id", "results_id", "filters")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    RESULTS_ID_FIELD_NUMBER: _ClassVar[int]
    FILTERS_FIELD_NUMBER: _ClassVar[int]
    model_id: _model_id_pb2.ModelId
    results_id: _results_id_pb2.ResultsId
    filters: _containers.RepeatedCompositeFieldContainer[ResultsFilter]
    def __init__(self, model_id: _Optional[_Union[_model_id_pb2.ModelId, _Mapping]] = ..., results_id: _Optional[_Union[_results_id_pb2.ResultsId, str]] = ..., filters: _Optional[_Iterable[_Union[ResultsFilter, _Mapping]]] = ...) -> None: ...

class ResultsFilter(_message.Message):
    __slots__ = ("column_id", "filter_expression")
    COLUMN_ID_FIELD_NUMBER: _ClassVar[int]
    FILTER_EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    column_id: str
    filter_expression: str
    def __init__(self, column_id: _Optional[str] = ..., filter_expression: _Optional[str] = ...) -> None: ...
