import time
import json
import webbrowser
import base64
from collections import Counter

import requests
import os
from urllib.parse import urlencode

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.translation import gettext as _

from .forms import RegistrationForm, LoginForm, ProfileEditForm, FeedbackForm, WrapForm, LoginFormMobile
from .models import Profile, Feedback, Wrap
from django.conf import settings



#REGISTRATION VIEWS
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.save()
            return redirect('success')
        else:
            return render(request, 'register.html', {'form': form})
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def register_mobile(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.save()
            return redirect('success')
        else:
            return render(request, 'register_mobile.html', {'form': form})
    else:
        form = RegistrationForm()
    return render(request, 'register_mobile.html', {'form': form})

def registration_successful(request):
    return render(request, 'registration_successful.html')



#LOGIN VIEWS
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home_logged_in', user)
            else:
                return redirect('invalid_login')
        else:
            return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def login_view_mobile(request):
    if request.method == 'POST':
        form = LoginFormMobile(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home_logged_in_mobile', user)
            else:
                return redirect('invalid_login_mobile')
        else:
            return render(request, 'login_mobile.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'login_mobile.html', {'form': form})

def invalid_login(request):
    return render(request, 'invalid_login.html')

def invalid_login_mobile(request):
    return render(request, 'invalid_login_mobile.html')



#PROFILE VIEWS
@login_required(login_url='login')
def profile(request, username):
    user_profile = get_object_or_404(Profile, user__username=username)
    return render(request, 'profile.html', {'profile': user_profile})

def edit_profile(request, username):
    user = request.user
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=user.username)
    else:
        form = ProfileEditForm(instance=user)
    return render(request, 'edit_profile.html', {'form': form})

def public_profile(request, username):
    user = request.user
    user_profile = request.user.profile
    wraps = Wrap.objects.filter(user=user, public=True)
    return render(request, 'public_profile.html', {'user': user, 'profile': user_profile, 'wraps': wraps})



#PASSWORD RESET VIEWS
def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email)
            if user.exists():
                token = PasswordResetTokenGenerator
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(f'/reset/{uid}/{token}/')
                message = render_to_string('password_reset_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                })
                send_mail(
                    "password_reset_subject.txt",
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                return render(request, 'password_reset_done.html')
            else:
                return redirect("user_doesnt_exist")
        else:
            form = PasswordResetForm()
        return render(request, 'password_reset.html', {'form': form})

def password_reset_mobile(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email)
            if user.exists():
                token = PasswordResetTokenGenerator
                uid = urlsafe_base64_encode(force_bytes(user[0].pk))
                reset_link = request.build_absolute_uri(f'/reset/{uid}/{token}/')
                message = render_to_string('password_reset_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                })
                send_mail(
                    "Password Reset Request",
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user[0].email],
                )
                return redirect(reverse_lazy('password_reset_done_mobile'))  # explicit redirect
            else:
                return redirect('user_doesnt_exist')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset_mobile.html', {'form': form})

def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    return render(request, 'password_reset_confirm.html')

def password_reset_complete(request):
    return render(request, 'password_reset_complete.html')

def password_reset_done_mobile(request):
    return render(request, 'password_reset_done_mobile.html')

def password_reset_confirm_mobile(request, uidb64, token):
    return render(request, 'password_reset_confirm_mobile.html')

def password_reset_complete_mobile(request):
    return render(request, 'password_reset_complete_mobile.html')



#USER DOESNT EXIST
def user_doesnt_exist(request):
    return render(request, 'user_doesnt_exist.html')



#CONTACT VIEWS
def contact_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            Feedback.objects.create(
                message=form.cleaned_data['message']
            )
            messages.success(request, 'Your feedback has been submitted successfully.')
            return redirect('contact')
        else:
            messages.error(request, 'There was an error with your submission. Please try again.')
    else:
        form = FeedbackForm()
    return render(request, 'contact.html', {'form': form})



#DELETE ACCOUNT VIEWS
def delete_account(request):
    user = request.user
    user.delete()
    return redirect('deleted')

def account_deleted(request):
    return render(request, 'account_deleted.html')



#LOGOUT VIEWS
def logout_view(request):
    logout(request)
    return redirect('home')

def logout_view_mobile(request):
    logout(request)  # log out the user
    messages.success(request, "You have been logged out.")
    return redirect('home-mobile')



#HOMEPAGE VIEWS
@login_required(login_url='login')
def home_logged_in(request, username):
    user = get_object_or_404(User, username=username)
    wraps = Wrap.objects.filter(user=user)
    data = fetch_data(request)
    if isinstance(data, JsonResponse) and data.status_code == 400:
        return redirect(home_logged_in_no_spotify, user)
    return render(request, 'logged_in_home.html', {'data': data, 'wraps': wraps})

@login_required(login_url='login_mobile')
def home_logged_in_mobile(request, username):
    user = get_object_or_404(User, username=username)
    wraps = Wrap.objects.filter(user=user)
    data = fetch_data(request)
    return render(request, 'logged_in_home_mobile.html', {'data': data, 'wraps': wraps})

@login_required(login_url='login')
def home_logged_in_no_spotify(request, username):
    user = get_object_or_404(User, username=username)
    wraps = Wrap.objects.filter(user=user)
    return render(request, 'logged_in_home_no_spotify.html')

def home(request):
    view_mode = request.GET.get('view', 'desktop')
    if view_mode == 'mobile':
        return render(request, 'home_mobile.html')
    return render(request, 'home.html')

def home_mobile(request):
    return render(request, 'home_mobile.html', {'user': request.user})



#EXPLORE PAGE VIEWS
def explore(request):
    wraps = Wrap.objects.filter(public=True)
    return render(request, 'explore.html', {'wraps': wraps})



#SPOTIFY VIEWS
def spotify_login(request):
    if "spotify_token" in request.session:
        del request.session["spotify_token"]
    cleanup()
    client_id = settings.SPOTIFY_CLIENT_ID
    auth_headers = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": "user-top-read user-library-read user-read-recently-played user-follow-read"
    }
    return redirect("https://accounts.spotify.com/authorize?" + urlencode(auth_headers))

from django.contrib.auth.decorators import login_required

@login_required
def spotify_callback(request):
    spotifyToken = request.session.get('spotify_token', None)
    code = request.GET.get('code')
    if not spotifyToken and code:
        client_id = settings.SPOTIFY_CLIENT_ID
        client_secret = settings.SPOTIFY_CLIENT_SECRET
        encoded_credentials = base64.b64encode(client_id.encode() + b':' + client_secret.encode()).decode("utf-8")
        token_headers = {
            "Authorization": "Basic " + encoded_credentials,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI
        }
        r = requests.post("https://accounts.spotify.com/api/token", data=token_data, headers=token_headers)
        token = r.json()["access_token"]
        request.session["spotify_token"] = token
    
    if not request.user.is_authenticated or not request.user.username:
        return redirect('login')  # or another appropriate view

    return redirect('home_logged_in', username=request.user.username)


@never_cache
def spotify_data(request):
    token = request.session.get('spotify_token')
    if not token:
        return redirect('users:spotify_login')
    user_headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
    }
    user_params = {
        "limit": 10,
        "time_range": "short_term"
    }
    try:
        top_artists = requests.get("https://api.spotify.com/v1/me/top/artists", params=user_params, headers=user_headers)
        top_tracks = requests.get("https://api.spotify.com/v1/me/top/tracks", params=user_params, headers=user_headers)
    except Exception as e:
        print("Error fetching data in spotify_data:", e)
    return render(request, 'users/spotify_data.html', {
        'top_artists': top_artists.json(),
        'top_tracks': top_tracks.json()
    })

import requests
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@csrf_exempt
@login_required
def fetch_data(request):
    time_range = request.POST.get('time_range', 'short_term')
    limit = int(request.POST.get('limit', 10))
    spotify_token = request.session.get('spotify_token')
    if not spotify_token:
        return JsonResponse({'success': False, 'error': 'No Spotify token found.'}, status=400)
    headers = {"Authorization": f"Bearer {spotify_token}"}
    params = {"limit": limit, "time_range": time_range}
    try:
        top_artists = requests.get("https://api.spotify.com/v1/me/top/artists", headers=headers, params=params).json()
        saved_albums = requests.get("https://api.spotify.com/v1/me/albums", headers=headers, params=params).json()
        saved_episodes = requests.get("https://api.spotify.com/v1/me/episodes", headers=headers,params=params).json()
        playlists = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers, params=params).json()
        recent_tracks = requests.get("https://api.spotify.com/v1/me/player/recently-played", headers=headers, params=params).json()
        audiobooks = requests.get("https://api.spotify.com/v1/me/audiobooks", headers=headers, params=params).json()
        top_tracks = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers, params=params).json()
        followed_artists = requests.get("https://api.spotify.com/v1/me/following", headers=headers, params={"type": "artist"}).json()
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    artists = [
            {
                'name': artist['name'],
                'image': artist['images'][0]['url'] if artist['images'] else None,
            }
            for artist in top_artists.get('items', [])
        ]
    albums = [
        {
            'name': album['album']['name'],
            'artists': ', '.join([artist['name'] for artist in album['album']['artists']]),
            'image': album['album']['images'][0]['url'] if album['album']['images'] else None,
        }
        for album in saved_albums.get('items', [])
    ]
    episodes = [
            {
                'name': episode['episode']['name'],
                'show': episode['episode']['show']['name'],
                'added_at': episode['added_at']
            }
            for episode in saved_episodes.get('items', [])
        ]
    playlists = [
            {
                'name': playlist['name'],
                'id': playlist['id'],
                'tracks': playlist['tracks']['total'],
                'image': playlist['images'][0]['url'] if playlist['images'] else None,
                'owner': playlist['owner']['display_name']
            }
            for playlist in playlists.get('items', [])
        ]
    recent_tracks = [
    {
        'track_name': track['track']['name'],
        'artist_name': ', '.join(artist['name'] for artist in track['track']['artists']),
        'album_name': track['track']['album']['name'],
        'played_at': track['played_at'],
        'image': track['track']['album']['images'][0]['url'] if track['track']['album']['images'] else None
    }
    for track in recent_tracks.get('items', [])
    ]
    audiobooks = [
    {
        'title': audiobook['name'],
        'authors': ', '.join(author['name'] for author in audiobook['authors']),
        'narrator': audiobook.get('narrator', None),
        'image': audiobook['images'][0]['url'] if audiobook['images'] else None
    }
    for audiobook in audiobooks.get('items', [])
]
    top_tracks = [
    {
        'name': track['name'],
        'artist': ', '.join(artist['name'] for artist in track['artists']),
        'album': track['album']['name'],
        'duration_ms': track['duration_ms'],
        'image': track['album']['images'][0]['url'] if track['album']['images'] else None
    }
    for track in top_tracks.get('items', [])
]
    followed_artists = [
    {
        'name': artist['name'],
        'id': artist['id'],
        'genres': artist.get('genres', []),
        'image': artist['images'][0]['url'] if artist['images'] else None
    }
    for artist in followed_artists.get('artists', {}).get('items', [])
]

    genres_list = [
        {
            'genres': artist['genres'],
        }
        for artist in top_artists.get('items', [])
    ]
    genres = sort_genres(genres_list)
    data = [artists, albums, episodes, playlists, recent_tracks, audiobooks, top_tracks, followed_artists, genres]
    return data

