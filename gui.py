import customtkinter as ctk
import logging
import asyncio
from typing import Optional
from datetime import datetime
from settings import settings_manager
from sprint_manager import sprint_manager
from sync_engine import sync_engine
from database import db_manager

logger = logging.getLogger(__name__)

class AISprintBridgeGUI:
    """Main GUI application for AI Sprint Bridge."""
    
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("AI Sprint Bridge")
        self.app.geometry("1400x900")
        self.app.resizable(True, True)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.app.grid_rowconfigure(0, weight=1)
        self.app.grid_columnconfigure(0, weight=1)
        
        self.current_sprint_id = settings_manager.get_current_sprint()
        self.sync_task: Optional[asyncio.Task] = None
        
        self._create_widgets()
        self._update_dashboard()
        self._start_dashboard_update()
    
    def _create_widgets(self) -> None:
        """Create all GUI widgets."""
        main_container = ctk.CTkFrame(self.app)
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        self._create_header(main_container)
        
        body_frame = ctk.CTkFrame(main_container)
        body_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        body_frame.grid_rowconfigure(0, weight=1)
        body_frame.grid_columnconfigure(0, weight=1)
        body_frame.grid_columnconfigure(1, weight=1)
        
        self._create_settings_panel(body_frame)
        self._create_dashboard_panel(body_frame)
        
        self._create_controls_panel(main_container)
    
    def _create_header(self, parent: ctk.CTkFrame) -> None:
        """Create header section."""
        header = ctk.CTkFrame(parent, fg_color="#1f1f1f")
        header.grid(row=0, column=0, sticky="ew", pady=10)
        header.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(
            header,
            text="🚀 AI Sprint Bridge",
            font=("Arial", 28, "bold")
        )
        title.grid(row=0, column=0, padx=20, pady=10)
        
        subtitle = ctk.CTkLabel(
            header,
            text="Automated synchronization between ChatGPT and Claude",
            font=("Arial", 12),
            text_color="gray"
        )
        subtitle.grid(row=1, column=0, padx=20, pady=(0, 10))
    
    def _create_settings_panel(self, parent: ctk.CTkFrame) -> None:
        """Create settings panel on the left."""
        settings_frame = ctk.CTkFrame(parent)
        settings_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        settings_frame.grid_rowconfigure(5, weight=1)
        
        sprint_label = ctk.CTkLabel(
            settings_frame,
            text="Sprint Selection",
            font=("Arial", 14, "bold")
        )
        sprint_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        sprints = sprint_manager.get_all_sprints()
        sprint_names = [f"{s['name']}" for s in sprints]
        
        self.sprint_combo = ctk.CTkComboBox(
            settings_frame,
            values=sprint_names,
            command=self._on_sprint_changed
        )
        self.sprint_combo.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        self.sprint_combo.set(sprint_names[0] if sprint_names else "No Sprints")
        
        details_label = ctk.CTkLabel(
            settings_frame,
            text="Sprint Details",
            font=("Arial", 14, "bold")
        )
        details_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        ctk.CTkLabel(settings_frame, text="ChatGPT URL:").grid(row=3, column=0, sticky="w")
        self.chatgpt_entry = ctk.CTkEntry(settings_frame, width=300)
        self.chatgpt_entry.grid(row=3, column=1, sticky="ew", pady=5)
        
        ctk.CTkLabel(settings_frame, text="Claude URL:").grid(row=4, column=0, sticky="w")
        self.claude_entry = ctk.CTkEntry(settings_frame, width=300)
        self.claude_entry.grid(row=4, column=1, sticky="ew", pady=5)
        
        ctk.CTkLabel(settings_frame, text="Notes:").grid(row=5, column=0, sticky="nw", pady=5)
        self.notes_text = ctk.CTkTextbox(settings_frame, height=100, width=300)
        self.notes_text.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)
        
        ctk.CTkLabel(settings_frame, text="Anti-Loop Limit:").grid(row=7, column=0, sticky="w", pady=10)
        self.anti_loop_var = ctk.StringVar(value=str(settings_manager.get_anti_loop_limit()))
        self.anti_loop_combo = ctk.CTkComboBox(
            settings_frame,
            values=["5", "10", "20", "50"],
            variable=self.anti_loop_var,
            command=self._on_anti_loop_changed
        )
        self.anti_loop_combo.grid(row=7, column=1, sticky="ew", pady=10)
        
        save_btn = ctk.CTkButton(
            settings_frame,
            text="💾 Save Sprint",
            command=self._save_sprint,
            fg_color="#0f7938",
            hover_color="#1a9c4a"
        )
        save_btn.grid(row=8, column=0, columnspan=2, sticky="ew", pady=10)
        
        self._load_sprint_data()
    
    def _create_dashboard_panel(self, parent: ctk.CTkFrame) -> None:
        """Create dashboard panel on the right."""
        dashboard_frame = ctk.CTkFrame(parent)
        dashboard_frame.grid(row=0, column=1, sticky="nsew")
        dashboard_frame.grid_rowconfigure(5, weight=1)
        
        title = ctk.CTkLabel(
            dashboard_frame,
            text="📊 Dashboard",
            font=("Arial", 14, "bold")
        )
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        ctk.CTkLabel(dashboard_frame, text="Sync Status:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w")
        self.status_label = ctk.CTkLabel(
            dashboard_frame,
            text="⭕ STOPPED",
            font=("Arial", 12),
            text_color="red"
        )
        self.status_label.grid(row=1, column=1, sticky="w", padx=10)
        
        ctk.CTkLabel(dashboard_frame, text="Messages Synced:", font=("Arial", 12, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.messages_label = ctk.CTkLabel(
            dashboard_frame,
            text="0",
            font=("Arial", 12),
            text_color="lightblue"
        )
        self.messages_label.grid(row=2, column=1, sticky="w", padx=10)
        
        ctk.CTkLabel(dashboard_frame, text="Files Synced:", font=("Arial", 12, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        self.files_label = ctk.CTkLabel(
            dashboard_frame,
            text="0",
            font=("Arial", 12),
            text_color="lightgreen"
        )
        self.files_label.grid(row=3, column=1, sticky="w", padx=10)
        
        ctk.CTkLabel(dashboard_frame, text="Last Sync:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        self.last_sync_label = ctk.CTkLabel(
            dashboard_frame,
            text="Never",
            font=("Arial", 11),
            text_color="gray"
        )
        self.last_sync_label.grid(row=4, column=1, sticky="w", padx=10)
        
        logs_label = ctk.CTkLabel(
            dashboard_frame,
            text="📋 Recent Logs",
            font=("Arial", 12, "bold")
        )
        logs_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=(20, 10))
        
        self.logs_text = ctk.CTkTextbox(
            dashboard_frame,
            height=300,
            width=400,
            state="disabled"
        )
        self.logs_text.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=5)
    
    def _create_controls_panel(self, parent: ctk.CTkFrame) -> None:
        """Create control buttons panel."""
        controls_frame = ctk.CTkFrame(parent)
        controls_frame.grid(row=2, column=0, sticky="ew", pady=20)
        controls_frame.grid_columnconfigure(5, weight=1)
        
        self.start_btn = ctk.CTkButton(
            controls_frame,
            text="▶️ START",
            command=self._on_start,
            fg_color="#0f7938",
            hover_color="#1a9c4a",
            width=150,
            height=50,
            font=("Arial", 12, "bold")
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.pause_btn = ctk.CTkButton(
            controls_frame,
            text="⏸️ PAUSE",
            command=self._on_pause,
            fg_color="#ff9500",
            hover_color="#ffb340",
            width=150,
            height=50,
            font=("Arial", 12, "bold"),
            state="disabled"
        )
        self.pause_btn.grid(row=0, column=1, padx=5)
        
        self.resume_btn = ctk.CTkButton(
            controls_frame,
            text="▶️ RESUME",
            command=self._on_resume,
            fg_color="#0f7938",
            hover_color="#1a9c4a",
            width=150,
            height=50,
            font=("Arial", 12, "bold"),
            state="disabled"
        )
        self.resume_btn.grid(row=0, column=2, padx=5)
        
        self.manual_btn = ctk.CTkButton(
            controls_frame,
            text="🖱️ MANUAL",
            command=self._on_manual_mode,
            fg_color="#5856d6",
            hover_color="#7c7ae0",
            width=150,
            height=50,
            font=("Arial", 12, "bold")
        )
        self.manual_btn.grid(row=0, column=3, padx=5)
        
        self.stop_btn = ctk.CTkButton(
            controls_frame,
            text="🛑 NOODSTOP",
            command=self._on_emergency_stop,
            fg_color="#d41f1f",
            hover_color="#ff3333",
            width=150,
            height=50,
            font=("Arial", 12, "bold"),
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=4, padx=5)
    
    def _load_sprint_data(self) -> None:
        """Load current sprint data into UI."""
        sprint = sprint_manager.get_current_sprint()
        if sprint:
            self.chatgpt_entry.delete(0, "end")
            self.chatgpt_entry.insert(0, sprint.get("chatgpt_url", ""))
            
            self.claude_entry.delete(0, "end")
            self.claude_entry.insert(0, sprint.get("claude_url", ""))
            
            self.notes_text.delete("1.0", "end")
            self.notes_text.insert("1.0", sprint.get("notes", ""))
    
    def _save_sprint(self) -> None:
        """Save sprint configuration."""
        sprint_manager.update_sprint(
            self.current_sprint_id,
            {
                "chatgpt_url": self.chatgpt_entry.get(),
                "claude_url": self.claude_entry.get(),
                "notes": self.notes_text.get("1.0", "end-1c")
            }
        )
        self._show_notification("✅ Sprint saved successfully")
    
    def _on_sprint_changed(self, value: str) -> None:
        """Handle sprint selection change."""
        sprints = sprint_manager.get_all_sprints()
        for sprint in sprints:
            if sprint["name"] == value:
                self.current_sprint_id = sprint["id"]
                sprint_manager.switch_sprint(self.current_sprint_id)
                self._load_sprint_data()
                self._update_dashboard()
                break
    
    def _on_anti_loop_changed(self, value: str) -> None:
        """Handle anti-loop limit change."""
        try:
            limit = int(value)
            settings_manager.set_anti_loop_limit(limit)
            sync_engine.anti_loop_limit = limit
        except:
            pass
    
    async def _start_sync_async(self) -> None:
        """Start synchronization asynchronously."""
        sprint = sprint_manager.get_current_sprint()
        
        if not sprint.get("chatgpt_url") or not sprint.get("claude_url"):
            self._show_error("❌ Please configure ChatGPT and Claude URLs")
            return
        
        success = await sync_engine.initialize()
        if not success:
            self._show_error("❌ Failed to initialize browser")
            return
        
        success = await sync_engine.start_sync(
            sprint.get("chatgpt_url"),
            sprint.get("claude_url")
        )
        
        if not success:
            self._show_error("❌ Failed to open chat pages")
            return
        
        self.status_label.configure(text="🟢 SYNCING", text_color="lightgreen")
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        
        await sync_engine.continuous_sync(self.current_sprint_id)
    
    def _on_start(self) -> None:
        """Start synchronization."""
        try:
            asyncio.run(self._start_sync_async())
        except Exception as e:
            logger.error(f"Error in _on_start: {e}")
    
    async def _on_pause_async(self) -> None:
        """Pause synchronization."""
        await sync_engine.pause_sync()
        self.status_label.configure(text="🟡 PAUSED", text_color="#ff9500")
        self.pause_btn.configure(state="disabled")
        self.resume_btn.configure(state="normal")
        self._show_notification("⏸️ Synchronization paused")
    
    def _on_pause(self) -> None:
        """Pause button handler."""
        try:
            asyncio.run(self._on_pause_async())
        except Exception as e:
            logger.error(f"Error in _on_pause: {e}")
    
    async def _on_resume_async(self) -> None:
        """Resume synchronization."""
        await sync_engine.resume_sync()
        self.status_label.configure(text="🟢 SYNCING", text_color="lightgreen")
        self.pause_btn.configure(state="normal")
        self.resume_btn.configure(state="disabled")
        self._show_notification("▶️ Synchronization resumed")
    
    def _on_resume(self) -> None:
        """Resume button handler."""
        try:
            asyncio.run(self._on_resume_async())
        except Exception as e:
            logger.error(f"Error in _on_resume: {e}")
    
    def _on_manual_mode(self) -> None:
        """Toggle manual mode."""
        is_manual = not sync_engine.manual_mode
        sync_engine.toggle_manual_mode(is_manual)
        
        if is_manual:
            self.manual_btn.configure(text="🖱️ MANUAL (ON)", fg_color="#7c7ae0")
            self._show_notification("🖱️ Manual mode activated")
        else:
            self.manual_btn.configure(text="🖱️ MANUAL", fg_color="#5856d6")
            self._show_notification("🖱️ Manual mode deactivated")
    
    async def _on_emergency_stop_async(self) -> None:
        """Emergency stop."""
        await sync_engine.stop_sync()
        self.status_label.configure(text="⭕ STOPPED", text_color="red")
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled")
        self.resume_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        self._show_notification("🛑 Emergency stop activated")
    
    def _on_emergency_stop(self) -> None:
        """Emergency stop button handler."""
        try:
            asyncio.run(self._on_emergency_stop_async())
        except Exception as e:
            logger.error(f"Error in _on_emergency_stop: {e}")
    
    def _update_dashboard(self) -> None:
        """Update dashboard information."""
        sprint = sprint_manager.get_current_sprint()
        msg_count = db_manager.get_message_count(self.current_sprint_id)
        file_count = db_manager.get_file_count(self.current_sprint_id)
        
        self.messages_label.configure(text=str(msg_count))
        self.files_label.configure(text=str(file_count))
        
        logs = db_manager.get_logs(self.current_sprint_id, limit=20)
        self.logs_text.configure(state="normal")
        self.logs_text.delete("1.0", "end")
        
        for log in reversed(logs):
            log_line = f"[{log['timestamp']}] {log['sender']} → {log['receiver']}: {log['content'][:50]}...\n"
            self.logs_text.insert("end", log_line)
        
        self.logs_text.configure(state="disabled")
    
    def _start_dashboard_update(self) -> None:
        """Start periodic dashboard updates."""
        self._update_dashboard()
        self.app.after(2000, self._start_dashboard_update)
    
    def _show_notification(self, message: str) -> None:
        """Show a notification message."""
        notification = ctk.CTkLabel(
            self.app,
            text=message,
            fg_color="#0f7938",
            text_color="white",
            pady=10,
            padx=20,
            corner_radius=8
        )
        notification.place(relx=0.5, rely=0.05, anchor="n")
        
        self.app.after(3000, notification.destroy)
    
    def _show_error(self, message: str) -> None:
        """Show an error notification."""
        notification = ctk.CTkLabel(
            self.app,
            text=message,
            fg_color="#d41f1f",
            text_color="white",
            pady=10,
            padx=20,
            corner_radius=8
        )
        notification.place(relx=0.5, rely=0.05, anchor="n")
        
        self.app.after(5000, notification.destroy)
    
    def run(self) -> None:
        """Run the application."""
        logger.info("Starting GUI...")
        self.app.mainloop()
