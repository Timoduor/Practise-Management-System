from datetime import datetime, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from hub.models import Absence, Project, Sales, LeaveType, Customer
from core.models import User

class AbsenceModelTest(TestCase):
    def setUp(self):
        # Create the necessary user, customer, project, and sale objects
        self.user = User.objects.create_user(email="user@example.com", password="password123")
        self.customer = Customer.objects.create(
            customer_name="Test Customer",
            customer_email="customer@example.com"
        )
        self.project = Project.objects.create(
            project_name="Test Project",
            customer=self.customer,
            project_value=50000.00
        )
        self.sale = Sales.objects.create(
            sales_name="Test Sale",
            customer=self.customer,
            project_value=10000.00,
            expected_order_date=datetime.now().date()
        )
        self.leave_type = LeaveType.objects.create(
            name="Sick Leave",
            is_paid=True
        )

    def test_create_absence(self):
        absence = Absence.objects.create(
            user=self.user,
            absence_date=datetime.now().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=8)).time(),
            absence_description="Sick leave for the day",
            project=self.project,
            leave_type=self.leave_type
        )
        absence.full_clean()  # Validate fields
        self.assertIsNotNone(absence.pk)
        self.assertEqual(absence.duration.total_seconds(), 8 * 3600)

    def test_absence_with_sale_relation(self):
        absence = Absence(
            user=self.user,
            absence_date=datetime.now().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=8)).time(),
            absence_description="Attending a sales event",
            sale=self.sale,
            leave_type=self.leave_type
        )
        absence.full_clean()
        absence.save()
        self.assertIsNotNone(absence.pk)
        self.assertEqual(absence.sale, self.sale)

    def test_absence_invalid_project_and_sale(self):
        absence = Absence(
            user=self.user,
            absence_date=datetime.now().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=8)).time(),
            project=self.project,
            sale=self.sale,
            leave_type=self.leave_type
        )
        with self.assertRaises(ValidationError):
            absence.full_clean()

    def test_absence_missing_relations(self):
        absence = Absence(
            user=self.user,
            absence_date=datetime.now().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=8)).time(),
            absence_description="General leave"
        )
        with self.assertRaises(ValidationError):
            absence.full_clean()

    def test_absence_str_representation(self):
        absence = Absence.objects.create(
            user=self.user,
            absence_date=datetime.now().date(),
            start_time=datetime.now().time(),
            end_time=(datetime.now() + timedelta(hours=8)).time(),
            absence_description="Sick leave",
            project=self.project,
            leave_type=self.leave_type
        )
        self.assertEqual(str(absence), f"{self.user} - {self.leave_type} on {absence.absence_date}")
