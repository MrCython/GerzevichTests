from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.enter),
    path('select/',views.select),
    path('users/',views.users),
    path('groups/',views.groups),
    path('tt/',views.tt),
    path('questions/',views.questions),
    path('tests/',views.tests),
    path('homework/',views.homework),
    path('writing/',views.writing),
]