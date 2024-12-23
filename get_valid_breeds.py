from typing import List

import httpx
from fastapi import HTTPException

CAT_API_URL = "https://api.thecatapi.com/v1/breeds"


async def fetch_valid_breeds() -> List[str]:
    async with httpx.AsyncClient() as client:
        response = await client.get(CAT_API_URL)
        if response.status_code != 200:
            raise HTTPException(
                status_code=502, detail="Failed to fetch breed data from the API"
            )
        breeds = response.json()
        return [breed["name"] for breed in breeds]
