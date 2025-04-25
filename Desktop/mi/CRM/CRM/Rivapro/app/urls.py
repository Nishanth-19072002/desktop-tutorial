from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', LoginView.as_view(template_name='login.html'), name='login'),  # Login
    path('login/', LoginView.as_view(template_name='app/login.html'), name='login'),  # Login
    path('logout/', LogoutView.as_view(template_name='app/logout.html'), name='logout'),
    path('user/<int:user_id>/manage_modules/', views.manage_module_visibility, name='manage_module_visibility'),
    path('<slug:module_slug>/', views.module_dashboard, name='module_dashboard'),
    path('user/<int:user_id>/submodule-visibility/', views.manage_submodule_visibility, name='manage_submodule_visibility'),
    path('submodule/<slug:submodule_slug>/', views.submodule_visibility, name='submodule_visibility'),

    # exporting 

]
