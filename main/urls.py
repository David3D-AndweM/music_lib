from django.urls import path, include
from . import views
from django.contrib import admin
from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.default, name='default'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('playlist/', views.playlist, name='playlist'),
    path('search/', views.search, name='search'),
    path('subscription/', views.subscription_plans, name='subscription_plans'),
    path('subscription/create-checkout-session/<int:plan_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('subscription/success/', views.subscription_success, name='subscription_success'),
    path('subscription/cancel/', views.subscription_cancel, name='subscription_cancel'),
]