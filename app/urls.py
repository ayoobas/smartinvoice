from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = [
     path("", views.home),
     path("geninvoice/", views.generate_invoice, name="generate_invoice"),
     path('invoice/<int:pk>/', views.view_invoice, name="view_invoice"),
 ]+ static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
