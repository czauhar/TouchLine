from fastapi import APIRouter, HTTPException
from app.sports_api import sports_api
from app.services import MatchService
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/matches", tags=["matches"])

# Sports API endpoints
@router.get("/live")
async def get_live_matches():
    """Get currently live matches"""
    matches = await sports_api.get_live_matches()
    formatted_matches = [sports_api.format_match_data(match) for match in matches]
    return {"matches": formatted_matches, "count": len(formatted_matches)}

@router.get("/today")
async def get_todays_matches():
    """Get today's matches"""
    matches = await sports_api.get_todays_matches()
    formatted_matches = [sports_api.format_match_data(match) for match in matches]
    return {"matches": formatted_matches, "count": len(formatted_matches)}

@router.get("/{fixture_id}/statistics")
async def get_match_statistics(fixture_id: int):
    """Get detailed statistics for a specific match"""
    stats = await sports_api.get_match_statistics(fixture_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Match statistics not found")
    return {"statistics": stats}

@router.get("/leagues/{league_id}")
async def get_league_matches(league_id: int, season: int = 2024):
    """Get matches for a specific league and season"""
    matches = await sports_api.get_league_matches(league_id, season)
    formatted_matches = [sports_api.format_match_data(match) for match in matches]
    return {"matches": formatted_matches, "count": len(formatted_matches)}

# Database endpoints
@router.get("/db/live")
async def get_db_live_matches():
    """Get live matches from database"""
    try:
        db = next(get_db())
        matches = MatchService.get_live_matches(db)
        return {
            "matches": [
                {
                    "id": match.id,
                    "external_id": match.external_id,
                    "home_team": match.home_team,
                    "away_team": match.away_team,
                    "league": match.league,
                    "start_time": match.start_time.isoformat(),
                    "status": match.status,
                    "home_score": match.home_score,
                    "away_score": match.away_score
                }
                for match in matches
            ],
            "count": len(matches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/db/today")
async def get_db_todays_matches():
    """Get today's matches from database"""
    try:
        db = next(get_db())
        matches = MatchService.get_todays_matches(db)
        return {
            "matches": [
                {
                    "id": match.id,
                    "external_id": match.external_id,
                    "home_team": match.home_team,
                    "away_team": match.away_team,
                    "league": match.league,
                    "start_time": match.start_time.isoformat(),
                    "status": match.status,
                    "home_score": match.home_score,
                    "away_score": match.away_score
                }
                for match in matches
            ],
            "count": len(matches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/db/sync")
async def sync_matches():
    """Sync live matches from sports API to database"""
    try:
        db = next(get_db())
        synced_matches = await MatchService.sync_live_matches(db)
        return {
            "message": f"Successfully synced {len(synced_matches)} matches",
            "synced_count": len(synced_matches)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing matches: {str(e)}") 