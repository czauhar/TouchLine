from fastapi import APIRouter, HTTPException
from app.sports_api import sports_api
from app.services import MatchService
from app.database import get_db
from app.data_service import data_service
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/matches", tags=["matches"])

# Sports API endpoints
@router.get("/live")
async def get_live_matches():
    """Get currently live matches with efficient caching"""
    try:
        match_data_list = await data_service.get_live_matches_efficient()
        
        # Convert MatchData objects to dict format for frontend
        matches = []
        for match_data in match_data_list:
            match_dict = {
                "id": match_data.external_id,
                "fixture": {
                    "id": int(match_data.external_id),
                    "date": match_data.start_time.isoformat(),
                    "status": {"short": match_data.status, "elapsed": match_data.elapsed_time},
                    "referee": match_data.referee,
                    "venue": {"name": match_data.venue},
                    "weather": match_data.weather
                },
                "teams": {
                    "home": {"name": match_data.home_team},
                    "away": {"name": match_data.away_team}
                },
                "goals": {
                    "home": match_data.home_score,
                    "away": match_data.away_score
                },
                "league": {"name": match_data.league},
                "alert_metrics": {
                    "basic": {
                        "home_score": match_data.home_score,
                        "away_score": match_data.away_score,
                        "score_difference": abs(match_data.home_score - match_data.away_score),
                        "total_goals": match_data.home_score + match_data.away_score,
                        "match_status": match_data.status,
                        "elapsed_time": match_data.elapsed_time,
                        "referee": match_data.referee,
                        "venue": match_data.venue,
                        "weather": match_data.weather
                    },
                    "possession": {"home": match_data.home_possession, "away": match_data.away_possession},
                    "shots": {
                        "home": match_data.home_shots,
                        "away": match_data.away_shots,
                        "home_on_target": match_data.home_shots_on_target,
                        "away_on_target": match_data.away_shots_on_target
                    },
                    "corners": {"home": match_data.home_corners, "away": match_data.away_corners},
                    "fouls": {"home": match_data.home_fouls, "away": match_data.away_fouls},
                    "cards": {
                        "home_yellow": match_data.home_yellow_cards,
                        "away_yellow": match_data.away_yellow_cards,
                        "home_red": match_data.home_red_cards,
                        "away_red": match_data.away_red_cards
                    },
                    "xg": {"home": match_data.home_xg, "away": match_data.away_xg},
                    "pressure": {"home": match_data.home_pressure, "away": match_data.away_pressure},
                    "momentum": {"home": match_data.home_momentum, "away": match_data.away_momentum}
                },
                "detailed_stats": match_data.stats_data,
                "events": match_data.events_data,
                "lineups": match_data.lineups_data
            }
            matches.append(match_dict)
        
        return {"matches": matches, "count": len(matches)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/today")
async def get_todays_matches():
    """Get today's matches with efficient caching"""
    try:
        match_data_list = await data_service.get_todays_matches_efficient()
        
        # Convert MatchData objects to dict format for frontend
        matches = []
        for match_data in match_data_list:
            match_dict = {
                "id": match_data.external_id,
                "fixture": {
                    "id": int(match_data.external_id),
                    "date": match_data.start_time.isoformat(),
                    "status": {"short": match_data.status, "elapsed": match_data.elapsed_time},
                    "referee": match_data.referee,
                    "venue": {"name": match_data.venue},
                    "weather": match_data.weather
                },
                "teams": {
                    "home": {"name": match_data.home_team},
                    "away": {"name": match_data.away_team}
                },
                "goals": {
                    "home": match_data.home_score,
                    "away": match_data.away_score
                },
                "league": {"name": match_data.league},
                "alert_metrics": {
                    "basic": {
                        "home_score": match_data.home_score,
                        "away_score": match_data.away_score,
                        "score_difference": abs(match_data.home_score - match_data.away_score),
                        "total_goals": match_data.home_score + match_data.away_score,
                        "match_status": match_data.status,
                        "elapsed_time": match_data.elapsed_time,
                        "referee": match_data.referee,
                        "venue": match_data.venue,
                        "weather": match_data.weather
                    },
                    "possession": {"home": match_data.home_possession, "away": match_data.away_possession},
                    "shots": {
                        "home": match_data.home_shots,
                        "away": match_data.away_shots,
                        "home_on_target": match_data.home_shots_on_target,
                        "away_on_target": match_data.away_shots_on_target
                    },
                    "corners": {"home": match_data.home_corners, "away": match_data.away_corners},
                    "fouls": {"home": match_data.home_fouls, "away": match_data.away_fouls},
                    "cards": {
                        "home_yellow": match_data.home_yellow_cards,
                        "away_yellow": match_data.away_yellow_cards,
                        "home_red": match_data.home_red_cards,
                        "away_red": match_data.away_red_cards
                    },
                    "xg": {"home": match_data.home_xg, "away": match_data.away_xg},
                    "pressure": {"home": match_data.home_pressure, "away": match_data.away_pressure},
                    "momentum": {"home": match_data.home_momentum, "away": match_data.away_momentum}
                },
                "detailed_stats": match_data.stats_data,
                "events": match_data.events_data,
                "lineups": match_data.lineups_data
            }
            matches.append(match_dict)
        
        return {"matches": matches, "count": len(matches)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get("/test")
async def get_test_matches():
    """Get test matches data for frontend testing"""
    return {
        "matches": [
            {
                "id": "test_1",
                "fixture": {
                    "id": 1,
                    "date": "2025-07-27T15:00:00+00:00",
                    "status": {
                        "short": "1H",
                        "elapsed": 25
                    },
                    "referee": "Test Referee",
                    "venue": {
                        "name": "Test Stadium"
                    },
                    "weather": {}
                },
                "teams": {
                    "home": {
                        "name": "Manchester United"
                    },
                    "away": {
                        "name": "Liverpool"
                    }
                },
                "goals": {
                    "home": 2,
                    "away": 1
                },
                "league": {
                    "name": "Premier League"
                },
                "alert_metrics": {
                    "basic": {
                        "home_score": 2,
                        "away_score": 1,
                        "score_difference": 1,
                        "total_goals": 3,
                        "match_status": "1H",
                        "elapsed_time": 25,
                        "referee": "Test Referee",
                        "venue": "Test Stadium",
                        "weather": {}
                    },
                    "possession": {
                        "home": 55,
                        "away": 45
                    },
                    "shots": {
                        "home": 8,
                        "away": 5,
                        "home_on_target": 4,
                        "away_on_target": 2
                    },
                    "corners": {
                        "home": 6,
                        "away": 3
                    },
                    "fouls": {
                        "home": 7,
                        "away": 9
                    },
                    "cards": {
                        "home_yellow": 1,
                        "away_yellow": 2,
                        "home_red": 0,
                        "away_red": 0
                    },
                    "xg": {
                        "home": 2.1,
                        "away": 1.3
                    },
                    "pressure": {
                        "home": 65,
                        "away": 35
                    },
                    "momentum": {
                        "home": 0.7,
                        "away": 0.3
                    }
                },
                "detailed_stats": [],
                "events": [],
                "lineups": []
            },
            {
                "id": "test_2",
                "fixture": {
                    "id": 2,
                    "date": "2025-07-27T17:30:00+00:00",
                    "status": {
                        "short": "NS",
                        "elapsed": 0
                    },
                    "referee": "Another Referee",
                    "venue": {
                        "name": "Another Stadium"
                    },
                    "weather": {}
                },
                "teams": {
                    "home": {
                        "name": "Arsenal"
                    },
                    "away": {
                        "name": "Chelsea"
                    }
                },
                "goals": {
                    "home": 0,
                    "away": 0
                },
                "league": {
                    "name": "Premier League"
                },
                "alert_metrics": {
                    "basic": {
                        "home_score": 0,
                        "away_score": 0,
                        "score_difference": 0,
                        "total_goals": 0,
                        "match_status": "NS",
                        "elapsed_time": 0,
                        "referee": "Another Referee",
                        "venue": "Another Stadium",
                        "weather": {}
                    },
                    "possession": {
                        "home": 50,
                        "away": 50
                    },
                    "shots": {
                        "home": 0,
                        "away": 0,
                        "home_on_target": 0,
                        "away_on_target": 0
                    },
                    "corners": {
                        "home": 0,
                        "away": 0
                    },
                    "fouls": {
                        "home": 0,
                        "away": 0
                    },
                    "cards": {
                        "home_yellow": 0,
                        "away_yellow": 0,
                        "home_red": 0,
                        "away_red": 0
                    },
                    "xg": {
                        "home": 0.0,
                        "away": 0.0
                    },
                    "pressure": {
                        "home": 50,
                        "away": 50
                    },
                    "momentum": {
                        "home": 0.5,
                        "away": 0.5
                    }
                },
                "detailed_stats": [],
                "events": [],
                "lineups": []
            }
        ],
        "count": 2
    } 