
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Avg
from django.core.mail import send_mail
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

import qrcode

from io import BytesIO

from django.core.files import File

from .models import (
    FeePayment,
    Donation,
    Student,
    Attendance,
    Mark,
    Assignment,
    Notice,
    Fee,
    Timetable,
    AssignmentSubmission,
)


# =====================================
# HELPER FUNCTION
# =====================================

def is_student(user):

    return user.groups.filter(
        name='Student'
    ).exists()


# =====================================
# HOME
# =====================================

def home(request):

    notices = Notice.objects.order_by(
        '-created_at'
    )[:3]

    return render(
        request,
        'home.html',
        {'notices': notices}
    )


def about(request):

    return render(request, 'about.html')


def contact(request):

    if request.method == "POST":

        name = request.POST.get('name')

        messages.success(
            request,
            f"Thank you {name}, your message has been received."
        )

    return render(request, 'contact.html')


# =====================================
# LOGIN
# =====================================

def login_page(request):

    if request.method == "POST":

        username = request.POST.get('username')

        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            messages.success(
                request,
                "Login Successful"
            )

            return redirect('/dashboard/')

        else:

            messages.error(
                request,
                "Invalid username or password"
            )

    return render(request, 'login.html')


# =====================================
# REGISTER
# =====================================

def register(request):

    if request.method == "POST":

        username = request.POST.get('username')

        email = request.POST.get('email')

        password = request.POST.get('password')

        password2 = request.POST.get('password2')

        role_key = request.POST.get('role_key')

        if password != password2:

            messages.error(
                request,
                "Passwords do not match"
            )

            return redirect('register')

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists"
            )

            return redirect('register')

        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already exists"
            )

            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        if role_key == "student123":

            group, created = Group.objects.get_or_create(
                name='Student'
            )

            user.groups.add(group)

        elif role_key == "teacher123":

            group, created = Group.objects.get_or_create(
                name='Teacher'
            )

            user.groups.add(group)

            user.is_staff = True

        elif role_key == "admin123":

            user.is_staff = True

            user.is_superuser = True

        else:

            user.delete()

            messages.error(
                request,
                "Invalid Role Key"
            )

            return redirect('register')

        user.save()

        send_mail(

    'Welcome to SmartSMS',

    'Your account has been created successfully.',

    'admin@smartsms.com',

    [email],

    fail_silently=True

)

        messages.success(
            request,
            "Registration Successful"
        )

        return redirect('login')

    return render(request, 'register.html')


# =====================================
# DASHBOARD
# =====================================

@login_required(login_url='/login/')
def dashboard(request):

    recent_students = Student.objects.order_by('-id')[:5]

    recent_notices = Notice.objects.order_by('-id')[:5]

    notices_count = Notice.objects.count()

    context = {

        'total_students': Student.objects.count(),

        'total_attendance': Attendance.objects.count(),

        'total_marks': Mark.objects.count(),

        'total_assignments': Assignment.objects.count(),

         'total_donations': Donation.objects.count(),

        'total_fee_payments': FeePayment.objects.count(),   

        'students': recent_students,

        'notices': recent_notices,

        'notices_count': notices_count,

        'top_students': (
            Student.objects
            .annotate(avg_marks=Avg('mark__marks'))
            .order_by('-avg_marks')[:5]
        ),

        'present_count': Attendance.objects.filter(
            status='Present'
        ).count(),

        'absent_count': Attendance.objects.filter(
            status='Absent'
        ).count(),

        'python_marks': Mark.objects.filter(
            subject__iexact='Python'
        ).count(),

        'dbms_marks': Mark.objects.filter(
            subject__iexact='DBMS'
        ).count(),

        'java_marks': Mark.objects.filter(
            subject__iexact='Java'
        ).count(),

        'other_marks': Mark.objects.exclude(
            subject__iexact='Python'
        ).exclude(
            subject__iexact='DBMS'
        ).exclude(
            subject__iexact='Java'
        ).count(),
    }

    return render(
        request,
        'dashboard.html',
        context
    )


