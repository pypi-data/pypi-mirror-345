import unittest
from iot_uncertainty.sat.constraint_solver import ConstraintSolver

class TestConstraintSolver(unittest.TestCase):
    def test_satisfiable(self):
        solver = ConstraintSolver()
        solver.encode_constraints([[1], [2]])
        self.assertTrue(solver.is_satisfiable())

    def test_unsatisfiable(self):
        solver = ConstraintSolver()
        solver.encode_constraints([[1], [-1]])
        self.assertFalse(solver.is_satisfiable())

if __name__ == "__main__":
    unittest.main()
