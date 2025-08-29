import asyncio
import aiohttp
import aiofiles
import os
import time
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from parsers.pdf_parser import PDFParser
from parsers.html_parser import HTMLParser
from utils.storage import StorageManager
from utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self, metrics=None, storage_path: str = None):
        self.metrics = metrics
        self.storage_path = storage_path or "/app/storage"
        self.session: Optional[aiohttp.ClientSession] = None
        self.storage_manager = StorageManager(self.storage_path)
        self.pdf_parser = PDFParser()
        self.html_parser = HTMLParser()
        self.rate_limiter = RateLimiter()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'fruxAI/1.0 (+https://github.com/c3nk/fruxAI)'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def process_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Process a crawl job"""
        start_time = time.time()
        url = job['url']
        job_id = job['job_id']

        logger.info(f"Starting crawl for job {job_id}: {url}")

        try:
            # Initialize session if not exists
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers={
                        'User-Agent': 'fruxAI/1.0 (+https://github.com/c3nk/fruxAI)'
                    }
                )

            # Check robots.txt if required
            if job.get('respect_robots', True):
                if not await self._check_robots_txt(url):
                    logger.info(f"Robots.txt disallows crawling: {url}")
                    return {
                        'status': 'blocked',
                        'url': url,
                        'error': 'Blocked by robots.txt'
                    }

            # Apply rate limiting
            await self.rate_limiter.wait_if_needed(url)

            # Fetch the content
            content, response_info = await self._fetch_url(url)

            if not content:
                return {
                    'status': 'failed',
                    'url': url,
                    'error': 'Failed to fetch content'
                }

            # Save content to storage
            local_path = await self.storage_manager.save_content(
                content, url, response_info['content_type']
            )

            # Extract metadata based on content type
            metadata = await self._extract_metadata(
                content, url, response_info, local_path
            )

            # If HTML and crawl_type is full, extract links
            links = []
            if response_info['content_type'].startswith('text/html') and job.get('crawl_type') == 'full':
                links = await self._extract_links(content, url, job.get('max_depth', 2))

            processing_time = time.time() - start_time

            result = {
                'status': 'completed',
                'url': url,
                'metadata': metadata,
                'local_path': local_path,
                'processing_time': processing_time,
                'links_found': len(links) if links else 0
            }

            # Update metrics
            if self.metrics:
                await self.metrics.record_crawl_success(processing_time, len(content))

            logger.info(f"Completed crawl for {url} in {processing_time:.2f}s")
            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Failed to crawl {url}: {e}")

            if self.metrics:
                await self.metrics.record_crawl_failure()

            return {
                'status': 'failed',
                'url': url,
                'error': str(e),
                'processing_time': processing_time
            }

    async def _fetch_url(self, url: str) -> tuple[bytes, Dict[str, Any]]:
        """Fetch URL content"""
        async with self.session.get(url, timeout=30) as response:
            content = await response.read()

            return content, {
                'status_code': response.status,
                'content_type': response.headers.get('content-type', ''),
                'content_length': len(content),
                'response_time': response.elapsed.total_seconds() if hasattr(response, 'elapsed') else 0
            }

    async def _check_robots_txt(self, url: str) -> bool:
        """Check if crawling is allowed by robots.txt"""
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

            async with self.session.get(robots_url) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    rp = RobotFileParser()
                    rp.parse(robots_content.split('\n'))
                    return rp.can_fetch('*', url)
                else:
                    # If robots.txt doesn't exist, assume crawling is allowed
                    return True
        except Exception as e:
            logger.warning(f"Failed to check robots.txt for {url}: {e}")
            return True  # Default to allowing if we can't check

    async def _extract_metadata(self, content: bytes, url: str, response_info: Dict[str, Any], local_path: str) -> Dict[str, Any]:
        """Extract metadata from content"""
        metadata = {
            'url': url,
            'content_type': response_info['content_type'],
            'file_size': response_info['content_length'],
            'response_time': response_info['response_time'],
            'status_code': response_info['status_code'],
            'local_file_path': local_path
        }

        try:
            if response_info['content_type'].startswith('application/pdf'):
                pdf_metadata = await self.pdf_parser.extract_metadata(content)
                metadata.update(pdf_metadata)
            elif response_info['content_type'].startswith('text/html'):
                html_metadata = await self.html_parser.extract_metadata(content, url)
                metadata.update(html_metadata)
        except Exception as e:
            logger.error(f"Failed to extract metadata from {url}: {e}")

        return metadata

    async def _extract_links(self, content: bytes, base_url: str, max_depth: int) -> list[str]:
        """Extract links from HTML content"""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            links = []

            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(base_url, href)

                # Filter out non-HTTP URLs and fragments
                if absolute_url.startswith(('http://', 'https://')) and '#' not in absolute_url:
                    links.append(absolute_url)

            # Remove duplicates while preserving order
            seen = set()
            unique_links = []
            for link in links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append(link)

            return unique_links[:100]  # Limit to prevent explosion
        except Exception as e:
            logger.error(f"Failed to extract links from {base_url}: {e}")
            return []
