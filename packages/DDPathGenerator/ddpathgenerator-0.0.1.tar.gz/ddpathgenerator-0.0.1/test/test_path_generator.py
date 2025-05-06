from DDPathGenerator import PathGenerator, PATH_SEQUENTIAL, PATH_KOPS, PATH_ITER
import pytest


pytestmark = pytest.mark.parametrize("tensor_list,open_indices,expected_paths",
                                     [
                                         (   # Simple circuit with 3 qubits and 2 cx simulated open - open
                                             (
                                                ('x0', 'y0', 'x1', 'x1_1'),
                                                ('x2', 'y2', 'x1_1', 'y1'),
                                             ),
                                             ('x0', 'x1', 'x2', 'y0', 'y1', 'y2'),
                                             {
                                                PATH_SEQUENTIAL: [(0, 1)],
                                                PATH_KOPS: [(0, 1)],
                                                PATH_ITER: [(0, 1)]
                                             }
                                         ),
                                         (   # Simple circuit with 3 qubits and 2 cx simulated close - open
                                             (
                                                ('x0',),
                                                ('x1',),
                                                ('x2',),
                                                ('x0', 'y0', 'x1', 'x1_1'),
                                                ('x2', 'y2', 'x1_1', 'y1'),
                                             ),
                                             ('y0', 'y1', 'y2'),
                                             {
                                                PATH_SEQUENTIAL: [(0, 1), (0, 3), (0, 2), (0, 1)],
                                                PATH_KOPS: [(3, 4), (0, 1), (0, 2), (0, 1)],
                                                PATH_ITER: [(3, 4), (0, 1), (0, 2), (0, 1)]
                                             }
                                         ),
                                         (   # Simple circuit with 3 qubits and 2 cx simulated open - close
                                             (
                                                ('x0', 'y0', 'x1', 'x1_1'),
                                                ('x2', 'y2', 'x1_1', 'y1'),
                                                ('y0',),
                                                ('y1',),
                                                ('y2',),
                                             ),
                                             ('x0', 'x1', 'x2'),
                                             {
                                                PATH_SEQUENTIAL: [(0, 1), (0, 3), (0, 2), (0, 1)],
                                                PATH_KOPS: [(0, 1), (0, 1), (0, 2), (0, 1)],
                                                PATH_ITER: [(0, 1), (0, 1), (0, 2), (0, 1)]
                                             }
                                         ),
                                         (   # Simple circuit with 3 qubits and 2 cx simulated close - close
                                             (
                                                ('x0',),
                                                ('x1',),
                                                ('x2',),
                                                ('x0', 'y0', 'x1', 'x1_1'),
                                                ('x2', 'y2', 'x1_1', 'y1'),
                                                ('y0',),
                                                ('y1',),
                                                ('y2',),
                                             ),
                                             (),
                                             {
                                                PATH_SEQUENTIAL: [
                                                    (0, 1), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1),
                                                ],
                                                PATH_KOPS: [
                                                    (3, 4), (3, 4), (3, 5),
                                                    (0, 1), (0, 3), (0, 2), (0, 1)
                                                ],
                                                PATH_ITER: [(3, 4), (0, 1), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1)]
                                             }
                                         ),
                                         (   # Simple circuit with 3 qubits and 3h-3cx-2x simulated open - open
                                             (
                                                 ('x0', 'x0_1'),
                                                 ('x1', 'x1_1'),
                                                 ('x2', 'x2_1'),
                                                 ('x0_1', 'x1_1', 'x1_2'),
                                                 ('x2_1', 'y2', 'x1_2', 'x1_3'),
                                                 ('x1_3', 'x0_1', 'x0_2'),
                                                 ('x0_2', 'y0'),
                                                 ('x1_3', 'y1')
                                             ),
                                             ('x0', 'x1', 'x2', 'y0', 'y1', 'y2'),
                                             {
                                                PATH_SEQUENTIAL: [
                                                    (0, 1), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1),
                                                ],
                                                PATH_KOPS: [
                                                    (0, 1), (0, 6), (0, 5),
                                                    (0, 1), (0, 3), (0, 2),
                                                    (0, 1)
                                                ],
                                                PATH_ITER: [
                                                    (0, 1), (0, 1), (0, 1), (0, 1),
                                                    (0, 1), (0, 1),
                                                    (0, 1)
                                                ]
                                             }
                                         ),
                                         (   # Simple circuit with 3 qubits and 3h-3cx-2x simulated close - open
                                             (
                                                 ('x0',),
                                                 ('x1',),
                                                 ('x2',),
                                                 ('x0', 'x0_1'),
                                                 ('x1', 'x1_1'),
                                                 ('x2', 'x2_1'),
                                                 ('x0_1', 'x1_1', 'x1_2'),
                                                 ('x2_1', 'y2', 'x1_2', 'x1_3'),
                                                 ('x1_3', 'x0_1', 'x0_2'),
                                                 ('x0_2', 'y0'),
                                                 ('x1_3', 'y1'),
                                             ),
                                             ('y0', 'y1', 'y2'),
                                             {
                                                PATH_SEQUENTIAL: [
                                                    (0, 1), (0, 9), (0, 8), (0, 7), (0, 6),
                                                    (0, 5), (0, 4), (0, 3), (0, 2), (0, 1),
                                                ],
                                                PATH_KOPS: [
                                                    (3, 4), (3, 9), (3, 8),
                                                    (3, 4), (3, 6), (3, 5),
                                                    (0, 1), (0, 3), (0, 2), (0, 1)
                                                ],
                                                PATH_ITER: [
                                                    (3, 4), (3, 4), (3, 4), (3, 4),
                                                    (3, 4), (3, 4),
                                                    (3, 4),
                                                    (0, 1), (0, 2), (0, 1)
                                                ]
                                             }
                                         ),
                                         (   # Simple circuit with 3 qubits and 3h-3cx-2x simulated open - close
                                             (
                                                 ('x0', 'x0_1'),
                                                 ('x1', 'x1_1'),
                                                 ('x2', 'x2_1'),
                                                 ('x0_1', 'x1_1', 'x1_2'),
                                                 ('x2_1', 'y2', 'x1_2', 'x1_3'),
                                                 ('x1_3', 'x0_1', 'x0_2'),
                                                 ('x0_2', 'y0'),
                                                 ('x1_3', 'y1'),
                                                 ('y0',),
                                                 ('y1',),
                                                 ('y2',)
                                             ),
                                             ('x0', 'x1', 'x2'),
                                             {
                                                PATH_SEQUENTIAL: [
                                                    (0, 1), (0, 9), (0, 8), (0, 7), (0, 6),
                                                    (0, 5), (0, 4), (0, 3), (0, 2), (0, 1),
                                                ],
                                                PATH_KOPS: [
                                                    (0, 1), (0, 9), (0, 8),
                                                    (0, 1), (0, 6), (0, 5),
                                                    (0, 1), (0, 3),
                                                    (0, 1), (0, 1)
                                                ],
                                                PATH_ITER: [
                                                    (0, 1), (0, 1), (0, 1), (0, 1),
                                                    (3, 4), (3, 4),
                                                    (3, 4),
                                                    (0, 1), (0, 2), (0, 1)
                                                ]
                                             }
                                         ),
                                         (   # Simple circuit with 3 qubits and 3h-3cx-2x simulated close - close
                                             (
                                                 ('x0',),
                                                 ('x1',),
                                                 ('x2',),
                                                 ('x0', 'x0_1'),
                                                 ('x1', 'x1_1'),
                                                 ('x2', 'x2_1'),
                                                 ('x0_1', 'x1_1', 'x1_2'),
                                                 ('x2_1', 'y2', 'x1_2', 'x1_3'),
                                                 ('x1_3', 'x0_1', 'x0_2'),
                                                 ('x0_2', 'y0'),
                                                 ('x1_3', 'y1'),
                                                 ('y0',),
                                                 ('y1',),
                                                 ('y2',)
                                             ),
                                             (),
                                             {
                                                PATH_SEQUENTIAL: [
                                                    (0, 1), (0, 12), (0, 11), (0, 10), (0, 9), (0, 8),
                                                    (0, 7), (0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1),
                                                ],
                                                PATH_KOPS: [
                                                    (3, 4), (3, 12), (3, 11),
                                                    (3, 4), (3, 9), (3, 8),
                                                    (3, 4), (3, 6),
                                                    (0, 1), (0, 4), (0, 3), (0, 2), (0, 1)
                                                ],
                                                PATH_ITER: [
                                                    (3, 4), (3, 4), (3, 4), (3, 4),
                                                    (6, 7), (6, 7),
                                                    (6, 7),
                                                    (0, 1), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1)
                                                ]
                                             }
                                         )
                                     ])


class ITest:
    def assert_path(self, tensor_list, open_indices, expected_paths, path_name):
        pg = PathGenerator(tensor_list, open_indices)
        path = pg.generate_path(path_name)
        assert path == expected_paths[path_name]


class TestPathGenerator(ITest):
    def test_sequential_path(self, tensor_list, open_indices, expected_paths):
        self.assert_path(tensor_list, open_indices, expected_paths, PATH_SEQUENTIAL)

    def test_kops_path(self, tensor_list, open_indices, expected_paths):
        self.assert_path(tensor_list, open_indices, expected_paths, PATH_KOPS)

    def test_iter_path(self, tensor_list, open_indices, expected_paths):
        self.assert_path(tensor_list, open_indices, expected_paths, PATH_ITER)
