
import argparse
import random
from abc import ABC, abstractmethod
from faker import Faker


PIT_RATE = 0.18
MILITARY_RATE = 0.015
SINGLE_TAX_RATE = 0.05
SOCIAL_CONTRIBUTION = 1760


class Employee(ABC):
    def __init__(self, tax_id, surname):
        self.tax_id = tax_id
        self.surname = surname

    @abstractmethod
    def calculate_salary(self):
        pass

    @abstractmethod
    def calculate_taxes(self):
        pass


class HourlyEmployee(Employee):
    def __init__(self, tax_id, surname, hourly_rate):
        super().__init__(tax_id, surname)
        self.hourly_rate = hourly_rate

    def calculate_salary(self):
        return 20.8 * 8 * self.hourly_rate

    def calculate_taxes(self):
        return self.calculate_salary() * (PIT_RATE + MILITARY_RATE)


class FixedEmployee(Employee):
    def __init__(self, tax_id, surname, monthly_salary):
        super().__init__(tax_id, surname)
        self.monthly_salary = monthly_salary

    def calculate_salary(self):
        return self.monthly_salary

    def calculate_taxes(self):
        return self.calculate_salary() * (PIT_RATE + MILITARY_RATE)


class FOPEmployee(Employee):
    def __init__(self, tax_id, surname, hourly_rate, group=3):
        super().__init__(tax_id, surname)
        self.hourly_rate = hourly_rate
        self.group = group

    def calculate_salary(self):
        return 20.8 * 8 * self.hourly_rate * 1.10

    def calculate_taxes(self):
        return (
            self.calculate_salary() * SINGLE_TAX_RATE
            + SOCIAL_CONTRIBUTION
        )


class SelfEmployedEmployee(Employee):
    def __init__(self, tax_id, surname, price_per_line, lines):
        super().__init__(tax_id, surname)
        self.price_per_line = price_per_line
        self.lines = lines

    def calculate_salary(self):
        return self.price_per_line * self.lines

    def calculate_taxes(self):
        return (
            self.calculate_salary() * (PIT_RATE + MILITARY_RATE)
            + SOCIAL_CONTRIBUTION
        )


def generate_employees(count=20, seed=42):
    if count < 0:
        raise ValueError("Employee count cannot be negative")

    fake = Faker("uk_UA")
    fake.seed_instance(seed)
    rng = random.Random(seed)

    employees = []

    for i in range(count):
        tax_id = f"{i + 1:010d}"
        surname = fake.last_name()
        employee_type = rng.randint(1, 4)

        if employee_type == 1:
            employee = HourlyEmployee(
                tax_id, surname, rng.randint(100, 500)
            )

        elif employee_type == 2:
            employee = FixedEmployee(
                tax_id, surname, rng.randint(20000, 80000)
            )

        elif employee_type == 3:
            employee = FOPEmployee(
                tax_id,
                surname,
                rng.randint(100, 500),
                rng.choice([2, 3])
            )

        else:
            employee = SelfEmployedEmployee(
                tax_id,
                surname,
                rng.randint(5, 30),
                rng.randint(500, 3000)
            )

        employees.append(employee)

    return employees


def sort_employees(employees):
    return sorted(
        employees,
        key=lambda e: (-e.calculate_salary(), e.surname.casefold())
    )


def filter_fop(employees, group=None, min_income=None,
               max_income=None, min_tax=None, max_tax=None):
    result = [e for e in employees if isinstance(e, FOPEmployee)]

    if group is not None:
        result = [e for e in result if e.group == group]

    if min_income is not None:
        result = [
            e for e in result if e.calculate_salary() >= min_income
        ]

    if max_income is not None:
        result = [
            e for e in result if e.calculate_salary() <= max_income
        ]

    if min_tax is not None:
        result = [
            e for e in result if e.calculate_taxes() >= min_tax
        ]

    if max_tax is not None:
        result = [
            e for e in result if e.calculate_taxes() <= max_tax
        ]

    return result


def print_employees(employees):
    print(
        f"{'Tax ID':<12} {'Surname':<20} "
        f"{'Salary':>12} {'Taxes':>12} {'Type':<15}"
    )
    print("-" * 78)

    for e in employees:
        print(
            f"{e.tax_id:<12} "
            f"{e.surname:<20} "
            f"{e.calculate_salary():>12.2f} "
            f"{e.calculate_taxes():>12.2f} "
            f"{type(e).__name__:<15}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="IT company employee management"
    )

    parser.add_argument(
        "--count", type=int, default=20,
        help="Number of employees"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random generation seed"
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List all employees")

    fop_parser = subparsers.add_parser(
        "fop", help="Filter FOP employees"
    )
    fop_parser.add_argument("--group", type=int, choices=[2, 3])
    fop_parser.add_argument("--min-income", type=float)
    fop_parser.add_argument("--max-income", type=float)
    fop_parser.add_argument("--min-tax", type=float)
    fop_parser.add_argument("--max-tax", type=float)

    args = parser.parse_args()

    if args.count < 0:
        parser.error("--count must be non-negative")

    employees = generate_employees(args.count, args.seed)

    if args.command == "fop":
        employees = filter_fop(
            employees,
            group=args.group,
            min_income=args.min_income,
            max_income=args.max_income,
            min_tax=args.min_tax,
            max_tax=args.max_tax
        )

    employees = sort_employees(employees)
    print_employees(employees)


if __name__ == "__main__":
    main()
