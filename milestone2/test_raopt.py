import radb
import raopt
import unittest

'''
Public unit tests for miniHive milestone 2.

Tests check several rewriting rules for the logical optimization
of relational algebra expressions.

Tests assume that all relational algebra queries 
use projection, selection, the cross product
and the renaming operator only.

Last modified 09-APR-2018.

09-MAY-2019 Updated comment.
'''

'''
Tests that selections are broken up correctly.
'''
class TestRuleBreakUpSelections(unittest.TestCase):

    def _check(self, input, expected):
        computed_expr = raopt.rule_break_up_selections(radb.parse.one_statement_from_string(input))
        expected_expr = radb.parse.one_statement_from_string(expected)        
        self.assertEqual(str(computed_expr), str(expected_expr))

    def test_break_selections_select_gender_age_person(self):
        self._check("\select_{Person.gender = 'f' and Person.age = 16}(Person);",
                    "\select_{Person.gender = 'f'} (\select_{Person.age = 16} Person);")

    def test_break_selections_project_select_gender_age_person(self):
        self._check("\project_{name}(\select_{gender='f' and age=16}(Person));",
                    "\project_{name}(\select_{gender = 'f'} (\select_{age = 16} Person));")

    def test_break_selections_select_gender_age_person_cross_eats(self):        
        self._check("\select_{Person.gender='f' and Person.age=16}(Person) \cross Eats;",
                    "\select_{Person.gender = 'f'} (\select_{Person.age = 16} Person) \cross Eats;")

    def test_select_rename_eats(self):
        self._check("\select_{E.pizza = 'mushroom' and E.price < 10} \\rename_{E: *}(Eats);",
                    "\select_{E.pizza = 'mushroom'} \select_{E.price < 10} \\rename_{E: *}(Eats);")


'''
Tests selection pushdown.
Assumes that conjunctions in selections have been broken up.
'''
class TestRulePushDownSelections(unittest.TestCase):

    def _check(self, input, expected):
        # The data dictionary records the relational schema.
        dd = {}
        dd["Person"] = {"name": "string", "age": "integer", "gender": "string"}
        dd["Eats"] = {"name": "string", "pizza": "string"}
        dd["Serves"] = {"pizzeria": "string", "pizza": "string", "price": "integer"}

        computed_expr = raopt.rule_push_down_selections(radb.parse.one_statement_from_string(input), dd)
        expected_expr = radb.parse.one_statement_from_string(expected)        
        self.assertEqual(str(computed_expr), str(expected_expr))

    def test_select_select_person(self):
        self._check("\select_{gender = 'f'} (\select_{age = 16} Person);",
                    "\select_{gender = 'f'} (\select_{age = 16} Person);")

    def test_select_person(self):
        self._check("\select_{'f' = gender} Person;",
                    "\select_{'f' = gender} Person;")

    def test_project_select_person(self):
        self._check("\project_{name}(\select_{gender = 'm'} Person);",
                    "\project_{name}(\select_{gender = 'm'} Person);")

    def test_select_gender_person_cross_eats(self):
        self._check("\select_{gender = 'm'} (Person \cross Eats);",
                    "(\select_{gender = 'm'} Person) \cross Eats;")

    def test_select_pizza_person_cross_eats(self):
        self._check("\select_{pizza = 'mushroom'} (Person \cross Eats);",
                    "Person \cross (\select_{pizza = 'mushroom'} Eats);")   

    def test_select_pizza_select_gender_person_cross_eats(self):
        self._check("\select_{pizza = 'mushroom'} \select_{gender = 'm'} (Person \cross Eats);",
                    "(\select_{gender = 'm'} Person) \cross (\select_{pizza = 'mushroom'} Eats);")       

    def test_select_person_cross_eats(self):
        self._check("\select_{Person.name = Eats.name} (Person \cross Eats);",
                    "\select_{Person.name = Eats.name} (Person \cross Eats);")

    def test_select_select_person_cross_eats(self):
        self._check("\select_{age = 16} \select_{Person.name = Eats.name} (Person \cross Eats);",
                    "\select_{Person.name = Eats.name} (\select_{age = 16}(Person) \cross Eats);")        

    def test_select_age_person_cross_eats_cross_serves(self):
        self._check("\select_{age = 16} ((Person \cross Eats) \cross Serves);",
                    "(\select_{age = 16}(Person) \cross Eats \cross Serves);")        

    def test_select_price_person_cross_eats_cross_serves(self):
        self._check("\select_{price < 10} ((Person \cross Eats) \cross Serves);",
                    "((Person \cross Eats) \cross \select_{price < 10}(Serves));")  

    def test_select_select_3cross(self):
        self._check("""\select_{Eats.pizza = Serves.pizza} \select_{Person.name = Eats.name}
                       ((Person \cross Eats) \cross Serves);""",
                    """\select_{Eats.pizza = Serves.pizza}( \select_{Person.name = Eats.name}
                       (Person \cross Eats) \cross Serves );""") 
        
    def test_select_rename_eats(self):
        self._check("\select_{pizza = 'mushroom'} \\rename_{E: *}(Eats);",
                    "\select_{pizza = 'mushroom'} \\rename_{E: *}(Eats);")

    def test_select_rename_eats_prefix_notation(self):
        self._check("\select_{E.pizza = 'mushroom'} \\rename_{E: *}(Eats);",
                    "\select_{E.pizza = 'mushroom'} \\rename_{E: *}(Eats);")

    def test_select_select_cross_2rename(self):
        self._check("""\select_{Eats1.pizza = Eats2.pizza} \select_{Eats1.name = 'Amy'} (\\rename_{Eats1: *}(Eats)
                       \cross \\rename_{Eats2: *}(Eats));""",
                    """\select_{Eats1.pizza = Eats2.pizza} ((\select_{Eats1.name = 'Amy'} \\rename_{Eats1: *}(Eats))
                       \cross \\rename_{Eats2: *}(Eats));""")

