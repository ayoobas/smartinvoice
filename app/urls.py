from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = [
     path("", views.home, name = 'home'),
     path("geninvoice/", views.generate_invoice, name="generate_invoice"),
    path("login/", views.login_def, name="login_def"),
    path("logout/", views.logout_user, name="user_logout"),
     path('invoice/<int:pk>/', views.view_invoice, name="view_invoice"),
     path("registerstaff/", views.StaffRegistration.as_view(), name="registerstaff"),
 ]+ static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)




