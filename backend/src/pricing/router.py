from fastapi import APIRouter, Query
from .config import pricing_config
from src.services.exceptions_handler import NoResourceFoundException, InternalServerErrorException
from src.services.logger import price_logger
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

    price_logger.sended_request(url, params)
    try:
        response = requests.get(
            url=url,
            params=params,
        )
        response.raise_for_status()
        response = response.json()
        price_logger.response_success()
        return response
    except ValueError:
        price_logger.no_resource_found(url, params)
        raise NoResourceFoundException()
    except requests.exceptions.RequestException as e:
        price_logger.internal_error(e)
        raise InternalServerErrorException(e)
    