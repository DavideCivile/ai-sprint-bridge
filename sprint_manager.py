import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from settings import settings_manager

logger = logging.getLogger(__name__)

class SprintManager:
    """Manages sprint configurations and switching."""
    
    def __init__(self):
        self.current_sprint_id = settings_manager.get_current_sprint()
        self.sprints_cache: Dict[int, Dict[str, Any]] = {}
        self._load_sprints()
    
    def _load_sprints(self) -> None:
        """Load all sprints from settings."""
        sprints = settings_manager.get_all_sprints()
        for sprint in sprints:
            self.sprints_cache[sprint.get("id")] = sprint
        logger.info(f"Loaded {len(self.sprints_cache)} sprints")
    
    def get_current_sprint(self) -> Dict[str, Any]:
        """Get current active sprint."""
        sprint = self.sprints_cache.get(self.current_sprint_id)
        if not sprint:
            logger.warning(f"Sprint {self.current_sprint_id} not found")
            return {}
        return sprint
    
    def switch_sprint(self, sprint_id: int) -> bool:
        """Switch to a different sprint."""
        if sprint_id not in self.sprints_cache:
            logger.error(f"Sprint {sprint_id} not found")
            return False
        
        self.current_sprint_id = sprint_id
        settings_manager.set_current_sprint(sprint_id)
        logger.info(f"Switched to sprint {sprint_id}")
        return True
    
    def get_sprint(self, sprint_id: int) -> Dict[str, Any]:
        """Get a specific sprint."""
        return self.sprints_cache.get(sprint_id, {})
    
    def add_sprint(self, name: str, chatgpt_url: str, claude_url: str, notes: str = "") -> int:
        """Add a new sprint."""
        sprint_data = {
            "name": name,
            "chatgpt_url": chatgpt_url,
            "claude_url": claude_url,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "notes": notes
        }
        
        sprint_id = settings_manager.add_sprint(sprint_data)
        self.sprints_cache[sprint_id] = sprint_data
        logger.info(f"Sprint added: {sprint_id}")
        return sprint_id
    
    def update_sprint(self, sprint_id: int, updates: Dict[str, Any]) -> bool:
        """Update a sprint."""
        if sprint_id not in self.sprints_cache:
            logger.error(f"Sprint {sprint_id} not found")
            return False
        
        self.sprints_cache[sprint_id].update(updates)
        settings_manager.update_sprint(sprint_id, updates)
        logger.info(f"Sprint {sprint_id} updated")
        return True
    
    def get_all_sprints(self) -> List[Dict[str, Any]]:
        """Get all sprints."""
        return list(self.sprints_cache.values())
    
    def get_sprint_count(self) -> int:
        """Get total number of sprints."""
        return len(self.sprints_cache)
    
    def remove_sprint(self, sprint_id: int) -> bool:
        """Remove a sprint."""
        if sprint_id not in self.sprints_cache:
            return False
        
        del self.sprints_cache[sprint_id]
        settings_manager.remove_sprint(sprint_id)
        logger.info(f"Sprint {sprint_id} removed")
        return True
    
    def validate_sprint(self, sprint_id: int) -> Tuple[bool, str]:
        """Validate sprint configuration."""
        sprint = self.sprints_cache.get(sprint_id)
        if not sprint:
            return False, "Sprint not found"
        
        if not sprint.get("chatgpt_url"):
            return False, "ChatGPT URL not configured"
        
        if not sprint.get("claude_url"):
            return False, "Claude URL not configured"
        
        return True, "OK"

sprint_manager = SprintManager()
