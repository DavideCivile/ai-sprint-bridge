import logging
import hashlib
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
import os

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = ["zip", "pdf", "docx", "txt", "xlsx", "png", "jpg"]
MAX_FILE_SIZE_MB = 100

class FileTransferManager:
    """Manages file transfers between ChatGPT and Claude."""
    
    def __init__(self, download_dir: str = "downloads", temp_dir: str = "storage/temp_files"):
        self.download_dir = Path(download_dir)
        self.temp_dir = Path(temp_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file."""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash: {e}")
            return ""
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported."""
        try:
            file_ext = Path(file_path).suffix.lower().lstrip(".")
            return file_ext in SUPPORTED_FORMATS
        except Exception as e:
            logger.error(f"Error checking format: {e}")
            return False
    
    def is_valid_size(self, file_path: str) -> bool:
        """Check if file size is within limits."""
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            return file_size_mb <= MAX_FILE_SIZE_MB
        except Exception as e:
            logger.error(f"Error checking file size: {e}")
            return False
    
    def validate_file(self, file_path: str) -> Tuple[bool, str]:
        """Validate file for transfer."""
        if not Path(file_path).exists():
            return False, "File not found"
        
        if not self.is_supported_format(file_path):
            return False, f"Format not supported. Allowed: {', '.join(SUPPORTED_FORMATS)}"
        
        if not self.is_valid_size(file_path):
            return False, f"File size exceeds {MAX_FILE_SIZE_MB}MB limit"
        
        return True, "OK"
    
    def get_file_info(self, file_path: str) -> dict:
        """Get detailed file information."""
        try:
            path = Path(file_path)
            return {
                "name": path.name,
                "size": os.path.getsize(file_path),
                "extension": path.suffix.lower().lstrip("."),
                "hash": self.calculate_file_hash(file_path),
                "full_path": str(path.absolute())
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return {}
    
    def copy_to_temp(self, source_file: str) -> Optional[str]:
        """Copy file to temporary storage."""
        try:
            source_path = Path(source_file)
            if not source_path.exists():
                logger.error(f"Source file not found: {source_file}")
                return None
            
            dest_path = self.temp_dir / source_path.name
            shutil.copy2(source_file, dest_path)
            logger.info(f"File copied to temp: {dest_path}")
            return str(dest_path)
        except Exception as e:
            logger.error(f"Error copying to temp: {e}")
            return None
    
    def copy_to_download(self, source_file: str) -> Optional[str]:
        """Copy file to download directory."""
        try:
            source_path = Path(source_file)
            if not source_path.exists():
                logger.error(f"Source file not found: {source_file}")
                return None
            
            dest_path = self.download_dir / source_path.name
            shutil.copy2(source_file, dest_path)
            logger.info(f"File copied to downloads: {dest_path}")
            return str(dest_path)
        except Exception as e:
            logger.error(f"Error copying to downloads: {e}")
            return None
    
    def move_file(self, source: str, destination: str) -> bool:
        """Move file from source to destination."""
        try:
            shutil.move(source, destination)
            logger.info(f"File moved: {source} -> {destination}")
            return True
        except Exception as e:
            logger.error(f"Error moving file: {e}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def get_temp_files(self) -> List[str]:
        """Get all files in temporary directory."""
        try:
            files = [str(f) for f in self.temp_dir.glob("*") if f.is_file()]
            return files
        except Exception as e:
            logger.error(f"Error getting temp files: {e}")
            return []
    
    def get_download_files(self) -> List[str]:
        """Get all files in download directory."""
        try:
            files = [str(f) for f in self.download_dir.glob("*") if f.is_file()]
            return files
        except Exception as e:
            logger.error(f"Error getting download files: {e}")
            return []
    
    def cleanup_temp_files(self) -> int:
        """Delete all temporary files."""
        try:
            count = 0
            for file in self.temp_dir.glob("*"):
                if file.is_file():
                    file.unlink()
                    count += 1
            logger.info(f"Cleaned up {count} temporary files")
            return count
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")
            return 0

file_transfer_manager = FileTransferManager()
