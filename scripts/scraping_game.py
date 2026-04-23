import requests
import pandas as pd
import time
import urllib.parse
from bs4 import BeautifulSoup

def get_games_by_genre(genre, limit=1500, request_type='genre'):
    encoded_genre = urllib.parse.quote(genre)
    url = f'https://steamspy.com/api.php?request={request_type}&{request_type}={encoded_genre}'
    try:
        response = requests.get(url)
        data = response.json()
        games = list(data.values())
        return games[:limit]
    except Exception as e:
        print(f"Error retrieving data for {request_type} '{genre}': {e}")
        return []

def get_app_details(appid):
    url = f'https://store.steampowered.com/api/appdetails?appids={appid}&l=en'
    for attempt in range(3):  # Trying up to 3 times
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            if data[str(appid)]['success']:
                time.sleep(0.1)  # Pause to avoid request limits
                return data[str(appid)]['data']
        except Exception as e:
            time.sleep(1)  # Wait before retrying
            continue
    return None

def clean_description(html_description):
    if not html_description:
        return ''
    soup = BeautifulSoup(html_description, 'html.parser')
    for element in soup(['script', 'style']):
        element.decompose()
    text = soup.get_text(separator=' ')
    clean_text = ' '.join(text.split())
    return clean_text.strip()

def collect_data_for_genre(genre_name, file_name, genre_limit=500):
    genre = genre_name
    request_type = 'genre'
    all_games = []
    collected_appids = set()

    print(f"\nCollecting games for genre {request_type}: {genre}")
    games_collected = 0
    games = get_games_by_genre(genre, limit=genre_limit*3, request_type=request_type)
    if not games:
        print(f"No games found for genre {request_type} '{genre}'")
        return
    for game in games:
        if games_collected >= genre_limit:
            break
        appid = game.get('appid', '')
        if appid in collected_appids:
            continue  # Skip if the game has already been collected
        app_details = get_app_details(appid)
        if app_details:
            # Ensuring the item is a game, not another application like software
            if app_details.get('type', '') != 'game':
                continue  # Skip if not game
            # Verify that the game has the desired genre
            game_genres = [g['description'] for g in app_details.get('genres', [])]
            if genre not in game_genres:
                continue  # Skip if the genre does not match
            description = clean_description(app_details.get('detailed_description', ''))
            if not description.strip():
                continue  # Skip if the description is empty
            game_data = {
                'title': app_details.get('name', ''),
                'genres': ', '.join(game_genres),
                'description': description
            }
            all_games.append(game_data)
            collected_appids.add(appid)
            games_collected += 1
            print(f"{games_collected}. Games collected for: {game_data['title']}")
        else:
            continue  # Skip if game details cannot be retrieved
    print(f"Total games collected for genre {request_type} '{genre}': {games_collected}")

    if games_collected < genre_limit:
        print(f"Warning: Only {games_collected} games collected for genre '{genre}'.")
    else:
        print(f"Successfully collected {games_collected} games for genre '{genre}'.")

    # Save game datasest to CSV file
    df = pd.DataFrame(all_games)
    df.to_csv(file_name, index=False, encoding='utf-8')
    print(f"\n Game dataset collection complete. Data saved '{file_name}'")

# %%
if __name__ == '__main__':
    # Collecting games for genre 'Adventure'
    collect_data_for_genre('Adventure', '../data/adventure_games_data.csv', genre_limit=500)

    # Collecting games for genre 'Sports'
    collect_data_for_genre('Sports', '../data/sports_games_data.csv', genre_limit=500)

    # Collecting games for genre 'Casual'
    collect_data_for_genre('Casual', '../data/casual_games_data.csv', genre_limit=500)


