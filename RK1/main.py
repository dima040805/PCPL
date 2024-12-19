from operator import itemgetter


class Procedure:
    def __init__(self, id, name, priority, db_id):
        self.id = id
        self.name = name
        self.priority = priority
        self.db_id = db_id


class DataBase:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class ProcedureInDataBase:
    def __init__(self, db_id, proc_id):
        self.db_id = db_id
        self.proc_id = proc_id


databases = [
    DataBase(1, 'Main db'),
    DataBase(2, 'Users db'),
    DataBase(3, 'Analytics db'),
    DataBase(4, 'Debug db'),
    DataBase(5, 'Products db'),
]

procedures = [
    Procedure(1, 'login',1, 1),
    Procedure(2, 'get user name', 2, 2),
    Procedure(3, 'get user email', 4, 2),
    Procedure(4, 'check user status', 5, 2),
    Procedure(5, 'build diagram',10,  3),
    Procedure(6, 'add tests', 14, 4),
    Procedure(7, 'get errors list', 22, 4),
    Procedure(8, 'add new product', 14, 5)
]

procedures_in_dbs = [
    ProcedureInDataBase(1, 1),
    ProcedureInDataBase(2, 1),
    ProcedureInDataBase(2, 2),
    ProcedureInDataBase(2, 3),
    ProcedureInDataBase(2, 4),
    ProcedureInDataBase(3, 5),
    ProcedureInDataBase(4, 6),
    ProcedureInDataBase(4, 7),
    ProcedureInDataBase(5, 8),
]


one_to_many = [
    (proc.name, proc.priority, db.name)
    for db in databases
    for proc in procedures
    if proc.db_id == db.id
]

many_to_many_temp = [
    (db.name, proc_in_db.db_id, proc_in_db.proc_id)
    for db in databases
    for proc_in_db in procedures_in_dbs
    if db.id == proc_in_db.db_id
]

many_to_many = [
    (proc.name, proc.priority, db_name)
    for db_name, db_id, proc_id in many_to_many_temp
    for proc in procedures if proc.id == proc_id
]


def main():
    print('Задание 1:\nСписок процедур, у которых название начинается на букву "g" и '
          'названия баз данных, в которых они хранятся')
    print([(x[0], x[2]) for x in one_to_many if x[0].startswith('g')])
    print('\nЗадание 2:\nСписок баз данных с минимальным приоритетом процедуры')
    dbs = {}
    for i in one_to_many:
        if i[-1] in dbs:
            dbs[i[-1]].append(i[:2])
        else:
            dbs[i[-1]] = [i[:2]]
    ans = [[db, min(dbs[db], key=lambda x: x[1])[1]] for db in dbs]
    ans.sort(key=lambda x: x[1])
    print(ans)
    print('\nЗадание 3:\nСписок всех процедур во всех базах данных (отсортировано по названию процедур)')
    for proc_name, proc_priority, db_name in sorted(many_to_many, key=itemgetter(0)):
        print(f'Процедура {proc_name} с приоритетом {proc_priority} находится в базе данных {db_name}')


if __name__ == '__main__':
    main()