# =====================================
# PROFILE
# =====================================

@login_required(login_url='/login/')
def profile(request):

    role = "User"

    if request.user.is_superuser:

        role = "Admin"

    elif request.user.groups.filter(name='Teacher').exists():

        role = "Teacher"

    elif request.user.groups.filter(name='Student').exists():

        role = "Student"

    return render(
        request,
        'profile.html',
        {'role': role}
    )


# =====================================
# STUDENTS
# =====================================

@login_required(login_url='/login/')
def students(request):

    query = request.GET.get('q')

    if query:

        student_list = Student.objects.filter(
            name__icontains=query
        ) | Student.objects.filter(
            student_id__icontains=query
        )

    else:

        student_list = Student.objects.all()

    return render(request, 'students.html', {

        'students': student_list,

        'query': query

    })


@login_required(login_url='/login/')
def student_detail(request, id):

    student = get_object_or_404(
        Student,
        id=id
    )

    attendance_count = Attendance.objects.filter(
        student=student,
        status="Present"
    ).count()

    total_attendance = Attendance.objects.filter(
        student=student
    ).count()

    marks = Mark.objects.filter(student=student)

    average_marks = 0

    if marks.exists():

        total = sum(mark.marks for mark in marks)

        average_marks = total / marks.count()

    context = {

        'student': student,

        'attendance_count': attendance_count,

        'total_attendance': total_attendance,

        'average_marks': round(average_marks, 1),

        'marks': marks,
    }

    return render(
        request,
        'student_detail.html',
        context
    )

@login_required(login_url='/login/')
def add_student(request):

    if is_student(request.user):
        return HttpResponseForbidden(
            "Students cannot add students."
        )

    if request.method == "POST":

        try:

            name = request.POST.get('name')
            email = request.POST.get('email')
            course = request.POST.get('course')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            photo = request.FILES.get('photo')

            username = request.POST.get('username')
            password = request.POST.get('password')

            # CHECK EXISTING USERNAME
            if User.objects.filter(username=username).exists():

                messages.error(
                    request,
                    "Username already exists"
                )

                return redirect('/add-student/')

            # CREATE LOGIN USER
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            # STUDENT GROUP
            student_group, created = Group.objects.get_or_create(
                name='Student'
            )

            user.groups.add(student_group)

            # CREATE STUDENT
            Student.objects.create(
                name=name,
                email=email,
                course=course,
                phone=phone,
                address=address,
                photo=photo
            )

            messages.success(
                request,
                "Student Added Successfully"
            )

            return redirect('/students/')

        except Exception as e:

            return HttpResponse(f"ERROR: {e}")

    return render(request, 'add_student.html')

@login_required(login_url='/login/')
def edit_student(request, id):

    if is_student(request.user):

        return HttpResponseForbidden(
            "Students cannot edit student records."
        )

    student = get_object_or_404(
        Student,
        id=id
    )

    if request.method == "POST":

        student.name = request.POST.get('name')

        student.email = request.POST.get('email')

        student.course = request.POST.get('course')

        student.phone = request.POST.get('phone')

        student.address = request.POST.get('address')

        if request.FILES.get('photo'):

            student.photo = request.FILES.get('photo')

        student.save()

        messages.success(
            request,
            "Student Updated Successfully"
        )

        return redirect('/students/')

    return render(
        request,
        'edit_student.html',
        {'student': student}
    )


@login_required(login_url='/login/')
def delete_student(request, id):

    if is_student(request.user):

        return HttpResponseForbidden(
            "Students cannot delete student records."
        )

    get_object_or_404(
        Student,
        id=id
    ).delete()

    messages.success(
        request,
        "Deleted Successfully"
    )

    return redirect('/students/')


# =====================================
# ATTENDANCE
# =====================================

