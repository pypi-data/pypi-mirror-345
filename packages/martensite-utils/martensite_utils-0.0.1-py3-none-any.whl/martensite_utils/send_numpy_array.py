import numpy as np
import requests

from martensite_utils import numpy_to_proto


def post_numpy_array(array: np.ndarray, url: str) -> requests.Response:
    proto = numpy_to_proto(array)

    response = requests.post(
        url,
        data=proto.SerializeToString(),
        headers={"Content-Type": "application/octet-stream"}
    )

    return response
