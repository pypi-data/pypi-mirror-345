import json
import os

def load_emoji():
    # Use os.path.join and dirname to construct the path correctly
    emoji_file_path = os.path.join(os.path.dirname(__file__), "log_emoji.json")
    try:
        with open(emoji_file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to a basic set of emojis if file not found
        print(f"Warning: Could not find {emoji_file_path}, using default emojis")
        return {
            "start": "🚀",
            "processing": "⚙️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "key": "🔑",
            "page": "📄",
            "image": "🖼️",
            "save": "💾",
            "table": "📊",
            "end": "🏁",
            "info": "ℹ️",
            "skip": "⏩",
            "debug": "🐛",
            "pdf": "📄",
            "config": "⚙️",
            "folder": "📁",
            "template": "📝",
            "search": "🔍",
            "model": "🤖",
            "complete": "🏁"
        }

EMOJI = load_emoji()