@login_required(login_url='/login/')
def attendance(request):

    if request.method == "POST":

        if is_student(request.user):

            return HttpResponseForbidden(
                "Students cannot add attendance."
            )

        Attendance.objects.create(
            student_id=request.POST.get('student'),
            date=request.POST.get('date'),
            status=request.POST.get('status')
        )

        messages.success(
            request,
            "Attendance Added Successfully"
        )

        return redirect('/attendance/')

    return render(request, 'attendance.html', {

        'records': Attendance.objects.all(),

        'students': Student.objects.all()

    })


@login_required(login_url='/login/')
def delete_attendance(request, id):

    if is_student(request.user):

        return HttpResponseForbidden(
            "Students cannot delete attendance."
        )

    get_object_or_404(
        Attendance,
        id=id
    ).delete()

    messages.success(request, "Deleted")

    return redirect('/attendance/')


# =====================================
# MARKS
# =====================================

@login_required(login_url='/login/')
def marks(request):

    if request.method == "POST":

        if is_student(request.user):

            return HttpResponseForbidden(
                "Students cannot add marks."
            )

        Mark.objects.create(
            student_id=request.POST.get('student'),
            subject=request.POST.get('subject'),
            marks=request.POST.get('marks')
        )

        messages.success(
            request,
            "Marks Added Successfully"
        )

        return redirect('/marks/')

    return render(request, 'marks.html', {

        'records': Mark.objects.all(),

        'students': Student.objects.all()

    })


@login_required(login_url='/login/')
def delete_mark(request, id):

    if is_student(request.user):

        return HttpResponseForbidden(
            "Students cannot delete marks."
        )

    get_object_or_404(
        Mark,
        id=id
    ).delete()

    messages.success(request, "Deleted")

    return redirect('/marks/')


# =====================================
# ASSIGNMENTS
# =====================================
@login_required
def assignments(request):

    assignments = Assignment.objects.all()

    submissions = AssignmentSubmission.objects.filter(
        student=request.user
    )

    # STUDENT UPLOAD
    if request.user.groups.filter(name="Student").exists():

        if request.method == "POST":

            assignment_id = request.POST.get("assignment_id")

            file = request.FILES.get("submission_file")

            assignment = Assignment.objects.get(id=assignment_id)

            AssignmentSubmission.objects.create(
                assignment=assignment,
                student=request.user,
                file=file
            )

            messages.success(
                request,
                "Assignment submitted successfully!"
            )

            return redirect("assignments")

        return render(
            request,
            "assignments.html",
            {
                "assignments": assignments,
                "submissions": submissions
            }
        )

    # TEACHER / ADMIN
    else:

        if request.method == "POST":

            title = request.POST.get("title")

            description = request.POST.get("description")

            due_date = request.POST.get("due_date")

            file = request.FILES.get("file")

            Assignment.objects.create(
                title=title,
                description=description,
                due_date=due_date,
                file=file
            )

            messages.success(
                request,
                "Assignment added successfully!"
            )

            return redirect("assignments")

        all_submissions = AssignmentSubmission.objects.all()

        return render(
            request,
            "assignments.html",
            {
                "assignments": assignments,
                "all_submissions": all_submissions
            }
        )


@login_required(login_url='/login/')
def delete_assignment(request, id):

    if is_student(request.user):

        return HttpResponseForbidden(
            "Students cannot delete assignments."
        )

    get_object_or_404(
        Assignment,
        id=id
    ).delete()

    messages.success(request, "Deleted")

    return redirect('/assignments/')


# =====================================
# NOTICES
# =====================================

@login_required(login_url='/login/')
def notices(request):

    if request.method == "POST":

        if is_student(request.user):

            return HttpResponseForbidden(
                "Students cannot add notices."
            )

        Notice.objects.create(
            title=request.POST.get('title'),
            message=request.POST.get('message')
        )

        users = User.objects.all()

        emails = []

        for user in users:

            if user.email:

                emails.append(user.email)

        send_mail(

            'New Notice Published',

            'A new notice has been added in SmartSMS.',

            'admin@smartsms.com',

            emails,

            fail_silently=True

        )

        messages.success(
            request,
            "Notice Added Successfully"
        )

        return redirect('/notices/')

    return render(request, 'notices.html', {

        'notices': Notice.objects.all()

    })


