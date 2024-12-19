import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from openid.consumer.consumer import Consumer
from openid.fetchers import HTTPFetchingError
from openid.store.memstore import MemoryStore
from .models import Profile


STEAM_API_KEY = "Enter your key here"
STEAM_OPENID_URL = "https://steamcommunity.com/openid"


def index(request):
    return render(request, 'games/index.html')


def profile_page(request, steam_id):
    profile = get_object_or_404(Profile, steam_id=steam_id)
    return render(request, 'games/profile.html', {'profile': profile})


def update_profile(steam_id, profile):
    url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
    params = {
        'key': STEAM_API_KEY,
        'steamids': steam_id,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json().get('response', {}).get('players', [])[0]
        updated_profile = profile
        updated_profile.steam_id = steam_id
        updated_profile.avatar_url = data.get('avatarmedium')
        updated_profile.nickname = data.get('personaname')
        updated_profile.save()


openid_store = MemoryStore()


def steam_login(request):
    consumer = Consumer({}, openid_store)
    auth_request = consumer.begin(STEAM_OPENID_URL)
    if not auth_request:
        return redirect('/error/')
    callback_url = request.build_absolute_uri('/login/callback/')
    realm = request.build_absolute_uri('/')
    redirect_url = auth_request.redirectURL(realm=realm, return_to=callback_url)
    return redirect(redirect_url)


def steam_callback(request):
    consumer = Consumer(request.session, openid_store)
    try:
        response = consumer.complete(request.GET, request.build_absolute_uri())
        if response.status == "success":
            steam_id = response.identity_url.split("/")[-1]
            if steam_id:
                profile, created = Profile.objects.get_or_create(steam_id=steam_id)
                update_profile(steam_id, profile)
                profile.save()
                return redirect('profile', steam_id=steam_id)
            else:
                return HttpResponse("Не удалось получить данные пользователя.", status=400)
        else:
            return HttpResponse("Ошибка в OpenID-ответе", status=400)

    except HTTPFetchingError as e:
        return HttpResponse(f"Ошибка при соединении с Steam: {str(e)}", status=500)


def get_friend_list(steam_id):
    url = f"https://api.steampowered.com/ISteamUser/GetFriendList/v0001/"
    params = {
        'key': STEAM_API_KEY,
        'steamid': steam_id,
        'relationship': 'friend',
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch friend list for Steam ID {steam_id}. Status code: {response.status_code}")
        return []
    data = response.json()
    friends = [friend['steamid'] for friend in data.get('friendslist', {}).get('friends', [])]
    return friends


def get_friends_games(steam_id):
    friends = get_friend_list(steam_id)
    friends_games = {}
    for friend_id in friends:
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        params = {
            'key': STEAM_API_KEY,
            'steamid': friend_id,
            'include_appinfo': True,
            'format': 'json',
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for game in data.get('response', {}).get('games', []):
                if game['appid'] not in friends_games:
                    friends_games[game['appid']] = 1
                else:
                    friends_games[game['appid']] += 1
    return friends_games


def count_friends_with_game(game_appid, friends_games):
    if game_appid not in friends_games:
        return 0
    return friends_games[game_appid]


def get_achievements_percentage(steam_id, app_id):
    url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
    params = {
        'appid': app_id,
        'key': STEAM_API_KEY,
        'steamid': steam_id,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"No player stats available for Steam ID {steam_id} and App ID {app_id}.")
        return 0
    data = response.json()
    if 'playerstats' in data:
        achievements = data['playerstats'].get('achievements', [])
        total_achievements = len(achievements)
        completed_achievements = sum(1 for achievement in achievements if achievement['achieved'] == 1)
        if total_achievements > 0:
            percentage = int((completed_achievements / total_achievements) * 100)
        else:
            percentage = 0
        return percentage
    else:
        print(f"No player stats available for Steam ID {steam_id} and App ID {app_id}.")
        return 0


def get_games(request):
    steam_id = request.GET.get('steam_id')
    if not steam_id:
        return render(request, 'games/index.html', {'error': 'Steam ID is required'})
    url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        'key': STEAM_API_KEY,
        'steamid': steam_id,
        'include_appinfo': True,
        'format': 'json',
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return render(request, 'games/index.html', {'error': 'Failed to fetch data from Steam API'})
    data = response.json()
    games = data.get('response', {}).get('games', [])
    friends_games = get_friends_games(steam_id)
    if not games:
        return render(request, 'games/index.html', {'error': 'No games found or the account is private.'})
    game_list = [
        {
            'name': game.get('name', 'Unknown'),
            'playtime_hours': game.get('playtime_forever', 0) // 60,
            'playtime_2weeks': game.get('playtime_2weeks', 0) // 60,
            'app_id': game.get('appid'),
            'friends_with_game': count_friends_with_game(game.get('appid'), friends_games),
            'achievements_percentage': get_achievements_percentage(steam_id, game.get('appid')),
        }
        for game in games
    ]
    return render(request, 'games/game_list.html', {'games': game_list, 'steam_id': steam_id})
