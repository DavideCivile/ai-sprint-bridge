import logging
import sys
from pathlib import Path
from gui import AISprintBridgeGUI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    try:
        logger.info("="*50)
        logger.info("AI Sprint Bridge - Application Started")
        logger.info("="*50)
        
        # Create GUI
        app = AISprintBridgeGUI()
        
        # Run
        app.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
