import requests
import pandas as pd
import time
import os
import re
import config

if not config.API_KEY:
    raise ValueError("No API_KEY found. Check your .env file 👀")

def get_games_by_label(label, limit=config.LIMIT_PER_LABEL):
    param_type, slug = config.RAWG_MAPPING[label]
    games = []
    page = 1
    
    while len(games) < limit:
        url = f"https://api.rawg.io/api/games?key={config.API_KEY}&{param_type}={slug}&page_size={config.API_PAGE_SIZE}&page={page}"
        try:
            response = requests.get(url, timeout=config.API_TIMEOUT)
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
    url = f"https://api.rawg.io/api/games/{game_id}?key={config.API_KEY}"
    for _ in range(config.API_RETRY_ATTEMPTS):
        try:
            response = requests.get(url, timeout=config.API_TIMEOUT)
            if response.status_code == 200:
                time.sleep(config.DELAY_NORMAL)
                return response.json()
            elif response.status_code == 429:
                time.sleep(config.DELAY_RATE_LIMIT)
            else:
                break
        except Exception: 
            time.sleep(config.DELAY_ERROR)
            continue
    return None

def process_single_game(game_id, current_label, collected_appids):
    if game_id in collected_appids: return None
    app_details = get_app_details(game_id)
    if not app_details: return None  

    rawg_genres = [g['name'] for g in app_details.get('genres', [])]
    rawg_tags = [t['name'] for t in app_details.get('tags', [])]
    
    all_rawg_labels = rawg_genres + rawg_tags
    if current_label not in all_rawg_labels:
        return None
    
    final_labels = list(set([l for l in all_rawg_labels if l in config.ALL_LABELS]))
    if not final_labels: return None  
    
    desc = app_details.get('description_raw', '')
    desc = re.sub(r'\s+', ' ', desc).strip()
    
    if len(desc.split()) < config.MIN_DESC_WORDS: return None  
        
    return {
        'appid': game_id, 
        'title': app_details.get('name', ''), 
        'genres': ', '.join(final_labels), 
        'description': desc
    }

def start_collection(label_list, final_file, limit_per_label, batch_size):
    collected_appids = set()
    os.makedirs(os.path.dirname(final_file), exist_ok=True)

    if os.path.exists(final_file):
        try:
            existing_df = pd.read_csv(final_file)
            if 'appid' in existing_df.columns:
                collected_appids = set(existing_df['appid'].astype(int).tolist())
                print(f"🔄 Resuming. {len(collected_appids)} previous records found.")
        except Exception as e:
            print(f"⚠️ Unable to read existing file: {e}")
    else:
        pd.DataFrame(columns=['appid', 'title', 'genres', 'description']).to_csv(final_file, index=False)

    for label in label_list:
        print(f"\n--- Fetching category: {label} ---")
        raw_games = get_games_by_label(label, limit=limit_per_label)
        batch_data = []
        count = 0
        
        for game in raw_games:
            if count >= limit_per_label: break
            appid = int(game.get('id'))
            if appid in collected_appids: continue

            game_data = process_single_game(appid, label, collected_appids)
            if game_data:
                batch_data.append(game_data)
                collected_appids.add(appid)
                count += 1
                print(f"[{label}] {count}. Retrieved: {game_data['title']}")

                if len(batch_data) >= batch_size:
                    pd.DataFrame(batch_data).to_csv(final_file, mode='a', index=False, header=False, encoding='utf-8')
                    batch_data = []

        if batch_data:
            pd.DataFrame(batch_data).to_csv(final_file, mode='a', index=False, header=False, encoding='utf-8')
        
        if label != label_list[-1]: 
            time.sleep(config.DELAY_CATEGORY)

if __name__ == '__main__':
    start_collection(
        label_list=config.ALL_LABELS, 
        final_file=config.DATA_FILE_PATH, 
        limit_per_label=config.LIMIT_PER_LABEL,
        batch_size=config.BATCH_SIZE
    )