@login_required(login_url='/login/')
def delete_notice(request, id):

    if is_student(request.user):

        return HttpResponseForbidden(
            "Students cannot delete notices."
        )

    get_object_or_404(
        Notice,
        id=id
    ).delete()

    messages.success(request, "Deleted")

    return redirect('/notices/')


# =====================================
# FEES
# =====================================

@login_required(login_url='/login/')
def fees(request):

    return render(request, 'fees.html', {

        'fee_records': Fee.objects.all(),

        'students': Student.objects.all()

    })


@login_required(login_url='/login/')
def edit_fee(request, id):

    if is_student(request.user):

        return HttpResponseForbidden(
            "Students cannot edit fees."
        )

    return render(request, 'edit_fee.html')


@login_required(login_url='/login/')
def delete_fee(request, id):

    if is_student(request.user):

        return HttpResponseForbidden(
            "Students cannot delete fees."
        )

    get_object_or_404(
        Fee,
        id=id
    ).delete()

    messages.success(request, "Deleted")

    return redirect('/fees/')


# =====================================
# TIMETABLE
# =====================================
@login_required(login_url='/login/')
def timetable(request):

    if request.method == "POST":

        day = request.POST.get('day')
        subject = request.POST.get('subject')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        room = request.POST.get('room')

        Timetable.objects.create(
            day=day,
            subject=subject,
            start_time=start_time,
            end_time=end_time,
            room=room
        )

        messages.success(request, "Timetable Added Successfully")

        return redirect('/timetable/')

    timetables = Timetable.objects.all()

    context = {
        'records': timetables
    }

    return render(request, 'timetable.html', context)

@login_required(login_url='/login/')
def delete_timetable(request, id):

    if is_student(request.user):

        return HttpResponseForbidden(
            "Students cannot delete timetable."
        )

    timetable = get_object_or_404(Timetable, id=id)

    timetable.delete()

    messages.success(request, "Deleted Successfully")

    return redirect('/timetable/')


# =====================================
# PDF DOWNLOAD
# =====================================

@login_required(login_url='/login/')
def download_student_report(request):

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'attachment; filename="student_report.pdf"'
    )

    pdf = canvas.Canvas(
        response,
        pagesize=letter
    )

    pdf.setFont("Helvetica-Bold", 20)

    pdf.drawString(
        180,
        760,
        "Student Management Report"
    )

    pdf.line(40, 745, 550, 745)

    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        40,
        720,
        "Generated from SmartSMS Dashboard"
    )

    y = 680

    students = Student.objects.all()

    pdf.setFont("Helvetica-Bold", 13)

    pdf.drawString(40, y, "Student Records")

    y -= 30

    pdf.setFont("Helvetica", 11)

    for student in students:

        pdf.drawString(
            50,
            y,
            f"ID: {student.student_id}"
        )

        pdf.drawString(
            150,
            y,
            f"Name: {student.name}"
        )

        pdf.drawString(
            340,
            y,
            f"Course: {student.course}"
        )

        y -= 25

        if y < 80:

            pdf.showPage()

            y = 750

    pdf.setFont("Helvetica-Oblique", 10)

    pdf.drawString(
        180,
        40,
        "Generated by SmartSMS Project"
    )

    pdf.save()

    return response


