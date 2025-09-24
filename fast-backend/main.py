import os
import base64
import requests
import httpx

from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from pydantic import BaseModel
from dotenv import load_dotenv
from helpers.spotify_helper import generateRandomString, token

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

app = FastAPI()

class Conversation(BaseModel):
    message: str


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/chat")
async def chat(conversation:Conversation):
    return {"Massage": conversation.message}

@app.get("/api/login")
async def login():
    state = generateRandomString(16)
    scope = 'user-library-read user-read-private user-read-email'
    params = {
        "response_type": 'code',
        "client_id": CLIENT_ID,
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        "state": state
    }
    queryParams = urlencode(params)
    
    return RedirectResponse(
        'https://accounts.spotify.com/authorize?' + queryParams
    )

@app.get("/callback")
async def callback(code, state, response:Response, error=None):
    print(f"code: {code}")
    print(f"state: {state}")
    if error:
        return RedirectResponse('/' + urlencode({"error": error }))
    
    try:
      token_res = await token(code)
      print("Spotify token response:", token_res)
      response.set_cookie(key='access_token', value=token_res["access_token"])
      response.set_cookie(key='refresh_token', value=token_res["refresh_token"], expires=token_res["expires_in"])
      return {"message": "tokens retrieved"}
    except Exception as e:
        print("Error in callback:", e)
        return {"error: ", str(e)}
    
@app.get("/api/refresh")
async def refresh_token(refresh_token:str, response:Response):
    authString = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8'))
    queryString = authString.decode('utf-8')
    url = "https://accounts.spotify.com/api/token"
    headers = {
        'Authorization': "Basic " + queryString,
        'content-type': "application/x-www-form-urlencoded"
    }
    body = {
        "grant_type": 'refresh_token',
        "refresh_token": refresh_token
    }

    try:
        async with httpx.AsyncClient() as client:
            http_response = await client.post(url=url, data=body, headers=headers)
            data = http_response.json()
            
            response.set_cookie(key='access_token', value=data["access_token"])
            response.set_cookie(key='refresh_token', value=data["refresh_token"], expires=data["expires_in"])

            return {"message": "tokens retrieved"}
        
    except Exception as e:
        return {"error: ", str(e)}

