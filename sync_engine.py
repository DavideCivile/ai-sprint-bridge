import logging
import asyncio
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime
from browser_manager import browser_manager
from file_transfer import file_transfer_manager
from database import db_manager, LogEntry
from settings import settings_manager
from pathlib import Path

logger = logging.getLogger(__name__)

class SyncEngine:
    """Main synchronization engine for ChatGPT and Claude."""
    
    def __init__(self):
        self.is_syncing = False
        self.is_paused = False
        self.manual_mode = False
        self.is_stopped = False
        self.sync_count = 0
        self.loop_count = 0
        self.chatgpt_page_id = "chatgpt"
        self.claude_page_id = "claude"
        self.chatgpt_last_message = None
        self.claude_last_message = None
        self.anti_loop_limit = settings_manager.get_anti_loop_limit()
        self.sync_interval = settings_manager.get_sync_interval()
        self.message_hashes = set()
    
    async def initialize(self) -> bool:
        """Initialize sync engine and browser."""
        try:
            logger.info("Initializing Sync Engine...")
            success = await browser_manager.initialize()
            if not success:
                logger.error("Failed to initialize browser")
                return False
            logger.info("Sync Engine initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing sync engine: {e}")
            return False
    
    async def start_sync(self, chatgpt_url: str, claude_url: str) -> bool:
        """Start synchronization."""
        try:
            self.is_syncing = True
            self.is_stopped = False
            logger.info("Starting synchronization...")
            
            chatgpt_page = await browser_manager.open_page(chatgpt_url, self.chatgpt_page_id)
            claude_page = await browser_manager.open_page(claude_url, self.claude_page_id)
            
            if not chatgpt_page or not claude_page:
                logger.error("Failed to open pages")
                self.is_syncing = False
                return False
            
            logger.info("Both pages opened successfully")
            return True
        except Exception as e:
            logger.error(f"Error starting sync: {e}")
            self.is_syncing = False
            return False
    
    async def stop_sync(self) -> bool:
        """Stop synchronization completely."""
        try:
            logger.info("Stopping synchronization...")
            self.is_syncing = False
            self.is_paused = False
            self.is_stopped = True
            
            await browser_manager.close_browser()
            logger.info("Synchronization stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping sync: {e}")
            return False
    
    async def pause_sync(self) -> None:
        """Pause synchronization."""
        self.is_paused = True
        logger.info("Synchronization paused")
    
    async def resume_sync(self) -> None:
        """Resume synchronization."""
        self.is_paused = False
        logger.info("Synchronization resumed")
    
    def toggle_manual_mode(self, enabled: bool) -> None:
        """Toggle manual mode."""
        self.manual_mode = enabled
        logger.info(f"Manual mode: {enabled}")
    
    def calculate_message_hash(self, message: str) -> str:
        """Calculate hash of message for deduplication."""
        return hashlib.sha256(message.encode()).hexdigest()
    
    async def get_claude_messages(self) -> List[str]:
        """Get recent messages from Claude."""
        try:
            page = await browser_manager.get_page(self.claude_page_id)
            if not page:
                return []
            
            messages = []
            try:
                message_elements = await page.query_selector_all('[data-testid="message"]')
                for element in message_elements:
                    text = await element.text_content()
                    if text:
                        messages.append(text.strip())
            except:
                pass
            
            return messages[-5:] if messages else []
        except Exception as e:
            logger.error(f"Error getting Claude messages: {e}")
            return []
    
    async def get_chatgpt_messages(self) -> List[str]:
        """Get recent messages from ChatGPT."""
        try:
            page = await browser_manager.get_page(self.chatgpt_page_id)
            if not page:
                return []
            
            messages = []
            try:
                message_elements = await page.query_selector_all('[data-testid="message"]')
                for element in message_elements:
                    text = await element.text_content()
                    if text:
                        messages.append(text.strip())
            except:
                pass
            
            return messages[-5:] if messages else []
        except Exception as e:
            logger.error(f"Error getting ChatGPT messages: {e}")
            return []
    
    async def send_message_to_claude(self, message: str) -> bool:
        """Send a message to Claude."""
        try:
            page = await browser_manager.get_page(self.claude_page_id)
            if not page:
                return False
            
            input_selectors = [
                'textarea[placeholder*="Message"]',
                '[contenteditable="true"]',
                'input[type="text"]'
            ]
            
            for selector in input_selectors:
                try:
                    if await browser_manager.wait_for_selector(self.claude_page_id, selector, 5000):
                        await browser_manager.type_text(self.claude_page_id, selector, message)
                        send_selectors = ['button[aria-label="Send"]', 'button:has-text("Send")']
                        for send_sel in send_selectors:
                            try:
                                await browser_manager.click_element(self.claude_page_id, send_sel)
                                logger.info(f"Message sent to Claude")
                                return True
                            except:
                                pass
                except:
                    pass
            
            return False
        except Exception as e:
            logger.error(f"Error sending message to Claude: {e}")
            return False
    
    async def send_message_to_chatgpt(self, message: str) -> bool:
        """Send a message to ChatGPT."""
        try:
            page = await browser_manager.get_page(self.chatgpt_page_id)
            if not page:
                return False
            
            input_selectors = [
                'textarea[placeholder*="Message"]',
                '[contenteditable="true"]',
                'input[type="text"]'
            ]
            
            for selector in input_selectors:
                try:
                    if await browser_manager.wait_for_selector(self.chatgpt_page_id, selector, 5000):
                        await browser_manager.type_text(self.chatgpt_page_id, selector, message)
                        send_selectors = ['button[aria-label="Send"]', 'button:has-text("Send")']
                        for send_sel in send_selectors:
                            try:
                                await browser_manager.click_element(self.chatgpt_page_id, send_sel)
                                logger.info(f"Message sent to ChatGPT")
                                return True
                            except:
                                pass
                except:
                    pass
            
            return False
        except Exception as e:
            logger.error(f"Error sending message to ChatGPT: {e}")
            return False
    
    async def sync_messages(self, sprint_id: int) -> int:
        """Synchronize messages between both platforms."""
        if self.is_paused or self.is_stopped or not self.is_syncing:
            return 0
        
        try:
            synced_count = 0
            
            claude_msgs = await self.get_claude_messages()
            chatgpt_msgs = await self.get_chatgpt_messages()
            
            for msg in claude_msgs:
                msg_hash = self.calculate_message_hash(msg)
                if msg_hash not in self.message_hashes:
                    self.message_hashes.add(msg_hash)
                    
                    msg_id = db_manager.add_message(sprint_id, "Claude", msg, msg_hash)
                    
                    if msg_id and not self.manual_mode:
                        sent = await self.send_message_to_chatgpt(msg)
                        if sent:
                            db_manager.mark_message_synced(msg_id)
                            synced_count += 1
                            
                            log_entry = LogEntry(
                                timestamp=datetime.now().isoformat(),
                                sender="Claude",
                                receiver="ChatGPT",
                                sprint=sprint_id,
                                message_type="text",
                                content=msg[:100]
                            )
                            db_manager.add_log(log_entry)
            
            for msg in chatgpt_msgs:
                msg_hash = self.calculate_message_hash(msg)
                if msg_hash not in self.message_hashes:
                    self.message_hashes.add(msg_hash)
                    
                    msg_id = db_manager.add_message(sprint_id, "ChatGPT", msg, msg_hash)
                    
                    if msg_id and not self.manual_mode:
                        sent = await self.send_message_to_claude(msg)
                        if sent:
                            db_manager.mark_message_synced(msg_id)
                            synced_count += 1
                            
                            log_entry = LogEntry(
                                timestamp=datetime.now().isoformat(),
                                sender="ChatGPT",
                                receiver="Claude",
                                sprint=sprint_id,
                                message_type="text",
                                content=msg[:100]
                            )
                            db_manager.add_log(log_entry)
            
            self.sync_count += synced_count
            
            if self.sync_count >= self.anti_loop_limit:
                logger.warning(f"Anti-loop limit reached: {self.sync_count}")
                await self.pause_sync()
                return synced_count
            
            return synced_count
        
        except Exception as e:
            logger.error(f"Error syncing messages: {e}")
            return 0
    
    async def sync_files(self, sprint_id: int) -> int:
        """Synchronize files between platforms."""
        if self.is_paused or self.is_stopped or not self.is_syncing:
            return 0
        
        try:
            synced_count = 0
            
            files = file_transfer_manager.get_download_files()
            
            for file_path in files:
                is_valid, msg = file_transfer_manager.validate_file(file_path)
                if not is_valid:
                    logger.warning(f"Invalid file: {file_path} - {msg}")
                    continue
                
                file_info = file_transfer_manager.get_file_info(file_path)
                file_hash = file_info.get("hash")
                
                file_id = db_manager.add_file(
                    sprint_id,
                    "System",
                    file_info.get("name"),
                    file_info.get("size"),
                    file_path,
                    file_hash
                )
                
                if file_id:
                    synced_count += 1
                    log_entry = LogEntry(
                        timestamp=datetime.now().isoformat(),
                        sender="System",
                        receiver="All",
                        sprint=sprint_id,
                        message_type="file",
                        content=f"File detected: {file_info.get('name')}",
                        file_name=file_info.get("name"),
                        file_size=file_info.get("size")
                    )
                    db_manager.add_log(log_entry)
            
            return synced_count
        
        except Exception as e:
            logger.error(f"Error syncing files: {e}")
            return 0
    
    async def continuous_sync(self, sprint_id: int) -> None:
        """Continuously synchronize messages and files."""
        logger.info("Starting continuous sync loop...")
        
        while self.is_syncing and not self.is_stopped:
            if not self.is_paused:
                msg_count = await self.sync_messages(sprint_id)
                file_count = await self.sync_files(sprint_id)
                
                if msg_count > 0 or file_count > 0:
                    logger.info(f"Synced: {msg_count} messages, {file_count} files")
            
            await asyncio.sleep(self.sync_interval)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        return {
            "is_syncing": self.is_syncing,
            "is_paused": self.is_paused,
            "manual_mode": self.manual_mode,
            "sync_count": self.sync_count,
            "anti_loop_limit": self.anti_loop_limit,
            "loop_reached": self.sync_count >= self.anti_loop_limit
        }

sync_engine = SyncEngine()
