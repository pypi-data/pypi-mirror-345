import numpy as np

import martensite_utils.message_pb2 as message_pb2


numpy_types = {
    "int64": np.int64,
    "float64": np.float64,
    "float32": np.float32
}


def proto_to_numpy(proto_message: message_pb2.NDArrayProto) -> np.ndarray:
    dtype = numpy_types[proto_message.dtype]
    array = np.frombuffer(proto_message.data, dtype=dtype).reshape(proto_message.shape)
    return array
