from django.db import models
from django.contrib.auth.models import User

import uuid

class Student(models.Model):
    student_id = models.CharField(
    max_length=10,
    unique=True,
    editable=False,
    null=True,
    blank=True
)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    course = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    photo = models.ImageField(
    upload_to='students/',
    blank=True,
    null=True
)

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = "STU" + str(uuid.uuid4().int)[:6]  # e.g. STU123456
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.student_id})"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ])

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"


class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    marks = models.IntegerField()

    def __str__(self):
        return f"{self.student.name} - {self.subject}"

class Assignment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)  # 🔥 NEW

    def __str__(self):
        return self.title


class Notice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    total_fee = models.IntegerField()
    paid_fee = models.IntegerField()
    due_fee = models.IntegerField()

    qr_code = models.ImageField(
    upload_to='qr_codes/',
    blank=True,
    null=True
)

    def __str__(self):
        return self.student.name


class Timetable(models.Model):
    day = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.day} - {self.subject}"
    
class AssignmentSubmission(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to='submissions/'
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f"{self.student.username} Submission"
    
import qrcode

from io import BytesIO

from django.core.files import File

from PIL import Image


class Donation(models.Model):

    STATUS_CHOICES = [

        ('Pending', 'Pending'),

        ('Completed', 'Completed'),

        ('Failed', 'Failed')

    ]

    name = models.CharField(max_length=100)

    upi_id = models.CharField(max_length=100)

    amount = models.IntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        upi_link = (
            f"upi://pay?"
            f"pa={self.upi_id}"
            f"&pn=SmartSMS"
            f"&am={self.amount}"
            f"&cu=INR"
        )

        qr = qrcode.QRCode(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=18,
            border=4
        )

        qr.add_data(upi_link)

        qr.make(fit=True)

        img = qr.make_image(
            fill_color="black",
            back_color="white"
        ).convert('RGB')

        img = img.resize((450, 450))

        buffer = BytesIO()

        img.save(
            buffer,
            format='PNG'
        )

        file_name = f"qr_{self.name}.png"

        self.qr_code.save(
            file_name,
            File(buffer),
            save=False
        )

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name
    
class FeePayment(models.Model):

    STATUS_CHOICES = [

        ('Pending', 'Pending'),

        ('Completed', 'Completed'),

        ('Failed', 'Failed')

    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    amount = models.IntegerField()

    upi_id = models.CharField(
        max_length=100
    )

    qr_code = models.ImageField(
        upload_to='fee_qr/',
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        upi_link = (
            f"upi://pay?"
            f"pa={self.upi_id}"
            f"&pn=SmartSMS Fees"
            f"&am={self.amount}"
            f"&cu=INR"
        )

        qr = qrcode.QRCode(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=18,
            border=4
        )

        qr.add_data(upi_link)

        qr.make(fit=True)

        img = qr.make_image(
            fill_color="black",
            back_color="white"
        ).convert('RGB')

        img = img.resize((450, 450))

        buffer = BytesIO()

        img.save(
            buffer,
            format='PNG'
        )

        file_name = f"fee_qr_{self.student.name}.png"

        self.qr_code.save(
            file_name,
            File(buffer),
            save=False
        )

        super().save(*args, **kwargs)

    def __str__(self):

        return self.student.name