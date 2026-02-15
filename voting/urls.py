from django.urls import path
from . import views, admin_views

urlpatterns = [
    # Student URLs
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('vote/<str:election_id>/', views.vote_page, name='vote_page'),
    path('vote/<str:election_id>/submit/', views.submit_vote, name='submit_vote'),
    path('vote/<str:election_id>/confirmation/', views.vote_confirmation, name='vote_confirmation'),
    
    # Admin URLs
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/elections/', admin_views.manage_elections, name='manage_elections'),
    path('admin/elections/create/', admin_views.create_election, name='create_election'),
    path('admin/elections/<str:election_id>/edit/', admin_views.edit_election, name='edit_election'),
    path('admin/elections/<str:election_id>/delete/', admin_views.delete_election, name='delete_election'),
    path('admin/elections/<str:election_id>/candidates/', admin_views.manage_candidates, name='manage_candidates'),
    path('admin/candidates/<str:candidate_id>/delete/', admin_views.delete_candidate, name='delete_candidate'),
    path('admin/elections/<str:election_id>/results/', admin_views.view_results, name='view_results'),
    path('admin/students/', admin_views.manage_students, name='manage_students'),
    path('admin/students/<str:user_id>/delete/', admin_views.delete_student, name='delete_student'),
]
