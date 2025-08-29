import re
import logging
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class HTMLParser:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self.url_pattern = re.compile(r'https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:\w)*)?)?')

    async def extract_metadata(self, content: bytes, url: str) -> Dict[str, Any]:
        """Extract metadata from HTML content"""
        try:
            text_content = content.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(text_content, 'html.parser')

            metadata = {
                'content_type': 'text/html',
                'extracted_text': '',
                'company_info': {}
            }

            # Extract basic metadata
            title = soup.find('title')
            if title:
                metadata['title'] = title.get_text().strip()

            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                metadata['description'] = meta_desc.get('content', '').strip()

            # Extract meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                metadata['keywords'] = meta_keywords.get('content', '').strip()

            # Extract main content text
            text_content = self._extract_main_content(soup)
            metadata['extracted_text'] = text_content

            # Extract company information
            company_info = self._extract_company_info(text_content, soup, url)
            metadata['company_info'] = company_info

            # Extract individual fields for database
            if company_info.get('name'):
                metadata['company_name'] = company_info['name']
            if company_info.get('email'):
                metadata['company_email'] = company_info['email'][0] if isinstance(company_info['email'], list) else company_info['email']
            if company_info.get('phone'):
                metadata['company_phone'] = company_info['phone'][0] if isinstance(company_info['phone'], list) else company_info['phone']
            if company_info.get('website'):
                metadata['company_website'] = company_info['website'][0] if isinstance(company_info['website'], list) else company_info['website']
            if company_info.get('address'):
                metadata['company_address'] = company_info['address']

            logger.info(f"Extracted metadata from HTML: {len(text_content)} chars")
            return metadata

        except Exception as e:
            logger.error(f"Failed to extract HTML metadata: {e}")
            return {
                'content_type': 'text/html',
                'error': str(e),
                'extracted_text': ''
            }

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content text from HTML"""
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()

        # Try to find main content areas
        content_selectors = [
            'main',
            '[role="main"]',
            '.content',
            '.main-content',
            '#content',
            '#main',
            'article',
            '.post',
            '.entry'
        ]

        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
                if len(text) > 100:  # Ensure we have substantial content
                    return text

        # Fallback: get text from body
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)

        # Ultimate fallback: get all text
        return soup.get_text(separator=' ', strip=True)

    def _extract_company_info(self, text: str, soup: BeautifulSoup, base_url: str) -> Dict[str, Any]:
        """Extract company information from HTML content"""
        company_info = {}

        # Extract from meta tags first
        company_info.update(self._extract_from_meta_tags(soup))

        # Extract from text content
        text_company_info = self._extract_company_info_from_text(text)
        company_info.update(text_company_info)

        # Extract from structured data
        structured_data = self._extract_structured_data(soup, base_url)
        if structured_data:
            company_info.update(structured_data)

        return company_info

    def _extract_from_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract company info from meta tags"""
        info = {}

        # Common meta tags for company info
        meta_mappings = {
            'company_name': ['author', 'publisher', 'organization'],
            'company_email': ['email', 'contact'],
            'company_phone': ['phone', 'telephone', 'tel']
        }

        for field, meta_names in meta_mappings.items():
            for meta_name in meta_names:
                meta_tag = soup.find('meta', attrs={'name': meta_name}) or soup.find('meta', attrs={'property': meta_name})
                if meta_tag and meta_tag.get('content'):
                    info[field.replace('company_', '')] = meta_tag['content'].strip()
                    break

        return info

    def _extract_company_info_from_text(self, text: str) -> Dict[str, Any]:
        """Extract company information from text content"""
        company_info = {}

        # Extract emails
        emails = self.email_pattern.findall(text)
        if emails:
            company_info['email'] = list(set(emails))

        # Extract phone numbers
        phones = self.phone_pattern.findall(text)
        if phones:
            formatted_phones = []
            for phone in phones:
                if len(phone) >= 4:
                    formatted_phone = f"({phone[1]}) {phone[2]}-{phone[3]}"
                    if phone[0]:
                        formatted_phone = f"{phone[0]} {formatted_phone}"
                    formatted_phones.append(formatted_phone)
            if formatted_phones:
                company_info['phone'] = list(set(formatted_phones))

        # Extract company name from title or common patterns
        company_name = self._extract_company_name(text)
        if company_name:
            company_info['name'] = company_name

        # Extract address
        address = self._extract_address(text)
        if address:
            company_info['address'] = address

        return company_info

    def _extract_structured_data(self, soup: BeautifulSoup, base_url: str) -> Optional[Dict[str, Any]]:
        """Extract company info from JSON-LD structured data"""
        try:
            script_tags = soup.find_all('script', type='application/ld+json')
            for script in script_tags:
                import json
                data = json.loads(script.string)

                # Handle different types of structured data
                if isinstance(data, dict):
                    return self._parse_structured_data_item(data, base_url)
                elif isinstance(data, list):
                    for item in data:
                        result = self._parse_structured_data_item(item, base_url)
                        if result:
                            return result
        except Exception as e:
            logger.debug(f"Failed to parse structured data: {e}")

        return None

    def _parse_structured_data_item(self, data: Dict, base_url: str) -> Optional[Dict[str, Any]]:
        """Parse a single structured data item"""
        info = {}

        # Organization schema
        if data.get('@type') in ['Organization', 'Corporation', 'Company']:
            if 'name' in data:
                info['name'] = data['name']
            if 'email' in data:
                info['email'] = data['email']
            if 'telephone' in data:
                info['phone'] = data['telephone']
            if 'url' in data:
                info['website'] = urljoin(base_url, data['url']) if data['url'].startswith('/') else data['url']
            if 'address' in data:
                address_data = data['address']
                if isinstance(address_data, dict):
                    address_parts = []
                    for field in ['streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'addressCountry']:
                        if field in address_data and address_data[field]:
                            address_parts.append(address_data[field])
                    if address_parts:
                        info['address'] = ', '.join(address_parts)

        return info if info else None

    def _extract_company_name(self, text: str) -> Optional[str]:
        """Extract company name from text"""
        # Look for common company name patterns
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip obvious non-company lines
            if any(skip in line.lower() for skip in [
                'http', 'www.', '@', 'tel:', 'phone:', 'email:', 'fax:',
                'copyright', '©', 'all rights reserved', 'terms of service',
                'privacy policy', 'contact us', 'about us'
            ]):
                continue

            # Look for company-like patterns
            if (len(line) > 3 and len(line) < 80 and
                line[0].isupper() and
                not line.endswith('.') and
                not line.isdigit() and
                ' ' in line):  # Most company names have spaces

                words = line.split()
                if 1 < len(words) <= 5:  # Reasonable company name length
                    return line

        return None

    def _extract_address(self, text: str) -> Optional[str]:
        """Extract address from text"""
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for address patterns
            if (',' in line and len(line) > 10 and len(line) < 200 and
                not any(skip in line.lower() for skip in [
                    'http', 'www.', '@', 'tel:', 'phone:', 'email:'
                ])):

                # Check for postal codes (US pattern)
                if re.search(r'\b\d{5}(-\d{4})?\b', line):
                    return line

                # Check for international postal codes
                if re.search(r'\b[A-Z]\d[A-Z] \d[A-Z]\d\b', line):  # Canadian
                    return line

        return None
