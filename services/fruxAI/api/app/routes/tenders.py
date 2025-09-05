from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import Optional, List, Dict, Any
from app.config.database import get_connection
from app.services.docling_processor import DoclingProcessor
import logging
import os
import json
import csv

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize Docling processor
docling_processor = DoclingProcessor()

# HEAD_ALIASES for PDF parsing
HEAD_ALIASES = {
    'contract_number': ['Contract Number', 'Contract No.', 'Contract #', 'Contract Num'],
    'project_id': ['Project ID', 'Project No.', 'Proj ID', 'Project Num'],
    'bid_amount': ['Bid Amount', 'Total Bid', 'Bid Total', 'Amount'],
    'firm_name': ['Bidder Name', 'Company Name', 'Firm Name', 'Bidder'],
    'rank': ['Rank', 'Bid Rank', 'Position', 'Rank Order']
}

@router.post("/ingest")
async def ingest_pdf(
    background_tasks: BackgroundTasks,
    state: str = Form(..., description="State code (e.g., CA, TX)"),
    file: UploadFile = File(..., description="PDF file to process")
):
    """
    Ingest a PDF file and extract tender/bid information
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Create state directory if not exists
    state_dir = f"/app/storage/pdfs/{state}"
    os.makedirs(f"{state_dir}/incoming", exist_ok=True)
    os.makedirs(f"{state_dir}/processed", exist_ok=True)
    os.makedirs(f"{state_dir}/exports", exist_ok=True)

    # Save uploaded file
    file_path = f"{state_dir}/incoming/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Add background processing task
    background_tasks.add_task(process_pdf_background, state, file.filename, file_path)

    return {
        "status": "processing",
        "message": f"PDF {file.filename} queued for processing in state {state}",
        "file_path": file_path
    }

@router.get("/state/{state}/tenders")
async def get_tenders(
    state: str,
    contract_number: Optional[str] = None,
    project_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Get tenders for a specific state with optional filters
    """
    # For now, return empty list since we don't have data yet
    return {
        "status": "success",
        "state": state,
        "count": 0,
        "data": []
    }

@router.get("/state/{state}/tenders/{tender_id}/bids")
async def get_tender_bids(state: str, tender_id: int):
    """
    Get all bids for a specific tender
    """
    try:
        async with get_connection() as session:
            result = await session.execute(
                text("""
                    SELECT b.id, b.firm_id, b.bid_amount, b.currency, b.rank,
                           b.preference, b.cslb_number, b.name_official,
                           f.name_official as firm_name_official
                    FROM bids b
                    LEFT JOIN firms f ON b.state = f.state AND b.firm_id = f.firm_id
                    WHERE b.state = $1 AND b.tender_id = $2
                    ORDER BY b.rank, b.bid_amount
                """),
                [state, tender_id]
            )
            rows = result.fetchall()

            bids = []
            for row in rows:
                bids.append({
                    "id": row[0],
                    "firm_id": row[1],
                    "bid_amount": float(row[2]),
                    "currency": row[3],
                    "rank": row[4],
                    "preference": row[5],
                    "cslb_number": row[6],
                    "name_official": row[7] or row[8]  # Use bid name or firm name
                })

            return {
                "status": "success",
                "state": state,
                "tender_id": tender_id,
                "count": len(bids),
                "data": bids
            }

    except Exception as e:
        logger.error(f"Error fetching tender bids: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/state/{state}/exports/{pdf_stem}/tables")
async def list_markdown_tables(state: str, pdf_stem: str):
    """
    List available Markdown tables for a processed PDF
    """
    tables_dir = f"/app/storage/pdfs/{state}/exports/{pdf_stem}/tables"

    if not os.path.exists(tables_dir):
        raise HTTPException(status_code=404, detail="Export directory not found")

    try:
        files = [f for f in os.listdir(tables_dir) if f.endswith('.md')]
        files.sort()

        return {
            "status": "success",
            "state": state,
            "pdf_stem": pdf_stem,
            "tables": files
        }
    except Exception as e:
        logger.error(f"Error listing markdown tables: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/state/{state}/exports/{pdf_stem}/tables/{table_name}.md")
