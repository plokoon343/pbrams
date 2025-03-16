from django.urls import path
from userauth import views

app_name= "userauth"

urlpatterns = [
    path("home/", views.home, name="home"),
    path("about-us/", views.about_us, name="about_us"),
    path("signup/", views.RegisterView, name= "signup"),
    path("login/", views.LoginView, name= "login"),
    path("logout/", views.LogoutView, name= "logout"),
    path("profile/", views.ProfileView, name= "profile"),
    path("changepassword/", views.ChangePasswordView, name= "changepassword"),
    path('dashboard/', views.StudentDashboardView, name='student_dashboard'),
    path('occupied-rooms/', views.OccupiedRoomsView, name='occupied_rooms'),
    path("request-room/", views.RequestRoomView, name="request_room"),


]