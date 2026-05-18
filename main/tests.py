from django.test import TestCase

from .models import Student


class StudentModelTest(TestCase):

    def test_student_creation(self):

        student = Student.objects.create(

            name="Manas",
            email="mayank.manas.2801@gmail.com",
            course="BCA",
            phone="8709791448",
            address="Muzaffarpur, Bihar"
        )

        self.assertEqual(student.name, "Manas")


class HomePageTest(TestCase):

    def test_homepage_status_code(self):

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)