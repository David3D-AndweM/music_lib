from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import playlist_user, SubscriptionPlan, UserSubscription
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from youtube_search import YoutubeSearch
import json
from django.db import IntegrityError
from django.conf import settings
import stripe
from .forms import UserRegistrationForm

stripe.api_key = settings.STRIPE_SECRET_KEY

def subscription_plans(request):
    plans = SubscriptionPlan.objects.all()
    return render(request, 'subscription_plans.html', {'plans': plans})

def create_checkout_session(request, plan_id):
    plan = SubscriptionPlan.objects.get(id=plan_id)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': plan.name,
                },
                'unit_amount': int(plan.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('subscription_success')),
        cancel_url=request.build_absolute_uri(reverse('subscription_cancel')),
    )
    return redirect(session.url, code=303)

def subscription_success(request):
    subscription = UserSubscription(user=request.user, plan=SubscriptionPlan.objects.first(), active=True)
    subscription.save()
    return render(request, 'subscription_success.html')

def subscription_cancel(request):
    return render(request, 'subscription_cancel.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            username = cd['username']
            email = cd['email']
            password = cd['password']
            try:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                # Create a corresponding playlist_user entry
                playlist_user.objects.create(username=user.username)
                login(request, user)
                return redirect('default')
            except IntegrityError:
                form.add_error('username', 'Username already exists')
                form.add_error('email', 'Email already exists')
    else:
        form = UserRegistrationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('default')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

f = open('card.json', 'r')
CONTAINER = json.load(f)

def default(request):
    global CONTAINER

    if request.method == 'POST':
        add_playlist(request)
        return HttpResponse("")

    song = 'kSFJGEHDCrQ'
    return render(request, 'player.html', {'CONTAINER': CONTAINER, 'song': song})

def playlist(request):
    try:
        cur_user, created = playlist_user.objects.get_or_create(username=request.user.username)
        if created:
            print(f"Created playlist_user entry for user '{request.user.username}'.")

        if request.method == 'GET':
            song_title = request.GET.get('song')
            if song_title:
                try:
                    song = cur_user.playlist_song_set.get(song_title=song_title)
                    song.delete()
                    print(f"Song '{song_title}' deleted from user '{request.user.username}' playlist.")
                except playlist_song.DoesNotExist:
                    print(f"Song '{song_title}' not found in user '{request.user.username}' playlist.")

        elif request.method == 'POST':
            add_playlist(request)
            return HttpResponse("")

        song = 'kSFJGEHDCrQ'  # Default song
        user_playlist = cur_user.playlist_song_set.all()
        return render(request, 'playlist.html', {'song': song, 'user_playlist': user_playlist})

    except Exception as e:
        print(f"An error occurred: {e}")
        return HttpResponse("An error occurred", status=500)
def search(request):
    if request.method == 'POST':
        add_playlist(request)
        return HttpResponse("")
    try:
        search = request.GET.get('search')
        song = YoutubeSearch(search, max_results=10).to_dict()
        song_li = [song[:10:2], song[1:10:2]]
    except:
        return redirect('/')
    return render(request, 'search.html', {'CONTAINER': song_li, 'song': song_li[0][0]['id']})

def add_playlist(request):
    cur_user = playlist_user.objects.get(username=request.user)
    if (request.POST['title'],) not in cur_user.playlist_song_set.values_list('song_title',):
        songdic = (YoutubeSearch(request.POST['title'], max_results=1).to_dict())[0]
        song__albumsrc = songdic['thumbnails'][0]
        cur_user.playlist_song_set.create(
            song_title=request.POST['title'],
            song_dur=request.POST['duration'],
            song_albumsrc=song__albumsrc,
            song_channel=request.POST['channel'],
            song_date_added=request.POST['date'],
            song_youtube_id=request.POST['songid']
        )
