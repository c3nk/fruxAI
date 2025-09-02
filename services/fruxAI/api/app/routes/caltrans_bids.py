from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.config.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/insert-caltrans-bids")
async def insert_caltrans_bids(data: dict):
    """
    Insert Caltrans bid data into database
    """
    logger.info("Inserting Caltrans bids into database...")

    try:
        # Get database session
        async with get_db() as session:
            # Insert bid data
            bids = [
                ('10-1L8604', 6, 1, 2053700.00, 'VC1200002736'),
                ('10-1L8604', 6, 2, 2271255.20, 'VC1500004960'),
                ('10-1L8604', 6, 3, 2287000.00, 'VC2000002246'),
                ('10-1L8604', 6, 4, 2307077.55, 'VC1700000908'),
                ('10-1L8604', 6, 5, 2324503.15, 'VC2200003483'),
                ('10-1L8604', 6, 6, 2575075.00, 'VC1200003869')
            ]

            inserted_count = 0
            for bid in bids:
                await session.execute(
                    text("""
                        INSERT INTO caltrans_bids
                        (contract_number, number_of_bidders, bid_rank, bid_amount, bidder_id)
                        VALUES ($1, $2, $3, $4, $5)
                    """),
                    bid
                )
                inserted_count += 1

            await session.commit()

            logger.info(f"Successfully inserted {inserted_count} Caltrans bid records")

            return {
                "status": "success",
                "message": f"Inserted {inserted_count} Caltrans bid records",
                "data": {
                    "contract_number": "10-1L8604",
                    "total_bidders": 6,
                    "inserted_records": inserted_count
                }
            }

    except Exception as e:
        logger.error(f"Error inserting Caltrans bids: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )

@router.get("/caltrans-bids")
async def get_caltrans_bids():
    """
    Get all Caltrans bids from database
    """
    try:
        async with get_db() as session:
            result = await session.execute(
                text("SELECT * FROM caltrans_bids ORDER BY bid_rank")
            )
            rows = result.fetchall()

            return {
                "status": "success",
                "count": len(rows),
                "data": [
                    {
                        "id": row[0],
                        "contract_number": row[1],
                        "number_of_bidders": row[2],
                        "bid_rank": row[3],
                        "bid_amount": row[4],
                        "bidder_id": row[5],
                        "created_at": row[6]
                    }
                    for row in rows
                ]
            }

    except Exception as e:
        logger.error(f"Error fetching Caltrans bids: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
