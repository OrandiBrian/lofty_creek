from django.urls import path
from . import views

app_name = 'sms'

urlpatterns = [
    path('login/', views.sms_login, name='login'),
    path('logout/', views.sms_logout, name='logout'),
    path('', views.dashboard_overview, name='overview'),
    path('compose/', views.compose_sms, name='compose'),
    path('contacts/', views.manage_contacts, name='contacts'),
    path('contacts/upload/', views.upload_contacts, name='upload_contacts'),
    path('contacts/delete/<int:contact_id>/', views.delete_contact, name='delete_contact'),
    path('campaign/<int:campaign_id>/resend/', views.resend_campaign, name='resend_campaign'),
    path('campaign/<int:campaign_id>/delete/', views.delete_campaign, name='delete_campaign'),
    path('message/<int:message_id>/resend/', views.resend_message, name='resend_message'),
    path('templates/', views.manage_templates, name='templates'),
    path('templates/delete/<int:template_id>/', views.delete_template, name='delete_template'),
    path('delivery-report/', views.delivery_report, name='delivery_report'),
]
