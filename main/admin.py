from django.contrib import admin
from .models import FeePayment, Student, Attendance, Mark, Assignment, Notice, Fee, Timetable

from .models import AssignmentSubmission
from .models import Donation

admin.site.register(AssignmentSubmission)
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Mark)
admin.site.register(Assignment)
admin.site.register(Notice)
admin.site.register(Fee)
admin.site.register(Timetable)

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'amount',
        'status',
        'created_at'
    )

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'amount',
        'status',
        'created_at'
    )