from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.enter),
    path('select/',views.select),
    path('tests/',views.tests),
    path('test/',views.test),
    path('homeworks/',views.homeworks),
    path('homework/',views.homework),
    path('klass/',views.klass),
]