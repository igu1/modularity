import os
import shutil
import hashlib
import mimetypes
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from ..logging.logger import CoreLogger
logger = CoreLogger()
class FileHelpers:
    @staticmethod
    def ensure_directory(path: str, mode: int = 0o755) -> bool:
        try:
            os.makedirs(path, mode=mode, exist_ok=True)
            return True
        except OSError as e:
            logger.log("file_ops", f"Failed to create directory {path}: {e}", "error")
            return False
    @staticmethod
    def get_file_size(file_path: str) -> int:
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    @staticmethod
    def file_exists(file_path: str) -> bool:
        return os.path.isfile(file_path)
    @staticmethod
    def directory_exists(dir_path: str) -> bool:
        return os.path.isdir(dir_path)
    @staticmethod
    def get_file_extension(filename: str) -> str:
        return os.path.splitext(filename)[1].lower()
    @staticmethod
    def get_filename_without_extension(filename: str) -> str:
        return os.path.splitext(filename)[0]
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        if not filename:
            return False
        dangerous_patterns = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        return not any(pattern in filename for pattern in dangerous_patterns)
    @staticmethod
    def sanitize_filename(filename: str, replacement: str = '_') -> str:
        if not filename:
            return 'unnamed_file'
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\x00']
        sanitized = filename
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, replacement)
        sanitized = sanitized.strip('. ')
        if not sanitized:
            sanitized = 'unnamed_file'
        return sanitized
    @staticmethod
    def get_mime_type(file_path: str) -> str:
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        mime_type = FileHelpers.get_mime_type(file_path)
        return mime_type.startswith('image/')
    @staticmethod
    def is_text_file(file_path: str) -> bool:
        mime_type = FileHelpers.get_mime_type(file_path)
        return mime_type.startswith('text/') or mime_type in [
            'application/json',
            'application/xml',
            'application/javascript'
        ]
    @staticmethod
    def copy_file(source: str, destination: str) -> bool:
        try:
            dest_dir = os.path.dirname(destination)
            if dest_dir:
                FileHelpers.ensure_directory(dest_dir)
            shutil.copy2(source, destination)
            logger.log("file_ops", f"Copied file from {source} to {destination}", "debug")
            return True
        except Exception as e:
            logger.log("file_ops", f"Failed to copy file from {source} to {destination}: {e}", "error")
            return False
    @staticmethod
    def move_file(source: str, destination: str) -> bool:
        try:
            dest_dir = os.path.dirname(destination)
            if dest_dir:
                FileHelpers.ensure_directory(dest_dir)
            shutil.move(source, destination)
            logger.log("file_ops", f"Moved file from {source} to {destination}", "debug")
            return True
        except Exception as e:
            logger.log("file_ops", f"Failed to move file from {source} to {destination}: {e}", "error")
            return False
    @staticmethod
    def delete_file(file_path: str) -> bool:
        try:
            os.remove(file_path)
            logger.log("file_ops", f"Deleted file: {file_path}", "debug")
            return True
        except Exception as e:
            logger.log("file_ops", f"Failed to delete file {file_path}: {e}", "error")
            return False
    @staticmethod
    def delete_directory(dir_path: str, recursive: bool = False) -> bool:
        try:
            if recursive:
                shutil.rmtree(dir_path)
            else:
                os.rmdir(dir_path)                                    
            logger.log("file_ops", f"Deleted directory: {dir_path} (recursive={recursive})", "debug")
            return True
        except Exception as e:
            logger.log("file_ops", f"Failed to delete directory {dir_path}: {e}", "error")
            return False
    @staticmethod
    def list_files(directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        try:
            if recursive:
                import glob
                pattern_path = os.path.join(directory, "**", pattern)
                return glob.glob(pattern_path, recursive=True)
            else:
                import glob
                pattern_path = os.path.join(directory, pattern)
                return glob.glob(pattern_path)
        except Exception as e:
            logger.log("file_ops", f"Failed to list files in {directory}: {e}", "error")
            return []
    @staticmethod
    def list_directories(directory: str, recursive: bool = False) -> List[str]:
        try:
            if recursive:
                dirs = []
                for root, subdirs, _ in os.walk(directory):
                    for subdir in subdirs:
                        dirs.append(os.path.join(root, subdir))
                return dirs
            else:
                return [os.path.join(directory, d) for d in os.listdir(directory) 
                       if os.path.isdir(os.path.join(directory, d))]
        except Exception as e:
            logger.log("file_ops", f"Failed to list directories in {directory}: {e}", "error")
            return []
    @staticmethod
    def get_directory_size(directory: str) -> int:
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
        except Exception as e:
            logger.log("file_ops", f"Failed to calculate directory size for {directory}: {e}", "error")
        return total_size
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        try:
            hash_obj = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            logger.log("file_ops", f"Failed to calculate hash for {file_path}: {e}", "error")
            return None
    @staticmethod
    def read_file_text(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logger.log("file_ops", f"Failed to read file {file_path}: {e}", "error")
            return None
    @staticmethod
    def write_file_text(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        try:
            dir_path = os.path.dirname(file_path)
            if dir_path:
                FileHelpers.ensure_directory(dir_path)
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            logger.log("file_ops", f"Wrote text to file: {file_path}", "debug")
            return True
        except Exception as e:
            logger.log("file_ops", f"Failed to write file {file_path}: {e}", "error")
            return False
    @staticmethod
    def read_file_binary(file_path: str) -> Optional[bytes]:
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.log("file_ops", f"Failed to read binary file {file_path}: {e}", "error")
            return None
    @staticmethod
    def write_file_binary(file_path: str, content: bytes) -> bool:
        try:
            dir_path = os.path.dirname(file_path)
            if dir_path:
                FileHelpers.ensure_directory(dir_path)
            with open(file_path, 'wb') as f:
                f.write(content)
            logger.log("file_ops", f"Wrote binary to file: {file_path}", "debug")
            return True
        except Exception as e:
            logger.log("file_ops", f"Failed to write binary file {file_path}: {e}", "error")
            return False
    @staticmethod
    def append_file_text(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        try:
            dir_path = os.path.dirname(file_path)
            if dir_path:
                FileHelpers.ensure_directory(dir_path)
            with open(file_path, 'a', encoding=encoding) as f:
                f.write(content)
            logger.log("file_ops", f"Appended text to file: {file_path}", "debug")
            return True
        except Exception as e:
            logger.log("file_ops", f"Failed to append to file {file_path}: {e}", "error")
            return False
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        try:
            stat = os.stat(file_path)
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'size_human': FileHelpers.format_file_size(stat.st_size),
                'extension': FileHelpers.get_file_extension(file_path),
                'mime_type': FileHelpers.get_mime_type(file_path),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'is_file': os.path.isfile(file_path),
                'is_directory': os.path.isdir(file_path),
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK),
                'is_executable': os.access(file_path, os.X_OK)
            }
        except Exception as e:
            logger.log("file_ops", f"Failed to get file info for {file_path}: {e}", "error")
            return {}
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    @staticmethod
    def create_temp_file(content: Union[str, bytes], suffix: str = '.tmp', 
                        prefix: str = 'temp_') -> Optional[str]:
        import tempfile
        try:
            with tempfile.NamedTemporaryFile(mode='w+b', suffix=suffix, prefix=prefix, delete=False) as f:
                if isinstance(content, str):
                    f.write(content.encode('utf-8'))
                else:
                    f.write(content)
                return f.name
        except Exception as e:
            logger.log("file_ops", f"Failed to create temp file: {e}", "error")
            return None
    @staticmethod
    def create_temp_directory(prefix: str = 'temp_dir_') -> Optional[str]:
        import tempfile
        try:
            temp_dir = tempfile.mkdtemp(prefix=prefix)
            return temp_dir
        except Exception as e:
            logger.log("file_ops", f"Failed to create temp directory: {e}", "error")
            return None