def sort_genres(genres):
    all_genres = []
    for genre_list in genres:
        all_genres.extend(genre_list['genres'])
    genre_counts = Counter(all_genres)
    top_genres = [genre for genre, count in genre_counts.most_common()]
    return top_genres



#WRAP VIEWS
@csrf_exempt
@login_required
def wrap_generate(request):
    if request.method == 'POST':
        time_range = request.POST.get('time_range', 'short_term')
        limit = int(request.POST.get('limit', 10))
        spotify_token = request.session.get('spotify_token')
        if not spotify_token:
            return JsonResponse({'success': False, 'error': 'No Spotify token found.'}, status=400)
        headers = {"Authorization": f"Bearer {spotify_token}"}
        params = {"limit": limit, "time_range": time_range}
        try:
            top_artists = requests.get("https://api.spotify.com/v1/me/top/artists", headers=headers, params=params).json()
            top_tracks = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers, params=params).json()
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        artists = [
            {
                'name': artist['name'],
                'image': artist['images'][0]['url'] if artist['images'] else None,
            }
            for artist in top_artists.get('items', [])
        ]
        tracks = [
            {
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'album': track['album']['name'],
                'image': track['album']['images'][0]['url'],
            }
            for track in top_tracks.get('items', [])]
        genres_list = [
            {
                'genres': artist['genres'],
            }
            for artist in top_artists.get('items', [])
        ]
        genres = sort_genres(genres_list)
        wrap = Wrap.objects.create(
            user=request.user,
            title=f"{time_range.capitalize()} Wrap",
            top_artists=artists,
            top_tracks=tracks,
            top_genres=genres,
        )
        return JsonResponse({
            'success': True,
            'wrap_id': wrap.id,
            'wrap_title': wrap.title,
            'top_artists': artists,
            'top_tracks': tracks,
            'top_genres': genres,
        })
    elif request.method == 'PUT':
        try:
            body = json.loads(request.body.decode('utf-8'))
            wrap_id = body.get('wrap_id')
            custom_title = body.get('custom_title')
            wrap = Wrap.objects.get(id=wrap_id, user=request.user)
            wrap.title = custom_title
            wrap.save()
            return JsonResponse({'success': True, 'wrap_title': wrap.title})
        except Wrap.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Wrap not found.'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@login_required
