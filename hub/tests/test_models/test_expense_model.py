from datetime import datetime
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from hub.models import Expense, Project, Sales, Customer, Task, ProjectPhase
from core.models import User

class ExpenseModelTest(TestCase):
    def setUp(self):
        # Set up dependencies for Expense
        self.user = User.objects.create_user(email="user@example.com", password="password123")
        self.customer = Customer.objects.create(
            customer_name="Test Customer",
            customer_email="customer@example.com"
        )
        self.project = Project.objects.create(
            project_name="Test Project",
            customer=self.customer,
            project_value=Decimal("50000.00")
        )
        self.phase = ProjectPhase.objects.create(
            phase_name="Initial Phase",
            project=self.project
        )
        self.task = Task.objects.create(
            task_name="Development Task",
            project=self.project,
            phase=self.phase
        )
        self.sale = Sales.objects.create(
            sales_name="Test Sale",
            customer=self.customer,
            project_value=Decimal("10000.00"),
            expected_order_date=datetime.now().date()
        )

    def test_create_expense_with_project_task(self):
        expense = Expense.objects.create(
            user=self.user,
            customer=self.customer,
            project=self.project,
            phase=self.phase,
            task=self.task,
            date=datetime.now().date(),
            value=Decimal("100.00"),
            description="Project Task Expense"
        )
        expense.full_clean()  # Validate fields
        self.assertIsNotNone(expense.pk)
        self.assertEqual(expense.project, self.project)
        self.assertEqual(expense.task, self.task)
        self.assertEqual(expense.value, Decimal("100.00"))

    def test_create_expense_with_sale_task(self):
        expense = Expense.objects.create(
            user=self.user,
            customer=self.customer,
            sale=self.sale,
            date=datetime.now().date(),
            value=Decimal("200.00"),
            description="Sales Task Expense"
        )
        expense.full_clean()
        expense.save()
        self.assertIsNotNone(expense.pk)
        self.assertEqual(expense.sale, self.sale)
        self.assertEqual(expense.value, Decimal("200.00"))

    def test_expense_invalid_project_and_sale(self):
        expense = Expense(
            user=self.user,
            customer=self.customer,
            project=self.project,
            sale=self.sale,
            date=datetime.now().date(),
            value=Decimal("150.00"),
            description="Invalid Expense with Project and Sale"
        )
        with self.assertRaises(ValidationError):
            expense.full_clean()

    def test_expense_without_required_relations(self):
        expense = Expense(
            user=self.user,
            date=datetime.now().date(),
            value=Decimal("50.00"),
            description="General Expense"
        )
        with self.assertRaises(ValidationError):
            expense.full_clean()

    def test_expense_str_representation(self):
        expense = Expense.objects.create(
            user=self.user,
            customer=self.customer,
            project=self.project,
            date=datetime.now().date(),
            value=Decimal("120.00"),
            description="String Representation Test"
        )
        self.assertEqual(str(expense), f"Expense {expense.expense_id} - {expense.value} on {self.project}")
