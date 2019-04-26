
import json
import luigi
import radb
import sqlparse
import unittest

import raopt
import ra2mr
import sql2ra

import test_ra2mr


'''
May be called like any Python unittest, or using pytest, e.g. "pytest test_e2e.py -p no:warnings".
'''

class End2EndUnitTests(unittest.TestCase):
    
    def setUp(self):
        test_ra2mr.prepareMockFileSystem()

    def _evaluate(self, sqlstring):
        dd = {}
        dd["Person"] = {"name": "string", "age": "integer", "gender": "string"}
        dd["Eats"] = {"name": "string", "pizza": "string"}
        dd["Serves"] = {"pizzeria": "string", "pizza": "string", "price": "integer"}
        
        stmt = sqlparse.parse(sqlstring)[0]
        ra0 = sql2ra.translate(stmt)
        
        ra1 = raopt.rule_break_up_selections(ra0)
        ra2 = raopt.rule_push_down_selections(ra1, dd)

        ra3 = raopt.rule_merge_selections(ra2)
        ra4 = raopt.rule_introduce_joins(ra3)

        task = ra2mr.task_factory(ra4, env=ra2mr.ExecEnv.MOCK)
        luigi.build([task], local_scheduler=True)

        f = task.output().open('r')
        lines = []
        for line in f:
            lines.append(line)
        return lines

    def test_select_person(self):
        sqlstring = "select distinct * from Person"
        computed = self._evaluate(sqlstring)
        self.assertEqual(len(computed), 9)

    def test_select_person_age_16(self):
        sqlstring = "select distinct * from Person where age = 16"
        computed = self._evaluate(sqlstring)
        self.assertEqual(len(computed), 1)

    def test_select_person_age_gender(self):
        sqlstring = "select distinct * from Person where gender='female' and age=16"
        computed = self._evaluate(sqlstring)
        self.assertEqual(len(computed), 1)

    def test_project_name(self):
        sqlstring = "select distinct name from Person"
        computed = self._evaluate(sqlstring)
        self.assertEqual(len(computed), 9)

    def test_project_name_age(self):
        sqlstring = "select distinct name, age from Person"
        computed = self._evaluate(sqlstring)
        self.assertEqual(len(computed), 9)
        self.assertIn({"Person.name": "Amy", "Person.age": 16}, [json.loads(tuple.split('\t')[1]) for tuple in computed])

    def test_person_join_eats(self):
        sqlstring = "select distinct * from Person, Eats where Person.name = Eats.name"
        computed = self._evaluate(sqlstring)
        self.assertEqual(len(computed), 20)

    def test_project_person_join_eats_join_serves(self):
        sqlstring = "select distinct Person.name, Serves.pizza from Person, Eats, Serves " \
                    "where Person.name = Eats.name and Eats.pizza = Serves.pizza"
        computed = self._evaluate(sqlstring)
        self.assertEqual(len(computed), 20)

    def test_project_name_of_person(self):
        sqlstring = "select distinct X.name from Person X"
        computed = self._evaluate(sqlstring)
        self.assertEqual(len(computed), 9)
        self.assertIn({"X.name": "Amy"}, [json.loads(tuple.split('\t')[1]) for tuple in computed])

    def test_mushroom_lovers(self):
        sqlstring = "select distinct Person.name, Serves.pizzeria from Person, Eats, Serves "\
                    "where Person.name = Eats.name and Eats.pizza = Serves.pizza " \
                    "and Eats.pizza = 'mushroom'"
        computed = self._evaluate(sqlstring)
        self.assertEqual(len(computed), 8)

    # NEW as of 19-MAY-2018
    def test_person_join_eats_join_serves_where(self):
        sqlstring = "select distinct * from Person, Eats, Serves " \
                    "where Person.name = Eats.name and Eats.pizza = Serves.pizza "\
                    "and Person.age = 16 and Serves.pizzeria = 'Little Ceasars'"
        computed = self._evaluate(sqlstring)
        self.assertEqual(len(computed), 2)

if __name__ == '__main__':
    unittest.main()
