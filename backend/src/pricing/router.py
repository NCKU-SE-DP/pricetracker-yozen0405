from fastapi import APIRouter, Query, HTTPException
from .config import pricing_config
from sentry_sdk import capture_exception
import requests

router = APIRouter(
    prefix="/prices",
    tags=["Prices"],
    responses={404: {"description": "Not found"}},
)

@router.get("/necessities-price")
def get_necessities_prices(
        category=Query(None), commodity=Query(None)
):
    url = pricing_config.NECESSITIES_PRICE_API_URL
    params = {"CategoryName": category, "Name": commodity}
    
    try:
        response = requests.get(
            url=url,
            params=params,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        capture_exception(e)
        raise HTTPException(status_code=500, detail="Our price server is down, please try later")
    
    try:
        response = response.json()
    except ValueError:
        raise HTTPException(status_code=404, detail="No resources found.")

    return response
    