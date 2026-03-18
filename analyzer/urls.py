from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login_view, name='login_view'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout_view'),
    path('tool/', views.analyzer_tool, name='analyzer_tool'),
    path('api/get_branch_data/<int:branch_id>/', views.get_branch_data, name='get_branch_data'),
    path('tool/submit/', views.submit_analysis, name='submit_analysis'),
    path('result/<int:selection_id>/', views.analysis_result, name='analysis_result'),
]
