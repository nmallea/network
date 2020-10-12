from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json

from .models import User, Post, Follower, Like


def index(request):
    if (request.method == 'PUT'):
        put_data = json.loads(request.body)
        handle_put(request, put_data)
    all_posts = Post.objects.all().order_by('-timestamp')
    all_posts.reverse()

    paginated_posts = paginate(request, all_posts)

    liked_posts = []
    try:
        logged_in_user = User.objects.get(username=request.user.username)
        liked_posts = get_likes(request)
        guest_user = False
    except:
        logged_in_user = None
        guest_user = True
    return render(request, "network/index.html", context={
        "posts": paginated_posts,
        "title": "All Posts",
        "empty_msg": "Nothing has been posted yet!",
        "logged_in_user": logged_in_user,
        "liked_posts": liked_posts,
        "guest_user": guest_user
    })

def paginate(request, posts):
    page = request.GET.get('page', 1)
    paginator = Paginator(posts, 10)
    try:
        paginated_posts = paginator.page(page)
    except PageNotAnInteger:
        paginated_posts = paginator.page(1)
    except EmptyPage:
        paginated_posts = paginator.page(paginator.num_pages)
    return paginated_posts

def login_view(request):
    if request.user.is_authenticated: # person already logged in
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.user.is_authenticated: # person already logged in
        return HttpResponseRedirect(reverse("index"))
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def create(request):
    if request.method == "POST":
        content = request.POST["content"]
        author = request.user

        # TODO: consider enabling markdown posts

        p = Post(author=author, content=content)
        p.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/create.html")

def profile(request, user):
    if (request.method == 'PUT'):
        put_data = json.loads(request.body)
        handle_put(request, put_data)
    try:
        user_info = User.objects.get(username=user)
        follower_list = Follower.objects.all().filter(following=user_info)
        user_followers = []
        for follower in follower_list: # get follower usernames
            user_followers.append(follower.username)
        following_list = Follower.objects.all().filter(username=user_info.username)

        if request.method == "POST":
            if request.user.username in user_followers: # unfollow
                logged_in_user = User.objects.get(username=request.user.username)
                Follower.objects.all().filter(following=user_info,username=request.user.username).delete()
                logged_in_user.save()
            else: # follow
                f = Follower(username=request.user.username, following=user_info)
                f.save()
            return HttpResponseRedirect(reverse("profile", args=(user,)))
        else:
            user_posts = Post.objects.all().filter(author=user_info).order_by("-timestamp")

            paginated_posts = paginate(request, user_posts)

            try:
                liked_posts = get_likes(request)
                guest_user = False
            except: # no one is logged in
                liked_posts =[]
                guest_user = True

            try:
                logged_in_user = User.objects.get(username=request.user.username)
            except:
                logged_in_user = None
            isFollowing = False
            if request.user.username in user_followers:
                # check if logged in user follows the profiled user
                isFollowing = True
            return render(request, "network/profile.html", context={
                "user_info": user_info,
                "posts": paginated_posts,
                "logged_in_user": logged_in_user,
                "isFollowing": isFollowing,
                "follower_count": len(user_followers),
                "following_count": len(following_list),
                "title": "Posts",
                "empty_msg": user_info.username + " is a lurker LOL. They haven't posted anything yet!",
                "liked_posts": liked_posts,
                "guest_user": guest_user
            })
    except: # user doesn't exist
        return render(request, "network/error.html", context={
            "error_type": "Profile Does Not Exist",
            "message": "Your request for " + user +"\'s profile did not return a match."
        })

@login_required
def following_page(request):
    if (request.method == 'PUT'):
        put_data = json.loads(request.body)
        handle_put(request, put_data)
    following_list = Follower.objects.all().filter(username=request.user.username)
    posts = []
    liked_posts = get_likes(request)
    for following in following_list:
        user_posts = Post.objects.all().filter(author=following.following)
        for post in user_posts:
            posts.append(post)
    posts = sorted(posts, key=lambda x: x.timestamp, reverse=True)

    paginated_posts = paginate(request, posts)

    return render(request, "network/index.html", context={
        "posts": paginated_posts,
        "title": "Your Feed",
        "empty_msg": "None of the users you follow have posted anything!",
        "liked_posts": liked_posts
    })

def get_likes(request):
    user_likes = Like.objects.all().filter(user=request.user)
    liked_posts = []
    for like in user_likes:
        liked_posts.append(like.post)
    return liked_posts

def update_likes(posts):
    for post in posts:
        post.likes = len(Like.objects.all().filter(post=post))
        post.save()

def handle_put(request, data):
    if (data['type'] == 'edit'):
        edit_post = Post.objects.get(id=data['post_id'])
        edit_post.content = data['new_content']
        edit_post.save()
    elif (data['type'] == 'like'):
        current_user = User.objects.get(username=request.user)
        liked_post = Post.objects.get(id=data['post_id'])
        l = Like(user=current_user, post=liked_post)
        l.save()
        update_likes([liked_post])
    elif (data['type'] == 'unlike'):
        print('unlike the post')
        current_user = User.objects.get(username=request.user)
        unliked_post = Post.objects.get(id=data['post_id'])
        Like.objects.all().filter(post=unliked_post, user=current_user).delete()
        update_likes([unliked_post])