import unittest

from prosto.Prosto import *

class TableProductTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_product(self):
        sch = Prosto("My Prosto")

        t1 = sch.populate(
            table_name="Table 1", attributes=["A"],
            func="lambda **m: pd.DataFrame({'A': [1.0, 2.0, 3.0]})", tables=[]
        )

        t2 = sch.populate(
            table_name="Table 2", attributes=["B"],
            func="lambda **m: pd.DataFrame({'B': ['x', 'y', 'z']})", tables=[]
        )

        product = sch.product(
            table_name="Product", attributes=["t1", "t2"],
            tables=["Table 1", "Table 2"]
        )

        t1.evaluate()
        t2.evaluate()
        product.evaluate()

        self.assertEqual(len(product.get_data().columns), 2)
        self.assertEqual(len(product.get_data()), 9)

        self.assertEqual(product.get_data().columns.to_list(), ["t1", "t2"])


if __name__ == '__main__':
    unittest.main()
