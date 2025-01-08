from fastapi import APIRouter, HTTPException, Query, Depends, Request
from app.services.kite_service import KiteService
import logging
from typing import Dict, Optional
from app.core.config import get_settings

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create router without prefix (prefix will be set in api.py)
router = APIRouter(tags=["kite"])

# Debug: Print router info
logger.debug("=== Kite Router Setup ===")
logger.debug(f"Router tags: {router.tags}")

# Initialize KiteService
kite_service = KiteService()

@router.get("/test/{token}")
async def test_kite_api(token: str) -> Dict:
    """Test Kite API with token"""
    logger.debug(f"=== GET /test/{token} endpoint called ===")
    try:
        # Set the token first
        kite_service.set_access_token(token)
        # Try to get profile as a test
        profile = kite_service.get_profile()
        return {"status": "success", "message": "API test successful", "data": profile}
    except Exception as e:
        logger.error(f"Error in test_kite_api: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/direct-test/{token}")
async def direct_test_kite_api(token: str) -> Dict:
    """Direct test of Kite API with token"""
    logger.debug(f"=== GET /direct-test/{token} endpoint called ===")
    try:
        # Make a direct API call without storing token
        url = "https://api.kite.trade/user/profile"
        settings = get_settings()
        headers = {
            'X-Kite-Version': '3',
            'Authorization': f'token {settings.KITE_API_KEY}:{token}'
        }
        
        logger.debug(f"Making direct request to: {url}")
        logger.debug(f"Headers: {headers}")
        
        response = kite_service._session.get(
            url=url,
            headers=headers,
            timeout=10
        )
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        logger.debug(f"Response body: {response.text[:1000]}")
        
        # If response is not 2xx, raise HTTPException
        if not 200 <= response.status_code < 300:
            error_detail = response.json() if response.text else {"message": "Unknown error"}
            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail.get("message", str(error_detail))
            )
        
        return {
            "status": "success", 
            "message": "Direct API test successful", 
            "data": response.json()
        }
    except requests.RequestException as e:
        logger.error(f"Request error in direct_test_kite_api: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Kite API: {str(e)}"
        )
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in direct_test_kite_api: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON response from Kite API: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in direct_test_kite_api: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/login")
async def login() -> Dict:
    """Get login URL for Kite Connect"""
    logger.debug("=== GET /login endpoint called ===")
    settings = get_settings()
    login_url = f"https://kite.zerodha.com/connect/login?api_key={settings.KITE_API_KEY}&v=3"
    return {"login_url": login_url}

@router.get("/callback")
async def callback(request: Request, request_token: str = Query(..., description="Request token from Kite")) -> Dict:
    """Handle callback from Kite Connect"""
    logger.debug("=== GET /callback endpoint called ===")
    logger.debug(f"Request token: {request_token}")
    try:
        access_token = kite_service.generate_session(request_token)
        logger.debug(f"Generated access token: {access_token}")
        return {"status": "success", "access_token": access_token}
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/token")
async def set_access_token(access_token: str = Query(..., description="Kite access token")) -> Dict:
    """Set and validate access token"""
    logger.debug(f"=== POST /token endpoint called ===")
    logger.debug(f"Access token: {access_token}")
    try:
        result = kite_service.set_access_token(access_token)
        logger.debug(f"Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in set_access_token: {str(e)}")
        raise

@router.get("/token")
async def get_access_token() -> Dict:
    """Get stored access token"""
    logger.debug("=== GET /token endpoint called ===")
    token = kite_service.get_stored_token()
    if token:
        return {"status": "success", "token": token}
    raise HTTPException(status_code=404, detail="No token found")

@router.delete("/token")
async def clear_access_token() -> Dict:
    """Clear stored access token"""
    logger.debug("=== DELETE /token endpoint called ===")
    return kite_service.clear_token()

@router.get("/profile/{token}")
async def get_profile_with_token(token: str) -> Dict:
    """Get user profile with token"""
    logger.debug(f"=== GET /profile/{token} endpoint called ===")
    try:
        # Set the token first
        kite_service.set_access_token(token)
        # Get profile
        return kite_service.get_profile()
    except Exception as e:
        logger.error(f"Error in get_profile_with_token: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profile")
async def get_profile() -> Dict:
    """Get user profile using stored token"""
    logger.debug("=== GET /profile endpoint called ===")
    return kite_service.get_profile()

@router.get("/positions")
async def get_positions() -> Dict:
    """Get user positions"""
    logger.debug("=== GET /positions endpoint called ===")
    return kite_service.get_positions()

@router.get("/holdings")
async def get_holdings() -> Dict:
    """Get user holdings"""
    logger.debug("=== GET /holdings endpoint called ===")
    return kite_service.get_holdings()

@router.get("/verify-token/{token}")
async def verify_token(token: str) -> Dict:
    """Verify token by checking storage and making a test API call"""
    logger.debug(f"=== GET /verify-token/{token} endpoint called ===")
    try:
        # 1. Try to set the token
        set_result = kite_service.set_access_token(token)
        logger.debug(f"Set token result: {set_result}")
        
        # 2. Try to get stored token
        stored_token = kite_service.get_stored_token()
        logger.debug(f"Stored token: {stored_token}")
        
        # 3. Try to get profile
        profile = kite_service.get_profile()
        logger.debug(f"Profile: {profile}")
        
        return {
            "status": "success",
            "message": "Token verified successfully",
            "token_stored": bool(stored_token),
            "token_matches": stored_token == token,
            "profile": profile
        }
    except Exception as e:
        logger.error(f"Error in verify_token: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Debug: Print all routes
logger.debug("Available kite routes:")
for route in router.routes:
    logger.debug(f"{route.methods} {route.path}")
    logger.debug(f"Route name: {route.name}")
    logger.debug(f"Route endpoint: {route.endpoint}")
    logger.debug("---")