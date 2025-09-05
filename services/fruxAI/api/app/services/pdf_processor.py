"""
PDF Processor using pdfplumber + markdownify
PDF dosyalarını işler ve Markdown formatına çevirir.
FastAPI ile entegrasyon için PdfProcessor interface sağlar.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import pdfplumber
from markdownify import markdownify as md
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PdfProcessor:
    """
    PDF processing class that replaces DoclingProcessor
    Uses pdfplumber + markdownify for faster, more reliable PDF processing
    """

    def __init__(self):
        logger.info("Initializing PdfProcessor with pdfplumber + markdownify")
        self.head_aliases = {
            'contract_number': ['Contract Number', 'Contract No.', 'Contract #', 'Contract Num'],
            'project_id': ['Project ID', 'Project No.', 'Proj ID', 'Project Num'],
            'bid_amount': ['Bid Amount', 'Total Bid', 'Bid Total', 'Amount'],
            'firm_name': ['Bidder Name', 'Company Name', 'Firm Name', 'Bidder'],
            'rank': ['Rank', 'Bid Rank', 'Position', 'Rank Order'],
            'preference': ['Preference', 'SB', 'Small Business'],
            'cslb_number': ['CSLB #', 'License #', 'License Number']
        }

    def extract_text_with_layout(self, pdf_path: str) -> str:
        """
        PDF'den metni layout'ı koruyarak çıkarır

        Args:
            pdf_path: PDF dosyasının yolu

        Returns:
            str: HTML formatında düzenlenmiş metin
        """
        html_content = []

        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Sayfa başlığı
                html_content.append(f"<h2>Sayfa {page_num + 1}</h2>")

                # Metni çıkar
                text = page.extract_text()

                if text:
                    # Metni paragraflara böl
                    paragraphs = text.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            # Tablo benzeri yapıları tespit et
                            if '\t' in para or '  ' in para.replace('\n', ''):
                                # Tablo benzeri yapı için pre tag kullan
                                tab_replaced = para.replace('\t', '    ')
                                html_content.append(f"<pre>{tab_replaced}</pre>")
                            else:
                                # Normal paragraf
                                br_replaced = para.replace('\n', '<br>')
                                html_content.append(f"<p>{br_replaced}</p>")
                else:
                    html_content.append("<p><em>Bu sayfada metin bulunamadı</em></p>")

                # Sayfa ayracı
                html_content.append("<hr>")

        return '\n'.join(html_content)

    def convert_pdf_to_markdown(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        """
        PDF dosyasını Markdown'a çevirir

        Args:
            pdf_path: PDF dosyasının yolu
            output_path: Çıktı Markdown dosyasının yolu (None ise otomatik belirlenir)

        Returns:
            str: Markdown içeriği
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF dosyası bulunamadı: {pdf_path}")

        if output_path is None:
            # Otomatik dosya adı oluştur
            pdf_name = Path(pdf_path).stem
            output_path = f"{pdf_name}.md"

        logger.info(f"Processing PDF: {pdf_path}")

        # PDF'den HTML çıkar
        html_content = self.extract_text_with_layout(pdf_path)
        logger.info(f"Extracted HTML content: {len(html_content)} characters")

        # HTML'den Markdown'a çevir
        markdown_content = md(html_content, heading_style="ATX")

        # Gereksiz boşlukları temizle
        markdown_content = markdown_content.strip()

        # Dosyaya yaz
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        logger.info(f"Markdown created: {output_path} ({len(markdown_content)} characters)")

        return markdown_content

    async def process_pdf(self, pdf_path: str, state: str) -> Dict[str, Any]:
        """
        Process PDF and extract tender/bid information
        Compatible interface with DoclingProcessor
        """
        try:
            logger.info(f"Processing PDF: {pdf_path} for state {state}")

            # PDF'yi Markdown'a çevir
            pdf_name = Path(pdf_path).stem
            markdown_path = f"/app/storage/pdfs/{state}/exports/{pdf_name}.md"
            markdown_content = self.convert_pdf_to_markdown(pdf_path, markdown_path)

            # Temel metadata çıkar (Contract Number, vb.)
            metadata = self.extract_basic_metadata(markdown_content)

            # İşlenmiş dosyayı taşı
            processed_path = f"/app/storage/pdfs/{state}/processed/{Path(pdf_path).name}"
            os.rename(pdf_path, processed_path)

            result = {
                'status': 'success',
                'state': state,
                'file_name': Path(pdf_path).name,
                'markdown_path': markdown_path,
                'metadata': metadata,
                'content_length': len(markdown_content),
                'extraction_info': {
                    'processor': 'pdfplumber_markdownify',
                    'timestamp': str(os.path.getmtime(markdown_path))
                }
            }

            logger.info(f"Successfully processed PDF: {pdf_path}")
            return result

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise

    def extract_basic_metadata(self, markdown_content: str) -> Dict[str, Any]:
        """
        Markdown içeriğinden temel metadata çıkarır
        """
        lines = markdown_content.split('\n')
        metadata = {}

        for line in lines[:50]:  # İlk 50 satırda ara
            line = line.strip()
            if not line:
                continue

            # Contract Number ara
            if 'Contract Number:' in line or 'Contract No:' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    metadata['contract_number'] = parts[1].strip()

            # Project ID ara
            elif 'Project ID:' in line or 'Project No:' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    metadata['project_id'] = parts[1].strip()

            # Bid Opening Date ara
            elif 'Bid Opening Date:' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    metadata['bid_opening_date'] = parts[1].strip()

            # Number of Bidders ara
            elif 'Number of Bidders:' in line:
                parts = line.split(':')
                if len(parts) > 1:
                    metadata['number_of_bidders'] = parts[1].strip()

        return metadata
