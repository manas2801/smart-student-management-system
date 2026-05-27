from django.test import TestCase
from django.urls import reverse

from .models import Student


# STUDENT MODEL TEST

class StudentModelTest(TestCase):

    def setUp(self):

        self.student = Student.objects.create(

            name="Manas Mayank",
            email="mayank.manas.2801@gmail.com",
            course="BCA",
            phone="8709791448",
            address="Muzaffarpur, Bihar"
        )

    def test_student_creation(self):

        self.assertEqual(
            self.student.name,
            "Manas Mayank"
        )

        self.assertEqual(
            self.student.course,
            "BCA"
        )

        self.assertEqual(
            self.student.phone,
            "8709791448"
        )


# HOMEPAGE TEST

class HomePageTest(TestCase):

    def test_homepage_status_code(self):

        response = self.client.get('/')

        self.assertEqual(
            response.status_code,
            200
        )


# LOGIN PAGE TEST

class LoginPageTest(TestCase):

    def test_login_page_loads(self):

        response = self.client.get('/login/')

        self.assertEqual(
            response.status_code,
            200
        )


# STUDENT LIST PAGE TEST

class StudentPageTest(TestCase):

    def test_student_page_loads(self):

        response = self.client.get('/students/')

        self.assertIn(
            response.status_code,
            [200, 302]
        )