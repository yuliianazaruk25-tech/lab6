
import subprocess
import sys
import unittest

from main import (
    Employee,
    HourlyEmployee,
    FixedEmployee,
    FOPEmployee,
    SelfEmployedEmployee,
    generate_employees,
    sort_employees,
    filter_fop
)


class TestEmployees(unittest.TestCase):

    def test_abstract_class(self):
        with self.assertRaises(TypeError):
            Employee("1234567890", "Test")

    def test_hourly_salary(self):
        e = HourlyEmployee("1", "Ivanenko", 100)
        self.assertAlmostEqual(e.calculate_salary(), 16640)

    def test_hourly_taxes(self):
        e = HourlyEmployee("1", "Ivanenko", 100)
        self.assertAlmostEqual(e.calculate_taxes(), 3244.8)

    def test_fixed_salary(self):
        e = FixedEmployee("2", "Petrenko", 30000)
        self.assertEqual(e.calculate_salary(), 30000)
        self.assertAlmostEqual(e.calculate_taxes(), 5850)

    def test_fop_salary(self):
        e = FOPEmployee("3", "Koval", 100, 3)
        self.assertAlmostEqual(e.calculate_salary(), 18304)

    def test_fop_taxes(self):
        e = FOPEmployee("3", "Koval", 100, 3)
        self.assertAlmostEqual(e.calculate_taxes(), 2675.2)

    def test_self_employed(self):
        e = SelfEmployedEmployee("4", "Bondar", 10, 1000)
        self.assertEqual(e.calculate_salary(), 10000)
        self.assertAlmostEqual(e.calculate_taxes(), 3710)

    def test_generation(self):
        employees = generate_employees(20)
        self.assertEqual(len(employees), 20)
        self.assertEqual(len({e.tax_id for e in employees}), 20)

    def test_sorting(self):
        employees = [
            FixedEmployee("1", "Z", 20000),
            FixedEmployee("2", "B", 30000),
            FixedEmployee("3", "A", 30000)
        ]
        result = sort_employees(employees)
        self.assertEqual(
            [e.surname for e in result],
            ["A", "B", "Z"]
        )

    def test_filter_fop(self):
        employees = [
            FOPEmployee("1", "A", 100, 2),
            FOPEmployee("2", "B", 200, 3),
            FixedEmployee("3", "C", 30000)
        ]
        result = filter_fop(employees, group=3)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].surname, "B")

    def test_filter_income_and_tax(self):
        employees = [
            FOPEmployee("1", "A", 100, 2),
            FOPEmployee("2", "B", 200, 3)
        ]
        result = filter_fop(
            employees, min_income=30000, min_tax=3500
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].surname, "B")

    def test_cli_list(self):
        result = subprocess.run(
            [sys.executable, "main.py", "--count", "5", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        self.assertIn("Salary", result.stdout)
        self.assertEqual(len(result.stdout.splitlines()), 7)

    def test_cli_fop(self):
        result = subprocess.run(
            [sys.executable, "main.py", "--count", "50",
             "fop", "--group", "3"],
            capture_output=True,
            text=True,
            check=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("FixedEmployee", result.stdout)


if __name__ == "__main__":
    unittest.main()
