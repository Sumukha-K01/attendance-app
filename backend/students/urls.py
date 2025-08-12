# project urls.py
from django.contrib import admin
from django.urls import path, include
from .views import (
    ResultsAPI, 
    ClassResultDashBoardAPI, 
    StudentResultsDetailAPI, 
    SubjectResultsDashboardAPI, 
    SubjectResultsAPI, 
    ListSubjectsAPI,
    ListExamsAPI,
    StudentResultListAPIView,
    BulkResultsAPI
)

urlpatterns = [
    path('', ResultsAPI.as_view(), name='results-list'),
    path('class-results/', ClassResultDashBoardAPI.as_view(), name='class-results'),
    path('student-results/<int:student_id>/', StudentResultsDetailAPI.as_view(), name='student-results'),
    path('subject-results/', SubjectResultsDashboardAPI.as_view(), name='subject-results'),
    path('subject-results-detail/', SubjectResultsAPI.as_view(), name='subject-results-detail'),
    path('subjects/', ListSubjectsAPI.as_view(), name='list-subjects'),
    path('exams/', ListExamsAPI.as_view(), name='list-exams'),
    path('students-list/', StudentResultListAPIView.as_view(), name='list-students'),
    path('bulk-results/', BulkResultsAPI.as_view(), name='bulk-results')
]