'''
Tests that nested selections are properly merged.
'''
class TestMergeSelections(unittest.TestCase):
    
    def _check(self, input, expected):
        computed_expr = raopt.rule_merge_selections(radb.parse.one_statement_from_string(input))
        expected_expr = radb.parse.one_statement_from_string(expected)        
        self.assertEqual(str(computed_expr), str(expected_expr))

    def test_project_select_person(self):
        self._check("\project_{name} \select_{'f' = gender} Person;",
                    "\project_{name} \select_{'f' = gender} Person;")

    def test_select_select_person(self):
        self._check("\select_{name = 'Amy'} \select_{gender = 'f'} Person;",
                    "\select_{name = 'Amy' and gender = 'f'} Person;")

    def test_select_double_join_person(self):
        self._check("\select_{Person.name = Eats.name} \select_{Person.name = Eats.pizza} (Person \cross Eats);",
                    "\select_{Person.name = Eats.name and Person.name = Eats.pizza} (Person \cross Eats);")

    def test_cross_select_select(self):
        self._check("Pizzeria \cross (\select_{pizza = 'mushroom'} \select_{price = 10} Serves);",
                    "Pizzeria \cross (\select_{pizza = 'mushroom' and price = 10} Serves);")


'''
Tests the introduction of joins.
Assumes that all selections have been pushed down as far as possible.
'''
class TestIntroduceJoins(unittest.TestCase):

    def _check(self, input, expected):
        computed_expr = raopt.rule_introduce_joins(radb.parse.one_statement_from_string(input))
        expected_expr = radb.parse.one_statement_from_string(expected)        
        self.assertEqual(str(computed_expr), str(expected_expr))

    def test_project_select_person(self):
        self._check("\project_{name} \select_{'f' = gender} Person;",
                    "\project_{name} \select_{'f' = gender} Person;")

    def test_select_person_cross_eats(self):
        self._check("\select_{Person.name = Eats.name} (Person \cross Eats);",
                    "Person \join_{Person.name = Eats.name} Eats;")

    def test_select_person_cross_eats_with_rename(self):
        self._check("\select_{P.name = Eats.name} ((\\rename_{P: *} Person) \cross Eats);",
                    "(\\rename_{P: *} Person) \join_{P.name = Eats.name} Eats;")

    def test_2_cross(self):
        self._check("""\select_{Eats.pizza = Serves.pizza}((\select_{Person.name = Eats.name}
                       (Person \cross Eats)) \cross Serves);""",
                    """(Person \join_{Person.name = Eats.name} Eats) \join_{Eats.pizza =
                       Serves.pizza} Serves;""")


'''
Tests all rules in combination.
'''
class TestAllSteps(unittest.TestCase):

    def _check(self, input, expected):
        dd = {}
        dd["Person"] = {"name": "string", "age": "integer", "gender": "string"}
        dd["Eats"] = {"name": "string", "pizza": "string"}
        dd["Serves"] = {"pizzeria": "string", "pizza": "string", "price": "integer"}
        
        ra0 = radb.parse.one_statement_from_string(input)
        ra1 = raopt.rule_break_up_selections(ra0)
        ra2 = raopt.rule_push_down_selections(ra1, dd)
        ra3 = raopt.rule_merge_selections(ra2)
        ra4 = raopt.rule_introduce_joins(ra3)

        computed_expr = ra4
        expected_expr = radb.parse.one_statement_from_string(expected)        
        self.assertEqual(str(computed_expr), str(expected_expr))

    def test_project_select_person(self):
        self._check("\project_{name}(\select_{gender='f' and age=16} Person);",
                    "\project_{name}(\select_{gender = 'f' and age = 16} Person);")

    def test_project_join(self):
        self._check("\select_{Person.name = Eats.name and Person.name = Eats.pizza} (Person \cross Eats);",
                    "Person \join_{Person.name = Eats.name and Person.name = Eats.pizza} Eats;")

    def test_cross_cross(self):
        self._check("""\project_{Person.name} \select_{Eats.pizza = Serves.pizza and Person.name = Eats.name}
                       ((Person \cross Eats) \cross Serves);""",
                    """\project_{Person.name} ((Person \join_{Person.name = Eats.name} Eats)
                       \join_{Eats.pizza = Serves.pizza} Serves);""")
    
    def test_renamings(self):
        self._check("""\project_{P.name, E.pizza} (\select_{P.name = E.name}
                       ((\\rename_{P: *} Person) \cross (\\rename_{E: *} Eats)));""",
                    """\project_{P.name, E.pizza} ((\\rename_{P: *} Person) \join_{P.name = E.name}
                       (\\rename_{E: *} Eats));""")


if __name__ == '__main__':
    unittest.main()

