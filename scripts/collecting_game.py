import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('RAWG_API_KEY')

if not API_KEY:
    raise ValueError("No API_KEY found. Check your .env file 👀")

GENRES_OFFICIAL = ['Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 'Sports', 'Racing', 'Casual', 'Massively Multiplayer']
TAGS_ADDITIONAL = ['Horror', 'Shooter', 'Survival', 'Open World', 'Sci-fi', 'Fantasy']
ALL_LABELS = GENRES_OFFICIAL + TAGS_ADDITIONAL

RAWG_MAPPING = {
    'Action': ('genres', 'action'),
    'Adventure': ('genres', 'adventure'),
    'RPG': ('genres', 'role-playing-games-rpg'),
    'Strategy': ('genres', 'strategy'),
    'Simulation': ('genres', 'simulation'),
    'Sports': ('genres', 'sports'),
    'Racing': ('genres', 'racing'),
    'Casual': ('genres', 'casual'),
    'Massively Multiplayer': ('genres', 'massively-multiplayer'),
    'Horror': ('tags', 'horror'),
    'Shooter': ('tags', 'shooter'),
    'Survival': ('tags', 'survival'),
    'Open World': ('tags', 'open-world'),
    'Sci-fi': ('tags', 'sci-fi'),
    'Fantasy': ('tags', 'fantasy')
}

def get_games_by_label(label, limit=2000):
    """Fetching games from RAWG (paginated)"""
    param_type, slug = RAWG_MAPPING[label]
    games = []
    page = 1
    
    while len(games) < limit:
        url = f"https://api.rawg.io/api/games?key={API_KEY}&{param_type}={slug}&page_size=40&page={page}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                if not results: break
                games.extend(results)
                page += 1
            else:
                print(f"⚠️ RAWG API Error: {response.status_code}")
                break
        except Exception as e:
            print(f"⚠️ Error retrieving {label}: {e}")
            break
            
    return games[:limit]

def get_app_details(game_id):
    """Fetching description by game ID from the RAWG API."""
    url = f"https://api.rawg.io/api/games/{game_id}?key={API_KEY}"
    for _ in range(3):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                time.sleep(1)
                return response.json()
            elif response.status_code == 429:
                time.sleep(5)
            else:
                break
        except Exception: 
            time.sleep(2)
            continue
    return None

def process_single_game(game_id, current_label, collected_appids):
    """Processing the game and extracting description_raw (HTML-free)"""
    if game_id in collected_appids: return None
    app_details = get_app_details(game_id)
    if not app_details: return None  

    rawg_genres = [g['name'] for g in app_details.get('genres', [])]
    rawg_tags = [t['name'] for t in app_details.get('tags', [])]
    
    all_rawg_labels = rawg_genres + rawg_tags
    if current_label not in all_rawg_labels:
        return None
    
    final_labels = list(set([l for l in all_rawg_labels if l in ALL_LABELS]))
    
    if not final_labels: return None  
    
    desc = app_details.get('description_raw', '')
    if len(desc.split()) < 15: return None  
        
    return {
        'appid': game_id, 
        'title': app_details.get('name', ''), 
        'genres': ', '.join(final_labels), 
        'description': desc
    }

def start_collection(label_list, final_file, limit_per_label=1000, batch_size=50):
    collected_appids = set()
    os.makedirs(os.path.dirname(final_file), exist_ok=True)

    if os.path.exists(final_file):
        try:
            existing_df = pd.read_csv(final_file)
            if 'appid' in existing_df.columns:
                collected_appids = set(existing_df['appid'].astype(int).tolist())
                print(f"🔄 RESUME MODE ON: Found {len(collected_appids)} existing records in the CSV.")
                print("Existing games will be automatically skipped to avoid duplicates.\n")
        except Exception as e:
            print(f"⚠️ Failed to read existing file: {e}")
    else:
        pd.DataFrame(columns=['appid', 'title', 'genres', 'description']).to_csv(final_file, index=False)

    for label in label_list:
        print(f"--- Investigating Category: {label} ---")
        raw_games = get_games_by_label(label, limit=limit_per_label)
        
        batch_data = []
        count = 0
        
        for game in raw_games:
            if count >= limit_per_label: break
                
            appid = int(game.get('id'))
            
            if appid in collected_appids:
                continue

            game_data = process_single_game(appid, label, collected_appids)
            
            if game_data:
                batch_data.append(game_data)
                collected_appids.add(appid)
                count += 1
                print(f"[{label}] {count}. Retrieved: {game_data['title']}")

                if len(batch_data) >= batch_size:
                    pd.DataFrame(batch_data).to_csv(final_file, mode='a', index=False, header=False, encoding='utf-8')
                    batch_data = []
                    print(f"💾 Batch saved (50). Current total unique count: {len(collected_appids)}")

        if batch_data:
            pd.DataFrame(batch_data).to_csv(final_file, mode='a', index=False, header=False, encoding='utf-8')
            print(f"💾 Last batch has been saved.")
        
        print(f"Category {label} has been completed.")
        
        if label != label_list[-1]: 
            print("Please wait 5 seconds before moving to the next category....\n")
            time.sleep(5)

    print(f"\nProcess completed successfully. Total unique records: {len(collected_appids)}")
    print(f"File saved in: {final_file}")

if __name__ == '__main__':
    start_collection(
        label_list=ALL_LABELS, 
        final_file='../data/game_genre_dataset.csv', 
        limit_per_label=1000 
    )