def wrap_detail(request, wrap_id):
    try:
        wrap = Wrap.objects.get(id=wrap_id, user=request.user)
        return JsonResponse({
            'success': True,
            'wrap_id': wrap.id,
            'wrap_title': wrap.title,
            'top_artists': wrap.top_artists,
            'top_tracks': wrap.top_tracks,
            'wrap_public': wrap.public,
        })
    except Wrap.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Wrap not found.'}, status=404)

@login_required
def wrap_detail_view(request, wrap_id):
    wrap = Wrap.objects.get(id=wrap_id)
    return render(request, 'wrap_detail.html', {'wrap': wrap})

@csrf_exempt
@login_required
def wrap_delete(request, wrap_id):
    if request.method == 'DELETE':
        try:
            wrap = Wrap.objects.get(id=wrap_id, user=request.user)
            wrap.delete()
            return JsonResponse({'success': True})
        except Wrap.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Wrap not found.'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@login_required
def wrap_update_public(request, wrap_id):
    csrf_token = request.headers.get('X-CSRFToken', None)
    if request.method == 'POST':
        try:
            wrap = get_object_or_404(Wrap, id=wrap_id, user=request.user)
            data = json.loads(request.body)
            if "public" in data:
                wrap.public = data["public"]
                wrap.save()
                return JsonResponse({'success': True})
            return JsonResponse({'error':'Invalid data'}, status=400)
        except Wrap.DoesNotExist:
            return JsonResponse({'error': 'Wrap not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def spotify_logout(request):
    request.session.pop('spotify_token', None)
    request.session.flush()
    response = redirect('users:spotify_login')
    response.delete_cookie('sessionid')
    time.sleep(3)
    return response


def cleanup():
    for filename in os.listdir():
        if filename.startswith(".cache"):
            os.remove(filename)
            print(f"Removed cache file: {filename}")