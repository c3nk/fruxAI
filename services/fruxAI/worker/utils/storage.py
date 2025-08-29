import os
import hashlib
import aiofiles
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self, base_path: str = "/app/storage"):
        self.base_path = Path(base_path)
        self.pdfs_path = self.base_path / "pdfs"
        self.htmls_path = self.base_path / "htmls"
        self.metadata_path = self.base_path / "metadata"

        # Create directories if they don't exist
        self.pdfs_path.mkdir(parents=True, exist_ok=True)
        self.htmls_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)

    def _get_file_hash(self, url: str) -> str:
        """Generate a hash for the URL to use as filename"""
        return hashlib.md5(url.encode()).hexdigest()

    def _get_content_directory(self, url: str, crawl_date: Optional[datetime] = None) -> Path:
        """Get the directory path for storing content based on URL domain and date"""
        if crawl_date is None:
            crawl_date = datetime.now()

        parsed = urlparse(url)
        domain = parsed.netloc.replace('.', '_')
        date_str = crawl_date.strftime("%Y/%m/%d")

        return Path(f"{domain}/{date_str}")

    async def save_content(self, content: bytes, url: str, content_type: str, crawl_date: Optional[datetime] = None) -> str:
        """Save content to appropriate storage location"""
        try:
            # Determine storage path based on content type
            if content_type.startswith('application/pdf'):
                base_dir = self.pdfs_path
                extension = '.pdf'
            elif content_type.startswith('text/html'):
                base_dir = self.htmls_path
                extension = '.html'
            else:
                # For other content types, save to metadata directory
                base_dir = self.metadata_path
                extension = self._guess_extension(content_type)

            # Create content directory
            content_dir = base_dir / self._get_content_directory(url, crawl_date)
            content_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            file_hash = self._get_file_hash(url)
            filename = f"{file_hash}{extension}"
            file_path = content_dir / filename

            # Save content
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)

            # Return relative path from storage root
            relative_path = file_path.relative_to(self.base_path)

            logger.info(f"Content saved: {url} -> {relative_path}")
            return str(relative_path)

        except Exception as e:
            logger.error(f"Failed to save content for {url}: {e}")
            raise

    async def save_metadata_file(self, metadata: dict, url: str, crawl_date: Optional[datetime] = None) -> str:
        """Save metadata as JSON file"""
        try:
            content_dir = self.metadata_path / self._get_content_directory(url, crawl_date)
            content_dir.mkdir(parents=True, exist_ok=True)

            file_hash = self._get_file_hash(url)
            filename = f"{file_hash}_metadata.json"
            file_path = content_dir / filename

            import json
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(metadata, indent=2, ensure_ascii=False, default=str))

            relative_path = file_path.relative_to(self.base_path)
            logger.info(f"Metadata saved: {url} -> {relative_path}")
            return str(relative_path)

        except Exception as e:
            logger.error(f"Failed to save metadata for {url}: {e}")
            raise

    async def read_content(self, relative_path: str) -> Optional[bytes]:
        """Read content from storage"""
        try:
            file_path = self.base_path / relative_path
            if not file_path.exists():
                return None

            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Failed to read content from {relative_path}: {e}")
            return None

    async def get_file_info(self, relative_path: str) -> Optional[dict]:
        """Get file information"""
        try:
            file_path = self.base_path / relative_path
            if not file_path.exists():
                return None

            stat = file_path.stat()
            return {
                'path': str(relative_path),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'exists': True
            }
        except Exception as e:
            logger.error(f"Failed to get file info for {relative_path}: {e}")
            return None

    async def cleanup_old_files(self, days_to_keep: int = 30):
        """Clean up files older than specified days"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            deleted_count = 0

            for root_dir in [self.pdfs_path, self.htmls_path, self.metadata_path]:
                if root_dir.exists():
                    for file_path in root_dir.rglob('*'):
                        if file_path.is_file() and file_path.stat().st_mtime < cutoff_date:
                            file_path.unlink()
                            deleted_count += 1

            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup old files: {e}")
            return 0

    def _guess_extension(self, content_type: str) -> str:
        """Guess file extension based on content type"""
        content_type_map = {
            'text/plain': '.txt',
            'text/csv': '.csv',
            'application/json': '.json',
            'application/xml': '.xml',
            'text/xml': '.xml',
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'application/zip': '.zip',
            'application/pdf': '.pdf',  # fallback
        }
        return content_type_map.get(content_type, '.bin')

    def get_storage_stats(self) -> dict:
        """Get storage statistics"""
        try:
            total_size = 0
            file_counts = {'pdfs': 0, 'htmls': 0, 'metadata': 0}

            # Count PDFs
            for file_path in self.pdfs_path.rglob('*'):
                if file_path.is_file():
                    file_counts['pdfs'] += 1
                    total_size += file_path.stat().st_size

            # Count HTMLs
            for file_path in self.htmls_path.rglob('*'):
                if file_path.is_file():
                    file_counts['htmls'] += 1
                    total_size += file_path.stat().st_size

            # Count metadata files
            for file_path in self.metadata_path.rglob('*'):
                if file_path.is_file():
                    file_counts['metadata'] += 1
                    total_size += file_path.stat().st_size

            return {
                'total_files': sum(file_counts.values()),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'file_counts': file_counts,
                'pdfs_size_mb': sum(f.stat().st_size for f in self.pdfs_path.rglob('*') if f.is_file()) / (1024 * 1024),
                'htmls_size_mb': sum(f.stat().st_size for f in self.htmls_path.rglob('*') if f.is_file()) / (1024 * 1024),
                'metadata_size_mb': sum(f.stat().st_size for f in self.metadata_path.rglob('*') if f.is_file()) / (1024 * 1024),
            }
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {'error': str(e)}
