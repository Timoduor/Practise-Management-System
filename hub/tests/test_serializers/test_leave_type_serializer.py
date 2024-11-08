# hub/tests/test_serializers/test_leave_type_serializer.py
from django.test import TestCase
from rest_framework import serializers  # Importing serializers to fix NameError
from hub.serializers import LeaveTypeSerializer
from hub.models import LeaveType

class LeaveTypeSerializerTest(TestCase):
    
    def setUp(self):
        self.valid_data = {
            "name": "Sick Leave",
            "description": "Paid leave for medical reasons.",
            "is_paid": True,
        }
        self.invalid_data = {
            "name": "",  # Invalid because it's required
            "description": "No pay leave.",
            "is_paid": False,
        }

    def test_valid_leave_type_creation(self):
        """Test creating a LeaveType with valid data."""
        serializer = LeaveTypeSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        leave_type = serializer.save()
        
        self.assertEqual(leave_type.name, self.valid_data["name"])
        self.assertEqual(leave_type.description, self.valid_data["description"])
        self.assertEqual(leave_type.is_paid, self.valid_data["is_paid"])

    def test_missing_required_name_field(self):
        """Test that the serializer fails when the required 'name' field is missing."""
        serializer = LeaveTypeSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_partial_update_leave_type(self):
        """Test updating a LeaveType with partial data."""
        leave_type = LeaveType.objects.create(**self.valid_data)
        update_data = {"description": "Updated description for sick leave"}
        
        serializer = LeaveTypeSerializer(leave_type, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_leave_type = serializer.save()
        
        self.assertEqual(updated_leave_type.description, update_data["description"])
        self.assertEqual(updated_leave_type.name, self.valid_data["name"])  # Name should remain unchanged
        self.assertEqual(updated_leave_type.is_paid, self.valid_data["is_paid"])  # is_paid should remain unchanged

    def test_invalid_is_paid_field(self):
        """Test the serializer with invalid type for is_paid field."""
        invalid_data = self.valid_data.copy()
        invalid_data["is_paid"] = "not_boolean"  # Invalid data type for is_paid field

        serializer = LeaveTypeSerializer(data=invalid_data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)
