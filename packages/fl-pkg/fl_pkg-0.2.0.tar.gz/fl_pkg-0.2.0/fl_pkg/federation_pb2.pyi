from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Parameters(_message.Message):
    __slots__ = ("tensors", "tensor_type")
    TENSORS_FIELD_NUMBER: _ClassVar[int]
    TENSOR_TYPE_FIELD_NUMBER: _ClassVar[int]
    tensors: _containers.RepeatedScalarFieldContainer[bytes]
    tensor_type: str
    def __init__(self, tensors: _Optional[_Iterable[bytes]] = ..., tensor_type: _Optional[str] = ...) -> None: ...

class ServerMessage(_message.Message):
    __slots__ = ("fit_ins", "evaluate_ins", "finished")
    class Finished(_message.Message):
        __slots__ = ("finished",)
        FINISHED_FIELD_NUMBER: _ClassVar[int]
        finished: bool
        def __init__(self, finished: bool = ...) -> None: ...
    class FitIns(_message.Message):
        __slots__ = ("parameters",)
        PARAMETERS_FIELD_NUMBER: _ClassVar[int]
        parameters: Parameters
        def __init__(self, parameters: _Optional[_Union[Parameters, _Mapping]] = ...) -> None: ...
    class EvaluateIns(_message.Message):
        __slots__ = ("parameters", "config")
        class ConfigEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: Scalar
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Scalar, _Mapping]] = ...) -> None: ...
        PARAMETERS_FIELD_NUMBER: _ClassVar[int]
        CONFIG_FIELD_NUMBER: _ClassVar[int]
        parameters: Parameters
        config: _containers.MessageMap[str, Scalar]
        def __init__(self, parameters: _Optional[_Union[Parameters, _Mapping]] = ..., config: _Optional[_Mapping[str, Scalar]] = ...) -> None: ...
    FIT_INS_FIELD_NUMBER: _ClassVar[int]
    EVALUATE_INS_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    fit_ins: ServerMessage.FitIns
    evaluate_ins: ServerMessage.EvaluateIns
    finished: ServerMessage.Finished
    def __init__(self, fit_ins: _Optional[_Union[ServerMessage.FitIns, _Mapping]] = ..., evaluate_ins: _Optional[_Union[ServerMessage.EvaluateIns, _Mapping]] = ..., finished: _Optional[_Union[ServerMessage.Finished, _Mapping]] = ...) -> None: ...

class ClientMessage(_message.Message):
    __slots__ = ("fit_res", "evaluate_res")
    class FitRes(_message.Message):
        __slots__ = ("parameters", "num_examples")
        PARAMETERS_FIELD_NUMBER: _ClassVar[int]
        NUM_EXAMPLES_FIELD_NUMBER: _ClassVar[int]
        parameters: Parameters
        num_examples: int
        def __init__(self, parameters: _Optional[_Union[Parameters, _Mapping]] = ..., num_examples: _Optional[int] = ...) -> None: ...
    class EvaluateRes(_message.Message):
        __slots__ = ("loss", "num_examples", "metrics")
        class MetricsEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: Scalar
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Scalar, _Mapping]] = ...) -> None: ...
        LOSS_FIELD_NUMBER: _ClassVar[int]
        NUM_EXAMPLES_FIELD_NUMBER: _ClassVar[int]
        METRICS_FIELD_NUMBER: _ClassVar[int]
        loss: float
        num_examples: int
        metrics: _containers.MessageMap[str, Scalar]
        def __init__(self, loss: _Optional[float] = ..., num_examples: _Optional[int] = ..., metrics: _Optional[_Mapping[str, Scalar]] = ...) -> None: ...
    FIT_RES_FIELD_NUMBER: _ClassVar[int]
    EVALUATE_RES_FIELD_NUMBER: _ClassVar[int]
    fit_res: ClientMessage.FitRes
    evaluate_res: ClientMessage.EvaluateRes
    def __init__(self, fit_res: _Optional[_Union[ClientMessage.FitRes, _Mapping]] = ..., evaluate_res: _Optional[_Union[ClientMessage.EvaluateRes, _Mapping]] = ...) -> None: ...

class Scalar(_message.Message):
    __slots__ = ("double", "float", "uint64", "sint64", "bool", "string", "bytes")
    DOUBLE_FIELD_NUMBER: _ClassVar[int]
    FLOAT_FIELD_NUMBER: _ClassVar[int]
    UINT64_FIELD_NUMBER: _ClassVar[int]
    SINT64_FIELD_NUMBER: _ClassVar[int]
    BOOL_FIELD_NUMBER: _ClassVar[int]
    STRING_FIELD_NUMBER: _ClassVar[int]
    BYTES_FIELD_NUMBER: _ClassVar[int]
    double: float
    float: float
    uint64: int
    sint64: int
    bool: bool
    string: str
    bytes: bytes
    def __init__(self, double: _Optional[float] = ..., float: _Optional[float] = ..., uint64: _Optional[int] = ..., sint64: _Optional[int] = ..., bool: bool = ..., string: _Optional[str] = ..., bytes: _Optional[bytes] = ...) -> None: ...
