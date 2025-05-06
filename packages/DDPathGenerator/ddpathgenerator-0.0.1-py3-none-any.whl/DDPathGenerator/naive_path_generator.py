from .data import TensorNetwork

import math


def _get_number_of_init_tensors(pg: TensorNetwork):
    """
    Calculates the number of tensors with only one index at the beginning of the tensor list. This will be
    considered the input state of the Tensor Network (if it has the input closed)
    :param pg: Object of the TensorNetwork containing all the relevant information of the circuit to contract
    :return: Number of tensors at the beginning of the list with only one index represented as int
    """
    n_tensors_init = 0
    while len(pg.tensor_list[n_tensors_init]) == 1:
        n_tensors_init += 1
    return n_tensors_init


def _get_number_of_end_tensors(pg: TensorNetwork):
    """
    Calculates the number of tensors with only one index at the end of the tensor list. This will be considered
    the output state of the Tensor Network (if it has the output closed)
    :param pg: Object of the TensorNetwork containing all the relevant information of the circuit to contract
    :return: Number of tensors at the end of the list with only one index represented as int
    """
    n = len(pg.tensor_list)
    n_tensors_end = 0
    while len(pg.tensor_list[n - n_tensors_end - 1]) == 1:
        n_tensors_end += 1
    return n_tensors_end


def generate_sequential_path_shifted(pos_tensor_list: list, shift_end=0):
    """
        Generalization for calculating the contraction path using the sequential heuristic. Can calculate the
        path for a given list of tensors of the tensor network, without the need of including all of them.
        Input:
        :param pos_tensor_list: Int list containing the position of all the tensors to contract
        :param shift_end: Number of tensor to be ignored that are at the right of the pos_tensor_list tensors
        Output:
        :return: The generated path for the pos_tensor_list tensors
    """
    if len(pos_tensor_list) < 2:
        return []
    shift_ini = min(pos_tensor_list)
    pos_tensor_list.remove(shift_ini)
    path = [(shift_ini, pos_tensor_list[0])]
    pos_tensor_list.remove(pos_tensor_list[0])
    for i in range(len(pos_tensor_list)):
        pos_tensor = pos_tensor_list[i]
        path.append((pos_tensor - i - 2, shift_ini + shift_end + len(pos_tensor_list) - i))
    return path


def generate_sequential_path(pg: TensorNetwork):
    """
    Calculates the path for a given TensorNetwork using the sequential heuristic
    :param pg: Object of the TensorNetwork containing all the relevant information of the circuit to contract
    :return: The generated path for the given TensorNetwork using the sequential path
    """
    return generate_sequential_path_shifted(list(range(len(pg.tensor_list))))


def generate_k_ops_path(pg: TensorNetwork, k=4):
    """
    Calculates the path for a given TensorNetwork using the K-Ops heuristic
    :param pg: Object of the TensorNetwork containing all the relevant information of the circuit to contract
    :param k: int value that set the number of contractions per operation block
    :return: The generated path for the given TensorNetwork using the sequential path
    """
    shift_ini = _get_number_of_init_tensors(pg)
    shift_end = _get_number_of_end_tensors(pg)
    n = len(pg.tensor_list)
    n_gates = n - shift_ini - shift_end
    n_block = math.ceil((n_gates / k))
    path = []
    pos_tensors = [shift_ini + i for i in range(k)]
    for i in range(n_block):
        n_remain_gates = n_gates - k * i
        n_gates_interval = min(n_remain_gates, k)
        block_shift_end = shift_end + (n_remain_gates - n_gates_interval)
        path = path + generate_sequential_path_shifted(pos_tensors[0:n_gates_interval], block_shift_end + i)
    end_interval_first_pos = shift_ini
    end_interval = [end_interval_first_pos + i for i in range(shift_end)]
    path = path + generate_sequential_path_shifted(end_interval, n_block)
    final_interval = [i for i in range(shift_ini + n_block + (1 if shift_end != 0 else 0))]
    path = path + generate_sequential_path_shifted(final_interval, 0)
    return path


def _generate_partial_iter(n: int, total_gates: int, first=0):
    if n < 2:
        return []
    partial_path = []
    i = 0
    while i < n - 1:
        partial_path.append((first, first + 1))
        i += 2
    if n % 2 != 0:
        partial_path.append((first, total_gates - (n // 2)))
    return partial_path


def _generate_shifted_iter(n_gates: int, shift_ini=0, shift_end=0):
    """
    Generalization for calculating the contraction path using the iterative heuristic. Can calculate the
        path for a given number of tensor, without the need of including all of them.
    :param n_gates:    Number of gates to contract
    :param shift_ini:  Number of tensor to be ignored that are at the left of the tensors list
    :param shift_end:  Number of tensor to be ignored that are at the right of the tensors list
    :return: The generated path, in the form of list of pos indices
    """
    n = n_gates - shift_ini - shift_end
    first = shift_ini
    path = _generate_partial_iter(n=n, total_gates=n_gates, first=first)
    n = (n - n % 2) // 2
    first += shift_end
    while n > 1:
        remain_gates = n + first
        path += _generate_partial_iter(n=n, total_gates=remain_gates, first=first)
        n = (n - n % 2) // 2
    return path


def generate_iter_path(pg: TensorNetwork):
    """
    Calculates the path for a given TensorNetwork using the iterative heuristic
    :param pg: Object of the TensorNetwork containing all the relevant information of the circuit to contract
    :return: The generated path for the given TensorNetwork using the iterative path
    """
    shift_ini = _get_number_of_init_tensors(pg)
    shift_end = _get_number_of_end_tensors(pg)
    n = len(pg.tensor_list)
    last_gates = shift_ini + shift_end + 1

    return _generate_shifted_iter(n_gates=n, shift_ini=shift_ini, shift_end=shift_end) + \
           generate_sequential_path_shifted(list(range(last_gates)))
