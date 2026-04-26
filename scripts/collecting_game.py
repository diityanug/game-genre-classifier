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
    for _ in range(3):
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            if data[str(appid)]['success']:
                time.sleep(0.1) 
                return data[str(appid)]['data']
        except Exception: 
            time.sleep(1)
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

def process_single_game(appid, genre_name, collected_appids):
    if appid in collected_appids:
        return None
        
    app_details = get_app_details(appid)
    if not app_details:
        return None
    
    if app_details.get('type', '') != 'game':
        return None  
        
    game_genres = [g['description'] for g in app_details.get('genres', [])]
    if genre_name not in game_genres:
        return None  
        
    description = clean_description(app_details.get('detailed_description', ''))
    if not description.strip():
        return None  
        
    return {
        'title': app_details.get('name', ''),
        'genres': ', '.join(game_genres),
        'description': description
    }

def collect_data_for_genre(genre_name, file_name, genre_limit=500):
    print(f"\nCollecting games for genre: {genre_name}")
    
    games = get_games_by_genre(genre_name, limit=genre_limit*3, request_type='genre')
    if not games:
        print(f"No games found for genre '{genre_name}'")
        return
        
    all_games = []
    collected_appids = set()
    games_collected = 0

    for game in games:
        if games_collected >= genre_limit:
            break
            
        appid = game.get('appid', '')
        game_data = process_single_game(appid, genre_name, collected_appids)
        
        if game_data:
            all_games.append(game_data)
            collected_appids.add(appid)
            games_collected += 1
            print(f"{games_collected}. Games collected for: {game_data['title']}")

    print(f"Total games collected for genre '{genre_name}': {games_collected}")

    if games_collected < genre_limit:
        print(f"Warning: Only {games_collected} games collected for genre '{genre_name}'.")
    else:
        print(f"Successfully collected {games_collected} games for genre '{genre_name}'.")

    # Save game dataset to CSV file
    df = pd.DataFrame(all_games)
    df.to_csv(file_name, index=False, encoding='utf-8')
    print(f"\nGame dataset collection complete. Data saved to '{file_name}'")


if __name__ == '__main__':
    # Collecting games for genre 'Adventure'
    collect_data_for_genre('Adventure', '../data/adventure_games_data.csv', genre_limit=500)

    # Collecting games for genre 'Sports'
    collect_data_for_genre('Sports', '../data/sports_games_data.csv', genre_limit=500)

    # Collecting games for genre 'Casual'
    collect_data_for_genre('Casual', '../data/casual_games_data.csv', genre_limit=500)


