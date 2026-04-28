import requests
import pandas as pd
import time
import urllib.parse
from bs4 import BeautifulSoup
import os

GENRES_OFFICIAL = [
    'Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 
    'Sports', 'Racing', 'Casual', 'Massively Multiplayer'
]

TAGS_ADDITIONAL = [
    'Horror', 'Shooter', 'Survival', 'Open World', 'Sci-fi', 'Fantasy'
]

ALL_LABELS = GENRES_OFFICIAL + TAGS_ADDITIONAL

def get_games_by_label(label, limit=2000):
    """Retrieve a list of games by genre or tag via SteamSpy"""
    request_type = 'genre' if label in GENRES_OFFICIAL else 'tag'
    
    encoded_label = urllib.parse.quote(label)
    url = f'https://steamspy.com/api.php?request={request_type}&{request_type}={encoded_label}'
    
    try:
        response = requests.get(url)
        data = response.json()
        if not data: return []
        games = list(data.values())
        return games[:limit]
    except Exception as e:
        print(f"Error retrieving {label}: {e}")
        return []

def get_app_details(appid):
    """Fetch game description and genre data from the Steam Store API"""
    url = f'https://store.steampowered.com/api/appdetails?appids={appid}&l=en'
    for _ in range(3):
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            if data and str(appid) in data and data[str(appid)]['success']:
                time.sleep(2.0)
                return data[str(appid)]['data']
        except Exception: 
            time.sleep(2)
            continue
    return None

def clean_description(html_description):
    if not html_description: return ''
    soup = BeautifulSoup(html_description, 'html.parser')
    for element in soup(['script', 'style']):
        element.decompose()
    text = soup.get_text(separator=' ')
    return ' '.join(text.split()).strip()

def process_single_game(appid, current_label, collected_appids):
    """Process a single game and align its search tags with the official genre."""
    if appid in collected_appids:
        return None
        
    app_details = get_app_details(appid)
    if not app_details or app_details.get('type', '') != 'game':
        return None  

    steam_genres = [g['description'] for g in app_details.get('genres', [])]
    
    combined_labels = set(steam_genres + [current_label])
    
    final_labels = [l for l in combined_labels if l in ALL_LABELS]
    
    if not final_labels:
        return None  
        
    description = clean_description(app_details.get('detailed_description', ''))
    if len(description.split()) < 15:
        return None  
        
    return {
        'title': app_details.get('name', ''),
        'genres': ', '.join(final_labels),
        'description': description
    }

def start_collection(label_list, final_file, limit_per_label=1000):
    all_collected_data = []
    collected_appids = set()

    os.makedirs(os.path.dirname(final_file), exist_ok=True)

    for label in label_list:
        print(f"\n--- Investigating Category: {label} ---")
        raw_games = get_games_by_label(label, limit=limit_per_label * 3)
        
        count = 0
        for game in raw_games:
            if count >= limit_per_label:
                break
                
            appid = game.get('appid')
            game_data = process_single_game(appid, label, collected_appids)
            
            if game_data:
                all_collected_data.append(game_data)
                collected_appids.add(appid)
                count += 1
                print(f"[{label}] {count}. Captured: {game_data['title']} (Labels: {game_data['genres']})")
        
        df_temp = pd.DataFrame(all_collected_data)
        df_temp.to_csv(final_file, index=False, encoding='utf-8')
        print(f"✅ Sub-total for {label} saved. Current Dataset Size: {len(df_temp)}")

    print(f"\nCOMPLETE! Final Dataset Size: {len(all_collected_data)}")

if __name__ == '__main__':
    start_collection(
        label_list=ALL_LABELS, 
        final_file='../data/game_genre_dataset.csv', 
        limit_per_label=1000 
    )