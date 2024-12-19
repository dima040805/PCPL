import unittest
from main import *


class TestTasks(unittest.TestCase):
    def setUp(self):
        self.databases = [
            DataBase(1, 'Main db'),
            DataBase(2, 'Users db'),
            DataBase(3, 'Analytics db'),
            DataBase(4, 'Debug db'),
            DataBase(5, 'Products db')
        ]

        self.procedures = [
            Procedure(1, 'login', 1, 1),
            Procedure(2, 'get user name', 2, 2),
            Procedure(3, 'get user email', 4, 2),
            Procedure(4, 'check user status', 5, 2),
            Procedure(5, 'build diagram', 10, 3),
            Procedure(6, 'add tests', 14, 4),
            Procedure(7, 'get errors list', 22, 4),
            Procedure(8, 'add new product', 14, 5)
        ]

        self.procedures_in_dbs = [
            ProcedureInDataBase(1, 1),
            ProcedureInDataBase(2, 1),
            ProcedureInDataBase(2, 2),
            ProcedureInDataBase(2, 3),
            ProcedureInDataBase(2, 4),
            ProcedureInDataBase(3, 5),
            ProcedureInDataBase(4, 6),
            ProcedureInDataBase(4, 7),
            ProcedureInDataBase(5, 8)
        ]

        self.one_to_many = create_one_to_many(self.procedures, self.databases)
        self.many_to_many = create_many_to_many(self.procedures, self.databases, self.procedures_in_dbs)

    def test_task1(self):
        result = task1(self.one_to_many)
        true_result = [('get user name', 'Users db'), ('get user email', 'Users db'), ('get errors list', 'Debug db')]
        self.assertEqual(result, true_result)

    def test_task2(self):
        result = task2(self.one_to_many)
        true_result = [['Main db', 1], ['Users db', 2], ['Analytics db', 10], ['Debug db', 14], ['Products db', 14]]
        self.assertEqual(result, true_result)

    def test_task3(self):
        result = task3(self.many_to_many)
        true_result = [
            'Процедура add new product с приоритетом 14 находится в базе данных Products db',
            'Процедура add tests с приоритетом 14 находится в базе данных Debug db',
            'Процедура build diagram с приоритетом 10 находится в базе данных Analytics db',
            'Процедура check user status с приоритетом 5 находится в базе данных Users db',
            'Процедура get errors list с приоритетом 22 находится в базе данных Debug db',
            'Процедура get user email с приоритетом 4 находится в базе данных Users db',
            'Процедура get user name с приоритетом 2 находится в базе данных Users db',
            'Процедура login с приоритетом 1 находится в базе данных Main db',
            'Процедура login с приоритетом 1 находится в базе данных Users db'
        ]
        self.assertEqual(result, true_result)


if __name__ == '__main__':
    unittest.main()
