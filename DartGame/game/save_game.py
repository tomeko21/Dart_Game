import json
import os
import glob
from datetime import datetime

SAVES_DIR = "saves"

def ensure_save_dir():
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)

def save_game_state(data, filename=None):
    ensure_save_dir()
    
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # nazwe generujemy na podstawie daty
    if not filename:
        filename = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    filepath = os.path.join(SAVES_DIR, filename)
    
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Gra zapisana: {filepath}")
        return filename
    except Exception as e:
        print(f"Błąd zapisu: {e}")
        return None

def get_all_saves():
    """Zwraca listę słowników z informacjami o zapisach, posortowaną od najnowszych."""
    ensure_save_dir()
    files = glob.glob(os.path.join(SAVES_DIR, "*.json"))
    save_list = []
    
    for fp in files:
        try:
            with open(fp, 'r') as f:
                data = json.load(f)
                info = {
                    "filename": os.path.basename(fp),
                    "timestamp": data.get("timestamp", "???"),
                    "mode": data.get("game_mode", "UNKNOWN"),
                    "score_type": data.get("start_score", 301),
                    "players": data.get("num_players", 1),
                    "current_round": data.get("current_player", 0) + 1,
                    "full_data": data
                }
                save_list.append(info)
        except:
            continue

    save_list.sort(key=lambda x: x["filename"], reverse=True)
    return save_list

def load_specific_save(filename):
    filepath = os.path.join(SAVES_DIR, filename)
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Błąd odczytu: {e}")
        return None
    
    
def delete_save_file(filename):
    """Usuwa wskazany plik zapisu."""
    filepath = os.path.join(SAVES_DIR, filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"Usunięto stary zapis: {filename}")
            return True
        except Exception as e:
            print(f"Nie udało się usunąć pliku {filename}: {e}")
            return False
    return False