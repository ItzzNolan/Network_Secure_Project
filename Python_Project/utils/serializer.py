# utils/serializer.py

import json
import pickle
import os

class Serializer:

    # -----------------------
    #   SAVE / LOAD JSON
    # -----------------------
    @staticmethod
    def save_json(data, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[JSON] Saved to {path}")

    @staticmethod
    def load_json(path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # -----------------------
    #   SAVE / LOAD PICKLE
    # -----------------------
    @staticmethod
    def save_pickle(data, path):
        with open(path, "wb") as f:
            pickle.dump(data, f)
        print(f"[PICKLE] Saved to {path}")

    @staticmethod
    def load_pickle(path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, "rb") as f:
            return pickle.load(f)

# Example usage:
# Serializer.save_json({"key": "value"}, "data.json")
# data = Serializer.load_json("data.json")
# Serializer.save_pickle(some_object, "data.pkl")
# some_object = Serializer.load_pickle("data.pkl")
