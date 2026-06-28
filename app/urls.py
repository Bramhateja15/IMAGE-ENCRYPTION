from django.urls import path

from .  import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/',views.about,name='about' ),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('training/', views.training, name='training'),
    path('home/', views.home, name='home'),
    path('uploadfiles/', views.uploadfiles, name='uploadfiles'),
    path('viewfiles/', views.viewfiles, name='viewfiles'),
    path('logout/', views.logout, name='logout'),
    path('forgotpass/', views.forgotpass, name='forgotpass'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),
    path('profile/', views.profile, name='profile'),
    path('updateprofile/', views.updateprofile, name='updateprofile'),
    path('editprofile/', views.editprofile, name='editprofile'),
    path('sendrequest/<int:id>/', views.sendrequest, name='sendrequest'),
    path('viewrequests/', views.viewrequests, name='viewrequests'),
    path('acceptrequest/<int:id>/', views.acceptrequest, name='acceptrequest'),
    path('rejectrequest/<int:id>/', views.rejectrequest, name='rejectrequest'),
    path('viewresponses/', views.viewresponses, name='viewresponses'),
    path('decrypt/<int:id>/', views.decrypt, name='decrypt'),
    path('download/<int:id>/', views.download, name='download'),
    path('delete/<int:id>/', views.delete, name='delete'),


]