async def download_markdown_table(state: str, pdf_stem: str, table_name: str):
    """
    Download a specific Markdown table
    """
    file_path = f"/app/storage/pdfs/{state}/exports/{pdf_stem}/tables/{table_name}.md"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Table file not found")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "status": "success",
            "state": state,
            "pdf_stem": pdf_stem,
            "table_name": table_name,
            "content": content
        }
    except Exception as e:
        logger.error(f"Error downloading markdown table: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

async def process_pdf_background(state: str, filename: str, file_path: str):
    """
    Background task to process PDF with Docling and save results
    """
    logger.info(f"Processing PDF: {filename} for state {state}")

    try:
        # Process PDF with Docling
        result = await docling_processor.process_pdf(file_path, state)

        if 'error' in result:
            logger.error(f"PDF processing failed: {result['error']}")
            return

        # Save to database
        await save_to_database(result)

        # Create exports
        pdf_stem = filename.replace('.pdf', '')
        await create_exports(state, pdf_stem, result)

        # Move to processed directory
        processed_path = f"/app/storage/pdfs/{state}/processed/{filename}"
        os.rename(file_path, processed_path)

        logger.info(f"PDF processing completed: {filename}")

    except Exception as e:
        logger.error(f"Error in background processing: {e}")
        # Move to processed anyway to avoid re-processing
        processed_path = f"/app/storage/pdfs/{state}/processed/{filename}"
        os.rename(file_path, processed_path)

async def save_to_database(result: Dict[str, Any]):
    """Save processing results to database"""
    try:
        async with get_connection() as session:
            # Insert tender
            tender = result['tender']
            tender_result = await session.execute(
                text("""
                    INSERT INTO tenders (state, file_name, contract_number, project_id,
                                       bid_opening_date, title, winner_firm_id, winner_amount,
                                       currency, extraction_info, status)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    ON CONFLICT (state, file_name) DO UPDATE SET
                        contract_number = EXCLUDED.contract_number,
                        project_id = EXCLUDED.project_id,
                        bid_opening_date = EXCLUDED.bid_opening_date,
                        title = EXCLUDED.title,
                        winner_firm_id = EXCLUDED.winner_firm_id,
                        winner_amount = EXCLUDED.winner_amount,
                        extraction_info = EXCLUDED.extraction_info,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """),
                [
                    tender['state'], tender['file_name'], tender.get('contract_number'),
                    tender.get('project_id'), tender.get('bid_opening_date'), tender.get('title'),
                    tender.get('winner_firm_id'), tender.get('winner_amount'), tender.get('currency'),
                    json.dumps(tender.get('extraction_info')), tender.get('status')
                ]
            )

            tender_id = tender_result.fetchone()[0]

            # Insert firms
            for firm in result.get('firms', []):
                await session.execute(
                    text("""
                        INSERT INTO firms (state, firm_id, name_official, cslb_number)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (state, firm_id) DO NOTHING
                    """),
                    [firm['state'], firm['firm_id'], firm.get('name_official'), firm.get('cslb_number')]
                )

            # Insert bids
            for bid in result.get('bids', []):
                await session.execute(
                    text("""
                        INSERT INTO bids (state, tender_id, firm_id, bid_amount, currency,
                                        rank, preference, cslb_number, name_official)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        ON CONFLICT (state, tender_id, firm_id) DO NOTHING
                    """),
                    [
                        bid['state'], tender_id, bid['firm_id'], bid['bid_amount'],
                        bid.get('currency'), bid.get('rank'), bid.get('preference'),
                        bid.get('cslb_number'), bid.get('name_official')
                    ]
                )

            await session.commit()
            logger.info(f"Saved tender {tender_id} with {len(result.get('bids', []))} bids")

    except Exception as e:
        logger.error(f"Error saving to database: {e}")
        raise

async def create_exports(state: str, pdf_stem: str, result: Dict[str, Any]):
    """Create JSON, CSV, and Markdown exports"""
    try:
        exports_dir = f"/app/storage/pdfs/{state}/exports/{pdf_stem}"
        os.makedirs(f"{exports_dir}/tables", exist_ok=True)

        # Create summary.json
        summary = {
            'pdf_stem': pdf_stem,
            'state': state,
            'tender': result['tender'],
            'bid_count': len(result.get('bids', [])),
            'firm_count': len(result.get('firms', [])),
            'table_count': len(result.get('tables', [])),
            'processing_timestamp': str(result['tender'].get('extraction_info', {}).get('processed_at'))
        }

        with open(f"{exports_dir}/summary.json", 'w') as f:
            json.dump(summary, f, indent=2, default=str)

        # Create bids.csv
        if result.get('bids'):
            with open(f"{exports_dir}/bids.csv", 'w', newline='') as f:
                if result['bids']:
                    writer = csv.DictWriter(f, fieldnames=result['bids'][0].keys())
                    writer.writeheader()
                    writer.writerows(result['bids'])

        # Create table Markdown files
        for i, table in enumerate(result.get('tables', [])):
            table_md = f"# Table {i+1}\n\n"
            table_md += "| " + " | ".join(table.get('columns', [])) + " |\n"
            table_md += "|" + "|".join(["---"] * len(table.get('columns', []))) + "|\n"

            for row in table.get('rows', []):
                table_md += "| " + " | ".join(row) + " |\n"

            with open(f"{exports_dir}/tables/table-{i+1:03d}.md", 'w') as f:
                f.write(table_md)

        logger.info(f"Created exports for {pdf_stem}")

    except Exception as e:
        logger.error(f"Error creating exports: {e}")
