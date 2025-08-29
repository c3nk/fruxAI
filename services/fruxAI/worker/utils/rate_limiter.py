import asyncio
import time
import logging
from typing import Dict
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, default_rate: float = 1.0):
        """
        Initialize rate limiter
        :param default_rate: Default requests per second
        """
        self.default_rate = default_rate
        self.last_request: Dict[str, float] = {}
        self.domain_rates: Dict[str, float] = {}

    def set_domain_rate(self, domain: str, rate_per_second: float):
        """Set custom rate limit for a specific domain"""
        self.domain_rates[domain] = rate_per_second
        logger.info(f"Set rate limit for {domain}: {rate_per_second} req/sec")

    def get_domain_rate(self, domain: str) -> float:
        """Get rate limit for a domain"""
        return self.domain_rates.get(domain, self.default_rate)

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return "unknown"

    async def wait_if_needed(self, url: str):
        """Wait if necessary to respect rate limits"""
        domain = self._extract_domain(url)
        rate = self.get_domain_rate(domain)

        if rate <= 0:
            return  # No rate limiting

        now = time.time()
        min_interval = 1.0 / rate

        last_request = self.last_request.get(domain, 0)
        time_since_last = now - last_request

        if time_since_last < min_interval:
            wait_time = min_interval - time_since_last
            logger.debug(f"Rate limiting {domain}: waiting {wait_time:.2f}s")
            await asyncio.sleep(wait_time)

        self.last_request[domain] = time.time()

    def get_wait_time(self, url: str) -> float:
        """Calculate how long to wait before next request"""
        domain = self._extract_domain(url)
        rate = self.get_domain_rate(domain)

        if rate <= 0:
            return 0

        now = time.time()
        min_interval = 1.0 / rate
        last_request = self.last_request.get(domain, 0)
        time_since_last = now - last_request

        if time_since_last < min_interval:
            return min_interval - time_since_last

        return 0

    def reset_domain(self, domain: str):
        """Reset rate limiting for a domain"""
        if domain in self.last_request:
            del self.last_request[domain]
        logger.info(f"Reset rate limiting for {domain}")

    def get_stats(self) -> Dict[str, Dict]:
        """Get rate limiting statistics"""
        stats = {}
        now = time.time()

        for domain in set(list(self.last_request.keys()) + list(self.domain_rates.keys())):
            last_req = self.last_request.get(domain, 0)
            rate = self.get_domain_rate(domain)

            stats[domain] = {
                'rate_per_second': rate,
                'last_request_seconds_ago': now - last_req if last_req > 0 else None,
                'min_interval_seconds': 1.0 / rate if rate > 0 else 0
            }

        return stats
