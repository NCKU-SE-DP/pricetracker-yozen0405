from fastapi import APIRouter, Query
from .config import pricing_settings
import requests

router = APIRouter(
    tags=["Prices"]
)

@router.get("/prices/necessities-price")
def get_necessities_prices(
        category=Query(None), commodity=Query(None)
):
    return requests.get(
        pricing_settings.NECESSITIES_PRICE_API_URL,
        params={"CategoryName": category, "Name": commodity},
    ).json()