# =====================================
# CHATBOT
# =====================================
@login_required(login_url='/login/')
def chatbot(request):

    response = ""

    if request.method == "POST":

        message = request.POST.get(
            'message'
        ).lower()

        # STUDENT

        if "student" in message:

            response = (
                "Student module manages "
                "student records, profiles, "
                "courses, contact details, "
                "and academic information."
            )

        # ATTENDANCE

        elif "attendance" in message:

            response = (
                "Attendance module helps "
                "teachers track student "
                "presence and attendance "
                "analytics efficiently."
            )

        # MARKS

        elif "marks" in message:

            response = (
                "Marks module stores "
                "academic performance, "
                "subject-wise marks, "
                "and leaderboard analytics."
            )

        # FEES

        elif "fee" in message:

            response = (
                "Fee management module "
                "tracks paid fees, due "
                "fees, and financial records."
            )

        # ASSIGNMENT

        elif "assignment" in message:

            response = (
                "Assignments module allows "
                "teachers to upload tasks "
                "and students to submit "
                "assignment files online."
            )

        # NOTICE

        elif "notice" in message:

            response = (
                "Notice module is used "
                "to publish academic "
                "announcements and updates."
            )

        # DASHBOARD

        elif "dashboard" in message:

            response = (
                "Dashboard provides "
                "real-time analytics, "
                "charts, statistics, "
                "and academic insights."
            )

        # LOGIN

        elif "login" in message:

            response = (
                "Secure login system is "
                "implemented using Django "
                "authentication framework."
            )

        # ROLE

        elif "role" in message:

            response = (
                "This project supports "
                "Admin, Teacher, and "
                "Student role-based access."
            )

        # PDF

        elif "pdf" in message or "report" in message:

            response = (
                "PDF reports can be "
                "generated dynamically "
                "using ReportLab library."
            )

        # CHATBOT

        elif "chatbot" in message:

            response = (
                "SmartSMS chatbot provides "
                "module guidance and "
                "project assistance."
            )

        # HELP

        elif "help" in message:

            response = (
                "You can ask about students, "
                "attendance, marks, fees, "
                "assignments, reports, "
                "dashboard, and login system."
            )

        # DEFAULT

        else:

            response = (
                "Sorry, I could not "
                "understand your question. "
                "Try asking about attendance, "
                "marks, fees, dashboard, "
                "assignments, or reports."
            )

    return render(request, 'chatbot.html', {

        'response': response

    })


# =====================================
# LOGOUT
# =====================================

def logout_page(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully"
    )

    return redirect('/login/')

@login_required
def donation(request):

    donation_data = None

    donations = Donation.objects.all().order_by('-created_at')

    if request.method == 'POST':

        name = request.POST.get('name')

        upi_id = "8709791448@pthdfc"

        amount = request.POST.get('amount')

        donation_data = Donation.objects.create(
            name=name,
            upi_id=upi_id,
            amount=amount
        )

        messages.success(
            request,
            "QR Code Generated Successfully"
        )

    return render(
    request,
    'donation.html',
    {
        'donation_data': donation_data,
        'donations': donations,
        'entered_name': name if request.method == 'POST' else '',
        'entered_amount': amount if request.method == 'POST' else ''
    }
)

@login_required
def update_donation_status(request, donation_id):

    if not request.user.is_superuser:

        return HttpResponseForbidden(
            "Only admin can update donation status."
        )

    donation = Donation.objects.get(id=donation_id)

    status = request.POST.get('status')

    donation.status = status

    donation.save()

    messages.success(
        request,
        "Donation status updated successfully!"
    )

    return redirect('/donation/')

@login_required
def fee_payment(request):

    fee_records = Fee.objects.all().order_by('-id')

    payment_data = None

    if request.method == 'POST':

        student_id = request.POST.get('student')

        total_fee = request.POST.get('total_fee')

        paid_fee = request.POST.get('paid_fee')

        student = Student.objects.get(id=student_id)

        due_fee = int(total_fee) - int(paid_fee)

        payment_data = Fee.objects.create(

            student=student,

            total_fee=total_fee,

            paid_fee=paid_fee,

            due_fee=due_fee
        )

        upi_link = f"upi://pay?pa=8709791448@pthdfc&pn=SmartCollege&am={paid_fee}&cu=INR"

        qr = qrcode.make(upi_link)

        buffer = BytesIO()

        qr.save(buffer, format='PNG')

        payment_data.qr_code.save(
            f'fee_{payment_data.id}.png',
            File(buffer),
            save=True
        )

        messages.success(
            request,
            "Fee QR Generated Successfully!"
        )

    return render(

        request,

        'fees.html',

        {
            'payment_data': payment_data,
            'fee_records': fee_records,
            'students': Student.objects.all()
        }
    )