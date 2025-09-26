import random
import math
import base64
import httpx
import requests
import os

from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

def generateRandomString(string_length: int):
    text = ""
    possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    for i in range(0,string_length):
        random_int = math.floor(random.random() * len(possible))
        text += possible[random_int]
    
    return text


async def token(code, redirect_uri=REDIRECT_URI, grant_type="authorization_code"):
    authString = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8'))
    queryString = authString.decode('utf-8')
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
    "Authorization": "Basic " + queryString,
    "Content-Type": "application/x-www-form-urlencoded"
    }
    body = {
        "code":code,
        "redirect_uri": redirect_uri,
        "grant_type": grant_type
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url=url, data=body, headers=headers)
        return response.json()


async def fetchAllLikedSongs(url:str, access_token: str):
    if not access_token:
        raise ValueError("No access token provided")
    headers = {
        "Authorization": "Bearer " + access_token
    }

    try:
        async with httpx.AsyncClient() as client:
            http_response = await client.get(url=url, headers=headers)
            data = http_response.json()

            allSongs = [*data["items"]]
            
            if data["next"]:
                print("fetching next: ", data["next"])
                nextBatchSongs = await fetchAllLikedSongs(data["next"], access_token=access_token)
                allSongs += nextBatchSongs
            
            return allSongs
        
    except Exception as e:
        return {"error: ", str(e)}