import radb
import radb.ast   # Some environments require this import.
import radb.parse # Some environments require this import.
import sql2ra
import sqlparse
import unittest

'''
Public unit tests for miniHive milestone 1.

These tests check the canonical translation of simple SQL statements
into the relational algebra using the operators selection, projection,
renaming and cross-product.

08-APR-2018: First release.
02-MAY-2018: Adapted imports because some students reported problems.        
12-MAR-2019: Removed some tests that were stricter than the succeeding milestones.
'''
class TestSQL2RA(unittest.TestCase):
    
    def _check(self, sqlstring, rastring):
        stmt = sqlparse.parse(sqlstring)[0]
        ra = sql2ra.translate(stmt)
        expected = radb.parse.one_statement_from_string(rastring)        
        self.assertEqual(str(ra), str(expected))

    def test_select_star_from_person(self):
        self._check("select distinct * from Person", "Person;")

    def test_select_star_from_person_where_age(self):
        self._check("select distinct * from Person where age=16", "\select_{age=16}(Person);")
    
    def test_select_star_fromPerson_where_age_and_gender(self):
        # Note: Strings within the SQL statement should be delimited with ', not ",
        # to avoid parsing errors.
        self._check("select distinct * from Person where age=16 and gender='f'", 
                    "\select_{(age = 16) and (gender = 'f')} Person;")
    
    def test_select_name_from_person(self):
        self._check("select distinct name from Person", "\project_{name}(Person);")

    def test_select_person_name_from_person(self):
        self._check("select distinct Person.name from Person", "\project_{Person.name}(Person);")

    def test_select_name_age_from_person(self):
        self._check("select distinct name, age from Person", "\project_{name, age}(Person);")

    def test_select_gender_from_Person_where_age(self):
        self._check("select distinct gender from Person where age = 16",
                    "\project_{gender}(\select_{age=16}(Person));")

    def test_select_star_from_person_eats(self):
        self._check("select distinct * from Person, Eats", "Person \cross Eats;")

    def test_select_star_from_person_eats_serves(self):
        self._check("select distinct * from Person, Eats, Serves", "(Person \cross Eats) \cross Serves;")

    def test_select_star_from_person_join_eats(self):
        self._check("select distinct * from Person, Eats where Person.name = Eats.name",
                    "\select_{Person.name = Eats.name}(Person \cross Eats);")

    def test_select_name_from_person_join_eats(self):
        self._check("select distinct Person.name from Person, Eats where Person.name = Eats.name",
                    "\project_{Person.name}(\select_{Person.name = Eats.name}(Person \cross Eats));")

    def test_select_name_pizzeria_from_person_join_eats_join_serves(self):
        self._check("""select distinct Person.name, pizzeria from Person, Eats, Serves
                       where Person.name = Eats.name and Eats.pizza = Serves.pizza""",
                    """\project_{Person.name, pizzeria}(\select_{Person.name = Eats.name
                       and Eats.pizza = Serves.pizza}((Person \cross Eats) \cross Serves));""")

    def test_select_X_name_from_person_X(self):
        # Note: Need to escape "\rename" by writing "\\rename"
        self._check("select distinct X.name from Person X", "\project_{X.name}(\\rename_{X: *}(Person));")

    def test_select_names_from_eats_A_join_eats_B(self):
        # Note: Do not use names like "e1" or "e2" in the from-clause,
        # this is misinterpreted as floats.
        self._check("select distinct A.name, B.name from Eats A, Eats B where A.pizza = B.pizza",
                    """\project_{A.name, B.name}(\select_{A.pizza = B.pizza}
                       (\\rename_{A: *} Eats \cross \\rename_{B: *} Eats));""")   

if __name__ == '__main__':
    unittest.main()
