from DDPathGenerator.naive_path_generator import generate_sequential_path_shifted, _generate_partial_iter, \
    _generate_shifted_iter
import pytest

TEST_PATH_SEQUENTIAL_SHIFTED = "SEQ_SHIFTED"
TEST_PATH_ITERATIVE_SHIFTED = "ITER_SHIFTED"
TEST_PATH_ITERATIVE_SHIFTED_PARTIAL = "ITER_SHIFTED_PARTIAL"


pytestmark = pytest.mark.parametrize("pos_tensor_list,shift_end,expected_paths",
                                     [
                                         (   # Equivalent of having a 4 gate circuit and simulate them in open - open
                                             [0, 1, 2, 3],
                                             0,
                                             {
                                                 TEST_PATH_SEQUENTIAL_SHIFTED: [(0, 1), (0, 2), (0, 1)],
                                                 TEST_PATH_ITERATIVE_SHIFTED_PARTIAL: [(0, 1), (0, 1)],
                                                 TEST_PATH_ITERATIVE_SHIFTED: [(0, 1), (0, 1), (0, 1)]
                                             }
                                         ),
                                         (   # Equivalent of having a 4 gate circuit and simulate them in open - close
                                             [0, 1, 2, 3],
                                             1,
                                             {
                                                 TEST_PATH_SEQUENTIAL_SHIFTED: [(0, 1), (0, 3), (0, 2)],
                                                 TEST_PATH_ITERATIVE_SHIFTED_PARTIAL: [(0, 1), (0, 1)],
                                                 TEST_PATH_ITERATIVE_SHIFTED: [(0, 1), (0, 1), (1, 2)]
                                             }
                                         ),
                                         (   # Equivalent of having a 4 gate circuit and simulate them in close - open
                                             [1, 2, 3, 4],
                                             0,
                                             {
                                                 TEST_PATH_SEQUENTIAL_SHIFTED: [(1, 2), (1, 3), (1, 2)],
                                                 TEST_PATH_ITERATIVE_SHIFTED_PARTIAL: [(1, 2), (1, 2)],
                                                 TEST_PATH_ITERATIVE_SHIFTED: [(1, 2), (1, 2), (1, 2)]
                                             }
                                         ),
                                         (   # Equivalent of having a 4 gate circuit and simulate them in close - close
                                             [1, 2, 3, 4],
                                             1,
                                             {
                                                 TEST_PATH_SEQUENTIAL_SHIFTED: [(1, 2), (1, 4), (1, 3)],
                                                 TEST_PATH_ITERATIVE_SHIFTED_PARTIAL: [(1, 2), (1, 2)],
                                                 TEST_PATH_ITERATIVE_SHIFTED: [(1, 2), (1, 2), (2, 3)]
                                             }
                                         ),
                                         (   # Equivalent of having a 6 gate circuit and simulate them in close - close
                                             [1, 2, 3, 4, 5],
                                             1,
                                             {
                                                 TEST_PATH_SEQUENTIAL_SHIFTED: [(1, 2), (1, 5), (1, 4), (1, 3)],
                                                 TEST_PATH_ITERATIVE_SHIFTED_PARTIAL: [(1, 2), (1, 2), (1, 5)],
                                                 TEST_PATH_ITERATIVE_SHIFTED: [(1, 2), (1, 2), (1, 5), (2, 3)]
                                             }
                                         )
                                     ])


class TestNaivePathGenerator:
    def test_sequential_path_shifted(self, pos_tensor_list, shift_end, expected_paths):
        path = generate_sequential_path_shifted(list(pos_tensor_list), shift_end)
        assert path == expected_paths[TEST_PATH_SEQUENTIAL_SHIFTED]

    def test_iterative_path_shifted_partial(self, pos_tensor_list, shift_end, expected_paths):
        shift_ini = min(pos_tensor_list)
        n_gates = len(pos_tensor_list)
        total_gates = n_gates + shift_ini + shift_end
        path = _generate_partial_iter(n=n_gates, total_gates=total_gates, first=shift_ini)
        assert path == expected_paths[TEST_PATH_ITERATIVE_SHIFTED_PARTIAL]

    def test_iterative_path_shifted(self, pos_tensor_list, shift_end, expected_paths):
        shift_ini = min(pos_tensor_list)
        n_gates = len(pos_tensor_list) + shift_ini + shift_end
        path = _generate_shifted_iter(n_gates=n_gates, shift_ini=shift_ini, shift_end=shift_end)
        assert path == expected_paths[TEST_PATH_ITERATIVE_SHIFTED]

