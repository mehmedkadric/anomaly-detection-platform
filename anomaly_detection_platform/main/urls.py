from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("about/", views.about_us, name="about"),
    path("profile/", views.profile, name="profile"),
    path("playground/", views.playground, name="playground"),
    path('generate-fake-data/', views.generate_fake_data, name='generate-fake-data'),
    path('learning-corner/', views.learning_corner_view, name='learning-corner'),
    path('analysis/', views.analysis, name='analysis'),
]
