from django.contrib import admin
from django.urls import path, include
from login import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('base/', views.base_view, name='base'),
    path('', include('login.urls')),
]
