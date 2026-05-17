from . import views
from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [

    # ---------- BASIC ----------
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),

    # ---------- AUTH ----------
    path('login/', login_page, name='login'),
    path('register/', register, name='register'),
    path(
    'password-reset/',

    auth_views.PasswordResetView.as_view(
        template_name='password_reset.html'
    ),

    name='password_reset'
),

path(
    'password-reset/done/',

   auth_views.PasswordResetDoneView.as_view(
    template_name='login.html'
),

    name='password_reset_done'
),

path(
    'reset/<uidb64>/<token>/',

    auth_views.PasswordResetConfirmView.as_view(
        template_name='login.html'
    ),

    name='password_reset_confirm'
),

path(
    'reset/done/',

    auth_views.PasswordResetCompleteView.as_view(
        template_name='login.html'
    ),

    name='password_reset_complete'
),
    path('logout/', logout_page, name='logout'),

    # ---------- DASHBOARD ----------
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),

    # ---------- STUDENTS ----------
    path('students/', students, name='students'),
    path('student/<int:id>/', student_detail, name='student_detail'),
    path('add-student/', add_student, name='add_student'),
    path('edit-student/<int:id>/', edit_student, name='edit_student'),
    path('delete-student/<int:id>/', delete_student, name='delete_student'),
    path('download-student-report/', download_student_report, name='download_student_report'),

    # ---------- ATTENDANCE ----------
    path('attendance/', attendance, name='attendance'),
    path('delete-attendance/<int:id>/', delete_attendance, name='delete_attendance'),

    # ---------- MARKS ----------
    path('marks/', marks, name='marks'),
    path('delete-mark/<int:id>/', delete_mark, name='delete_mark'),

    # ---------- ASSIGNMENTS ----------
    path('assignments/', assignments, name='assignments'),
    path('delete-assignment/<int:id>/', delete_assignment, name='delete_assignment'),

    # ---------- NOTICES ----------
    path('notices/', notices, name='notices'),
    path('delete-notice/<int:id>/', delete_notice, name='delete_notice'),

    # ---------- FEES ----------
    path('fees/', fee_payment, name='fees'),
    path('edit-fee/<int:id>/', edit_fee, name='edit_fee'),
    path('delete-fee/<int:id>/', delete_fee, name='delete_fee'),

    # ---------- TIMETABLE ----------
    path('timetable/', timetable, name='timetable'),
    path('delete-timetable/<int:id>/', delete_timetable, name='delete_timetable'),

    # ---------- CHATBOT ----------
    path('chatbot/', chatbot, name='chatbot'),

    path(
    'donation/',
    views.donation,
    name='donation'
),
    path(
    'update-donation-status/<int:donation_id>/',
    views.update_donation_status,
    name='update_donation_status'
),

path(
    'fee-payment/',
    views.fee_payment,
    name='fee_payment'
),
]