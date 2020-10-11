from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("addpost", views.addpost, name="addpost"),
    path("savepost", views.savepost, name="savepost"),
    path("editpost", views.editpost, name="editpost"),
    path("likepost", views.likepost, name="likepost"),
    path("unlikepost", views.unlikepost, name="unlikepost"),
    path("getlikes", views.getlikes, name="getlikes"),
    path("getfollowdetails", views.getfollowdetails, name="getfollowdetails"),
    path("allposts", views.allposts, name="allposts"),
    path("followingposts", views.followingposts, name="followingposts"),
    path("<str:username>", views.userprofile, name="userprofile"),
    path("<str:username>/follow", views.follow, name="follow"),
    path("<str:username>/unfollow", views.unfollow, name="unfollow"),

    ] 
