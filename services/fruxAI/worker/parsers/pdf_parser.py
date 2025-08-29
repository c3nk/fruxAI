import pdfplumber
import logging
from typing import Dict, Any, Optional
import re
from io import BytesIO

logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self.url_pattern = re.compile(r'https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:\w)*)?)?')

    async def extract_metadata(self, content: bytes) -> Dict[str, Any]:
        """Extract metadata from PDF content"""
        try:
            with pdfplumber.open(BytesIO(content)) as pdf:
                metadata = {
                    'content_type': 'application/pdf',
                    'page_count': len(pdf.pages),
                    'extracted_text': '',
                    'company_info': {}
                }

                # Extract text from all pages
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"

                metadata['extracted_text'] = full_text.strip()

                # Extract basic metadata
                if hasattr(pdf, 'metadata') and pdf.metadata:
                    pdf_metadata = pdf.metadata
                    if '/Title' in pdf_metadata:
                        metadata['title'] = pdf_metadata['/Title']
                    if '/Subject' in pdf_metadata:
                        metadata['description'] = pdf_metadata['/Subject']
                    if '/Author' in pdf_metadata:
                        metadata['author'] = pdf_metadata['/Author']
                    if '/Keywords' in pdf_metadata:
                        metadata['keywords'] = pdf_metadata['/Keywords']

                # Extract company information
                company_info = self._extract_company_info(full_text)
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

                logger.info(f"Extracted metadata from PDF: {len(full_text)} chars, {metadata.get('page_count', 0)} pages")
                return metadata

        except Exception as e:
            logger.error(f"Failed to extract PDF metadata: {e}")
            return {
                'content_type': 'application/pdf',
                'error': str(e),
                'extracted_text': ''
            }

    def _extract_company_info(self, text: str) -> Dict[str, Any]:
        """Extract company information from text"""
        company_info = {}

        # Extract emails
        emails = self.email_pattern.findall(text)
        if emails:
            company_info['email'] = list(set(emails))  # Remove duplicates

        # Extract phone numbers
        phones = self.phone_pattern.findall(text)
        if phones:
            formatted_phones = []
            for phone in phones:
                # Format phone numbers
                if len(phone) >= 4:
                    formatted_phone = f"({phone[1]}) {phone[2]}-{phone[3]}"
                    if phone[0]:  # Country code
                        formatted_phone = f"{phone[0]} {formatted_phone}"
                    formatted_phones.append(formatted_phone)
            if formatted_phones:
                company_info['phone'] = list(set(formatted_phones))

        # Extract URLs
        urls = self.url_pattern.findall(text)
        if urls:
            # Filter out common non-company URLs
            company_urls = [url for url in urls if not any(skip in url.lower() for skip in [
                'linkedin.com', 'facebook.com', 'twitter.com', 'instagram.com',
                'youtube.com', 'google.com', 'wikipedia.org'
            ])]
            if company_urls:
                company_info['website'] = list(set(company_urls))

        # Try to extract company name (this is heuristic-based)
        company_name = self._extract_company_name(text)
        if company_name:
            company_info['name'] = company_name

        # Try to extract address
        address = self._extract_address(text)
        if address:
            company_info['address'] = address

        return company_info

    def _extract_company_name(self, text: str) -> Optional[str]:
        """Try to extract company name from text using heuristics"""
        lines = text.split('\n')

        # Look for lines that might be company names
        candidates = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip lines that are clearly not company names
            if any(skip in line.lower() for skip in [
                'http', 'www.', '@', 'tel:', 'phone:', 'email:', 'fax:',
                'address:', 'contact', '©', 'all rights reserved'
            ]):
                continue

            # Look for lines with proper capitalization and reasonable length
            if (len(line) > 3 and len(line) < 100 and
                line[0].isupper() and
                not line.endswith('.') and
                not line.isdigit()):

                # Check if it looks like a company name
                words = line.split()
                if len(words) <= 5:  # Company names are usually short
                    candidates.append(line)

        # Return the most promising candidate
        if candidates:
            # Prefer candidates that appear multiple times
            return max(candidates, key=candidates.count)

        return None

    def _extract_address(self, text: str) -> Optional[str]:
        """Try to extract address from text"""
        lines = text.split('\n')

        # Look for lines that might contain addresses
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for patterns that suggest an address
            if (',' in line and
                any(state in line.upper() for state in [
                    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
                ]) and len(line) > 10):

                return line

        return None
