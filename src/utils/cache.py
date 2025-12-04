# src/utils/cache.py
import pickle
import hashlib
import os
from datetime import datetime, timedelta

class ResearchCache:
    def __init__(self, cache_dir: str = "./data/cache", ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, topic: str) -> str:
        return hashlib.md5(topic.encode()).hexdigest()
    
    def get(self, topic: str):
        cache_key = self._get_cache_key(topic)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        if os.path.exists(cache_file):
            # Check TTL
            file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - file_time < self.ttl:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        return None
    
    def set(self, topic: str, data):
        cache_key = self._get_cache_key(topic)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)