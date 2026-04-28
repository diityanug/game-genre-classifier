import requests
import pandas as pd
import time
import urllib.parse
from bs4 import BeautifulSoup

TARGET_GENRES = ['Adventure', 'Sports', 'Casual']

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
                time.sleep(0.2)
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

def process_single_game(appid, collected_appids):
    if appid in collected_appids:
        return None
        
    app_details = get_app_details(appid)
    if not app_details or app_details.get('type', '') != 'game':
        return None  
        
    raw_genres = [g['description'] for g in app_details.get('genres', [])]
    
    matched_genres = [g for g in raw_genres if g in TARGET_GENRES]
    
    if not matched_genres:
        return None  
        
    description = clean_description(app_details.get('detailed_description', ''))
    if len(description.split()) < 10:
        return None  
        
    return {
        'title': app_details.get('name', ''),
        'genres': ', '.join(matched_genres),
        'description': description
    }

def start_collection(genre_list, final_file, limit_per_genre=500):
    all_collected_data = []
    collected_appids = set()

    for genre in genre_list:
        print(f"\n--- Searching for: {genre} ---")
        raw_games = get_games_by_genre(genre, limit=limit_per_genre*2)
        
        count = 0
        for game in raw_games:
            if count >= limit_per_genre:
                break
                
            appid = game.get('appid')
            game_data = process_single_game(appid, collected_appids)
            
            if game_data:
                all_collected_data.append(game_data)
                collected_appids.add(appid)
                count += 1
                print(f"[{genre}] {count}. Collected: {game_data['title']} (Genres: {game_data['genres']})")

    df = pd.DataFrame(all_collected_data)
    df.to_csv(final_file, index=False, encoding='utf-8')
    print(f"\n✅ Success! Total unique games: {len(df)}")
    print(f"Data saved to: {final_file}")

if __name__ == '__main__':
    start_collection(
        genre_list=TARGET_GENRES, 
        final_file='../data/multigenre_game_datasets.csv', 
        limit_per_genre=500
    )