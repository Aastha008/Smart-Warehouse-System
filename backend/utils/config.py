import yaml
from pathlib import Path
import os
from functools import lru_cache

class Config:
    def __init__(self):
        self.config = {}
        pass

@lru_cache()
def get_config():
    return Config()
