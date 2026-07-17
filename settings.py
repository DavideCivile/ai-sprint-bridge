import json
import os
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class SettingsManager:
    """Manages application settings and configuration."""
    
    CONFIG_DIR = Path("config")
    SETTINGS_FILE = CONFIG_DIR / "settings.json"
    
    DEFAULT_SETTINGS = {
        "sprints": [
            {
                "id": 1,
                "name": "Sprint 1",
                "chatgpt_url": "",
                "claude_url": "",
                "date": "",
                "notes": ""
            }
        ],
        "anti_loop_limit": 5,
        "sync_interval": 2,
        "max_file_size_mb": 100,
        "supported_formats": ["zip", "pdf", "docx", "txt", "xlsx", "png", "jpg"],
        "current_sprint": 1,
        "auto_sync_enabled": False,
        "manual_mode_enabled": False,
        "pause_enabled": False
    }
    
    def __init__(self):
        """Initialize settings manager."""
        self.config_dir = Path("config")
        self.settings_file = self.config_dir / "settings.json"
        self.settings: Dict[str, Any] = {}
        
        self._ensure_directories()
        self._load_settings()
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            "config",
            "storage/temp_files",
            "logs",
            "downloads",
            "database"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {directory}")
    
    def _load_settings(self) -> None:
        """Load settings from JSON file or create default."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                logger.info(f"Settings loaded from {self.settings_file}")
            except json.JSONDecodeError:
                logger.warning("Invalid settings.json, using defaults")
                self.settings = self.DEFAULT_SETTINGS.copy()
                self._save_settings()
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
                self.settings = self.DEFAULT_SETTINGS.copy()
        else:
            self.settings = self.DEFAULT_SETTINGS.copy()
            self._save_settings()
            logger.info("Default settings created")
    
    def _save_settings(self) -> None:
        """Save settings to JSON file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Settings saved to {self.settings_file}")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a setting value."""
        self.settings[key] = value
        self._save_settings()
    
    def get_sprint(self, sprint_id: int) -> Dict[str, Any]:
        """Get a specific sprint configuration."""
        sprints = self.settings.get("sprints", [])
        for sprint in sprints:
            if sprint.get("id") == sprint_id:
                return sprint
        return {}
    
    def update_sprint(self, sprint_id: int, sprint_data: Dict[str, Any]) -> None:
        """Update a sprint configuration."""
        sprints = self.settings.get("sprints", [])
        for i, sprint in enumerate(sprints):
            if sprint.get("id") == sprint_id:
                sprints[i].update(sprint_data)
                self._save_settings()
                logger.info(f"Sprint {sprint_id} updated")
                return
        logger.warning(f"Sprint {sprint_id} not found")
    
    def add_sprint(self, sprint_data: Dict[str, Any]) -> int:
        """Add a new sprint and return its ID."""
        sprints = self.settings.get("sprints", [])
        
        if not sprints:
            new_id = 1
        else:
            new_id = max(sprint.get("id", 0) for sprint in sprints) + 1
        
        sprint_data["id"] = new_id
        sprints.append(sprint_data)
        self.settings["sprints"] = sprints
        self._save_settings()
        logger.info(f"Sprint {new_id} added")
        return new_id
    
    def remove_sprint(self, sprint_id: int) -> bool:
        """Remove a sprint."""
        sprints = self.settings.get("sprints", [])
        original_length = len(sprints)
        self.settings["sprints"] = [s for s in sprints if s.get("id") != sprint_id]
        
        if len(self.settings["sprints"]) < original_length:
            self._save_settings()
            logger.info(f"Sprint {sprint_id} removed")
            return True
        
        logger.warning(f"Sprint {sprint_id} not found")
        return False
    
    def get_all_sprints(self) -> List[Dict[str, Any]]:
        """Get all sprints."""
        return self.settings.get("sprints", [])
    
    def set_current_sprint(self, sprint_id: int) -> None:
        """Set the current active sprint."""
        self.settings["current_sprint"] = sprint_id
        self._save_settings()
        logger.info(f"Current sprint set to {sprint_id}")
    
    def get_current_sprint(self) -> int:
        """Get the current active sprint ID."""
        return self.settings.get("current_sprint", 1)
    
    def get_anti_loop_limit(self) -> int:
        """Get anti-loop limit."""
        return self.settings.get("anti_loop_limit", 5)
    
    def set_anti_loop_limit(self, limit: int) -> None:
        """Set anti-loop limit."""
        self.settings["anti_loop_limit"] = limit
        self._save_settings()
    
    def get_sync_interval(self) -> int:
        """Get sync interval in seconds."""
        return self.settings.get("sync_interval", 2)
    
    def set_sync_interval(self, interval: int) -> None:
        """Set sync interval in seconds."""
        self.settings["sync_interval"] = interval
        self._save_settings()
    
    def reset_to_defaults(self) -> None:
        """Reset settings to defaults."""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self._save_settings()
        logger.info("Settings reset to defaults")


settings_manager = SettingsManager()
