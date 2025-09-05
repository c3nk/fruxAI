from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
import logging
import json
from typing import Dict, List, Any, Optional
import os

logger = logging.getLogger(__name__)

class DoclingProcessor:
    def __init__(self):
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfPipelineOptions(
                    do_ocr=True,
                    ocr_options={
                        'lang': ['en'],
                        'force_ocr': False
                    }
                )
            }
        )

        # HEAD_ALIASES for column matching
        self.head_aliases = {
            'contract_number': ['Contract Number', 'Contract No.', 'Contract #', 'Contract Num'],
            'project_id': ['Project ID', 'Project No.', 'Proj ID', 'Project Num'],
            'bid_amount': ['Bid Amount', 'Total Bid', 'Bid Total', 'Amount'],
            'firm_name': ['Bidder Name', 'Company Name', 'Firm Name', 'Bidder'],
            'rank': ['Rank', 'Bid Rank', 'Position', 'Rank Order'],
            'preference': ['Preference', 'SB', 'Small Business'],
            'cslb_number': ['CSLB #', 'License #', 'License Number']
        }

    async def process_pdf(self, pdf_path: str, state: str) -> Dict[str, Any]:
        """
        Process PDF and extract tender/bid information
        """
        try:
            logger.info(f"Processing PDF: {pdf_path} for state {state}")

            # Convert document
            result = self.converter.convert(pdf_path)
            document = result.document

            # Extract metadata
            metadata = self._extract_metadata(document)

            # Extract tables
            tables = self._extract_tables(document)

            # Process bids from tables
            bids_data = self._process_bids_from_tables(tables, state)

            # Create tender record
            tender_data = self._create_tender_record(metadata, bids_data, pdf_path, state)

            return {
                'tender': tender_data,
                'bids': bids_data,
                'firms': self._extract_firms(bids_data),
                'tables': tables,
                'metadata': metadata
            }

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return {
                'error': str(e),
                'pdf_path': pdf_path,
                'state': state
            }

    def _extract_metadata(self, document) -> Dict[str, Any]:
        """Extract basic metadata from document"""
        metadata = {
            'page_count': len(document.pages),
            'title': None,
            'contract_number': None,
            'project_id': None,
            'bid_opening_date': None
        }

        # Try to extract from text content
        full_text = document.export_to_text()
        lines = full_text.split('\n')

        for line in lines[:50]:  # Check first 50 lines for metadata
            line = line.strip()
            if not line:
                continue

            # Extract contract number
            if 'contract' in line.lower() and ('number' in line.lower() or '#' in line):
                for alias in self.head_aliases['contract_number']:
                    if alias.lower() in line.lower():
                        metadata['contract_number'] = line.split(':')[-1].strip()
                        break

            # Extract project ID
            if 'project' in line.lower() and ('id' in line.lower() or 'number' in line.lower()):
                for alias in self.head_aliases['project_id']:
                    if alias.lower() in line.lower():
                        metadata['project_id'] = line.split(':')[-1].strip()
                        break

        return metadata

    def _extract_tables(self, document) -> List[Dict[str, Any]]:
        """Extract tables from document"""
        tables = []

        for table_idx, table in enumerate(document.tables):
            table_data = {
                'table_index': table_idx,
                'columns': [],
                'rows': []
            }

            # Extract headers
            if table.table_cells:
                # Get first row as headers
                first_row = []
                for cell in table.table_cells:
                    if cell.row_index == 0:
                        first_row.append(cell.text.strip() if cell.text else '')

                table_data['columns'] = first_row

                # Extract data rows
                for cell in table.table_cells:
                    if cell.row_index > 0:
                        if len(table_data['rows']) <= cell.row_index - 1:
                            table_data['rows'].extend([[] for _ in range(cell.row_index - len(table_data['rows']))])

                        if cell.row_index - 1 < len(table_data['rows']):
                            table_data['rows'][cell.row_index - 1].append(
                                cell.text.strip() if cell.text else ''
                            )

            tables.append(table_data)

        return tables

    def _process_bids_from_tables(self, tables: List[Dict], state: str) -> List[Dict[str, Any]]:
        """Process bids from extracted tables"""
        bids = []

        for table in tables:
            columns = table.get('columns', [])
            rows = table.get('rows', [])

            if not columns or not rows:
                continue

            # Map columns to our expected fields
            column_mapping = self._map_columns(columns)

            # Process each row
            for row_idx, row in enumerate(rows):
                if len(row) != len(columns):
                    continue

                bid_data = {
                    'state': state,
                    'firm_id': None,
                    'bid_amount': None,
                    'currency': 'USD',
                    'rank': None,
                    'preference': None,
                    'cslb_number': None,
                    'name_official': None
                }

                # Extract data based on column mapping
                for col_idx, col_name in enumerate(columns):
                    if col_idx < len(row):
                        value = row[col_idx].strip()

                        if col_name in column_mapping:
                            field = column_mapping[col_name]

                            if field == 'firm_name':
                                bid_data['name_official'] = value
                                bid_data['firm_id'] = self._generate_firm_id(value)
                            elif field == 'bid_amount':
                                bid_data['bid_amount'] = self._parse_amount(value)
                            elif field == 'rank':
                                bid_data['rank'] = self._parse_int(value)
                            elif field == 'preference':
                                bid_data['preference'] = value
                            elif field == 'cslb_number':
                                bid_data['cslb_number'] = value

                # Only add if we have essential data
                if bid_data['firm_id'] and bid_data['bid_amount']:
                    bids.append(bid_data)

        return bids

    def _map_columns(self, columns: List[str]) -> Dict[str, str]:
        """Map table columns to our expected fields using aliases"""
        mapping = {}

        for col in columns:
            col_lower = col.lower().strip()

            for field, aliases in self.head_aliases.items():
                for alias in aliases:
                    if alias.lower() in col_lower:
                        mapping[col] = field
                        break
                if col in mapping:
                    break

        return mapping

    def _create_tender_record(self, metadata: Dict, bids: List, pdf_path: str, state: str) -> Dict[str, Any]:
        """Create tender record from metadata and bids"""
        filename = os.path.basename(pdf_path)

        tender = {
            'state': state,
            'file_name': filename,
            'contract_number': metadata.get('contract_number'),
            'project_id': metadata.get('project_id'),
            'bid_opening_date': metadata.get('bid_opening_date'),
            'title': metadata.get('title'),
            'status': 'active',
            'extraction_info': {
                'pdf_path': pdf_path,
                'page_count': metadata.get('page_count'),
                'total_bids': len(bids)
            }
        }

        # Determine winner (lowest bid if no rank)
        if bids:
            if any(bid.get('rank') for bid in bids):
                # Use rank if available
                winner_bid = min(bids, key=lambda x: x.get('rank') or 999)
            else:
                # Use lowest amount
                winner_bid = min(bids, key=lambda x: x.get('bid_amount') or 999999999)

            tender['winner_firm_id'] = winner_bid.get('firm_id')
            tender['winner_amount'] = winner_bid.get('bid_amount')

        return tender

    def _extract_firms(self, bids: List[Dict]) -> List[Dict[str, Any]]:
        """Extract unique firms from bids"""
        firms = {}
        state = bids[0]['state'] if bids else 'CA'

        for bid in bids:
            firm_id = bid.get('firm_id')
            if firm_id and firm_id not in firms:
                firms[firm_id] = {
                    'state': state,
                    'firm_id': firm_id,
                    'name_official': bid.get('name_official'),
                    'cslb_number': bid.get('cslb_number')
                }

        return list(firms.values())

    def _generate_firm_id(self, firm_name: str) -> str:
        """Generate a firm ID from firm name"""
        if not firm_name:
            return 'UNKNOWN'

        # Clean and format firm name
        clean_name = ''.join(c for c in firm_name if c.isalnum() or c.isspace())
        return clean_name.upper().replace(' ', '_')[:50]

    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string to float"""
        if not amount_str:
            return None

        try:
            # Remove currency symbols and commas
            clean = amount_str.replace('$', '').replace(',', '').strip()
            return float(clean)
        except ValueError:
            return None

    def _parse_int(self, int_str: str) -> Optional[int]:
        """Parse string to int"""
        if not int_str:
            return None

        try:
            return int(int_str.strip())
        except ValueError:
            return None
