import os
from dotenv import load_dotenv

load_dotenv()

# Collecting Datsets
API_KEY = os.getenv('RAWG_API_KEY')
DATA_FILE_PATH = os.getenv('DATA_FILE_PATH', '../data/game_genre_dataset.csv')

LIMIT_PER_LABEL = 1000
BATCH_SIZE = 50
MIN_DESC_WORDS = 15

API_PAGE_SIZE = 40
API_TIMEOUT = 10
API_RETRY_ATTEMPTS = 3

DELAY_NORMAL = 1
DELAY_RATE_LIMIT = 5
DELAY_ERROR = 2
DELAY_CATEGORY = 5

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

# Model Train
TEST_SIZE = 0.2
RANDOM_STATE = 42
CONFIDENCE_THRESHOLD = 15.0

MODEL_DIR = '../models'
MODEL_FILE_PATH = os.path.join(MODEL_DIR, 'model_multilabel.pkl')
MLB_FILE_PATH = os.path.join(MODEL_DIR, 'mlb.pkl')

CUSTOM_STOP_WORDS = {
    'game', 'games', 'play', 'player', 'players', 'playing', 
    'experience', 'world', 'feature', 'features', 'new', 'time', 
    'make', 'take', 'get', 'like', 'one'
}

CLEANING_REGEX_PATTERNS = [
    r"all rights reserved",
    r"copyright\s*(c)?\s*\d{4}",
    r"intel\s*core\s*(i\d+)?",
    r"amd\s*ryzen",
    r"nvidia\s*geforce|gtx|rtx",
    r"directx\s*(version)?\s*\d+",
    r"minimum\s*requirements?|recommended\s*requirements?",
    r"windows\s*\d+",
    r"mac\s*os|linux"
]