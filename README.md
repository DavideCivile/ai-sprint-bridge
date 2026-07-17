# AI Sprint Bridge

Eine lokale Windows Desktop-Anwendung, die Ihre bestehenden ChatGPT- und Claude-Webchats verbindet.

## 🎯 Ziel

Automatische Synchronisierung von Nachrichten, Prompts und Dateien zwischen ChatGPT und Claude ohne manuelle Kopier-Paste-Vorgänge.

## ✨ Funktionen

- ✅ Multi-Sprint-Management (bis zu 5 Sprints)
- ✅ Automatische Nachrichtensynchronisierung
- ✅ Intelligente Dateiaustausch (ZIP, PDF, DOCX, TXT, XLSX, PNG, JPG)
- ✅ Pause/Fortsetzen-Funktionalität
- ✅ Handmodus für manuelle Kontrolle
- ✅ Notfallstop-Funktion
- ✅ Anti-Loop-Schutz
- ✅ SQLite-Logging und Dashboard
- ✅ Browser-Automatisierung via Playwright
- ✅ Moderne CustomTkinter GUI

## 🛠️ Systemanforderungen

- **OS:** Windows 11
- **Python:** 3.12.8 (64-bit)
- **RAM:** Mindestens 4GB
- **Festplatte:** 500MB frei

## 📦 Installation

### 1. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 2. Playwright Chromium installieren

```bash
playwright install chromium
```

### 3. Anwendung starten

```bash
python main.py
```

## 📁 Projektstruktur

```
ai_sprint_bridge/
├── main.py                 # Haupteinstiegspunkt
├── gui.py                  # CustomTkinter GUI
├── sync_engine.py          # Synchronisierungs-Engine
├── browser_manager.py      # Playwright Browser-Manager
├── file_transfer.py        # Dateiübertragungslogik
├── sprint_manager.py       # Sprint-Management
├── database.py             # SQLite Datenbank
├── settings.py             # Konfigurationsmanager
├── config/
│   └── settings.json       # Benutzerkonfiguration
├── storage/
│   └── temp_files/         # Temporäre Dateien
├── logs/
│   ├── app.log             # Anwendungs-Log
│   └── app.db              # SQLite Log-Datenbank
├── downloads/              # Heruntergeladene Dateien
└── database/
    └── app.db              # Hauptdatenbank
```

## 🚀 Erste Schritte

1. **Starten Sie die Anwendung**
   ```bash
   python main.py
   ```

2. **Konfigurieren Sie Ihre Sprints:**
   - Geben Sie ChatGPT URL ein
   - Geben Sie Claude URL ein
   - Speichern Sie pro Sprint

3. **Aktivieren Sie die Synchronisierung**
   - Klicken Sie auf "START"
   - Überwachen Sie das Dashboard
   - Meldungen werden automatisch weitergeleitet

4. **Dateiaustausch:**
   - Dateien werden automatisch erkannt
   - Von Claude zu ChatGPT und umgekehrt
   - Unterstützte Formate: ZIP, PDF, DOCX, TXT, XLSX, PNG, JPG

## 🎮 Steuerelemente

| Schaltfläche | Funktion |
|---|---|
| **START** | Synchronisierung aktivieren |
| **PAUSE** | Synchronisierung pausieren |
| **FORTSETZEN** | Synchronisierung fortsetzen |
| **HANDMODUS** | Manuelle Nachrichtenfreigabe |
| **NOODSTOP** | Alle Prozesse beenden |

## ⚙️ Konfiguration

Die Anwendung speichert Einstellungen in `config/settings.json`:

```json
{
  "sprints": [
    {
      "id": 1,
      "name": "Sprint 1",
      "chatgpt_url": "https://chatgpt.com/c/...",
      "claude_url": "https://claude.ai/chat/...",
      "date": "2024-01-01",
      "notes": "Initial Sprint"
    }
  ],
  "anti_loop_limit": 5,
  "sync_interval": 2,
  "max_file_size_mb": 100
}
```

## 🔒 Sicherheitshinweise

- ✅ Keine API-Keys erforderlich
- ✅ Verwendet vorhandene Browser-Sitzungen
- ✅ Lokal auf Windows 11 ausgeführt
- ✅ SQLite-Verschlüsselung möglich
- ✅ Anti-Loop-Schutz integriert

## 📊 Logging

Alle Aktivitäten werden protokolliert:

- **app.log:** Textbasierte Protokolle
- **logs/app.db:** SQLite-Datenbank mit detaillierten Logs

## 🐛 Troubleshooting

**Problem:** Playwright findet keinen Browser
```bash
playwright install chromium
```

**Problem:** Dateien werden nicht hochgeladen
- Überprüfen Sie Dateigröße (max 100MB)
- Prüfen Sie Unterstützung des Dateiformats

**Problem:** Synchronisierung funktioniert nicht
- Überprüfen Sie URLs in den Sprint-Einstellungen
- Stellen Sie sicher, dass Sie in ChatGPT und Claude angemeldet sind
- Prüfen Sie die Logs

## 📝 Lizenz

MIT License - Frei verwendbar

## 👨‍💻 Entwicklung

Entwickelt mit:
- Python 3.12.8
- CustomTkinter
- Playwright
- SQLite

---

**Version:** 1.0.0
