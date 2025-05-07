import json
import os.path

from xcsp.utils.paths import get_cache_dir
from loguru import logger

class Cache:
    @staticmethod
    def create_from_file_or_default():
        cache_file = get_cache_dir() / "solver_cache.json"
        logger.info(f"Reading cache from {cache_file}")
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        else:
            return dict()
    @staticmethod
    def save_cache(cache):
        cache_file = get_cache_dir() / "solver_cache.json"
        with open(cache_file, 'w') as f:
            json.dump(cache, f)

CACHE = Cache.create_from_file_or_default()
