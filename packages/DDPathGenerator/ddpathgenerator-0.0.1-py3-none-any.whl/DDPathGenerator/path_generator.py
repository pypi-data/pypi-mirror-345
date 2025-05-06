from .naive_path_generator import generate_sequential_path, generate_k_ops_path, generate_iter_path
from .literal import PATH_SEQUENTIAL, PATH_KOPS, PATH_ITER
from .data import TensorNetwork


class PathGenerator:
    def __init__(self, tensor_list, open_indices):
        self.tensor_network = TensorNetwork(tensor_list, open_indices)

    def generate_path(self, selected_path: str):
        path = None
        if selected_path == PATH_SEQUENTIAL:
            path = generate_sequential_path(self.tensor_network)
        elif selected_path == PATH_KOPS:
            path = generate_k_ops_path(self.tensor_network)
        elif selected_path == PATH_ITER:
            path = generate_iter_path(self.tensor_network)
        return path



