import numpy as np

from martensite_utils import proto_to_numpy, numpy_to_proto


def full_integration_test():
    x = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.6]
    ])

    proto = numpy_to_proto(x)
    y = proto_to_numpy(proto)

    if (x != y).any() or (x.shape != y.shape):
        print(f'x:\n\t{x}')
        print(f'y:\n\t{y}')
        raise ValueError("X and Y do not match!")
    
    print("Test passed!")


if __name__ == '__main__':
    full_integration_test()
