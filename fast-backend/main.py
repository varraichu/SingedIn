import os, json
import base64
import requests
import httpx

from dotenv import load_dotenv
from contextlib import asynccontextmanager
from urllib.parse import urlencode

from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from utilities.lyrics import fetchLyricsForSongs
from helpers.spotify_helper import generateRandomString, token, fetchAllLikedSongs
from utilities.chroma_setup import initialiseChromaClient, addDataToVectorStore
from utilities.chatbot import ChatBot

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
FRONTEND_URI = os.getenv('FRONTEND_URI')
# vector_store = None

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Backend Starting")
    vector_store = initialiseChromaClient()
    print("vector store: ", vector_store)
    yield {"vector_store": vector_store}
    print("Backend Shutting Down")


app = FastAPI(lifespan=lifespan)

class Conversation(BaseModel):
    message: str

class UserData():
    username: str
    email: str
    profile: str
    followers: int
    avatar:str

@app.get("/")
async def root():
    return {"message": "Hello World"}

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
async def callback(code, state, error=None):
    print(f"code: {code}")
    print(f"state: {state}")
    if error:
        return RedirectResponse('/' + urlencode({"error": error }))
    
    try:
        token_res = await token(code)
        print("Spotify token response:", token_res)
        redirect_response = RedirectResponse(url=FRONTEND_URI)
        redirect_response.set_cookie(
            key='access_token',
            value=token_res["access_token"],
            expires=token_res["expires_in"]
        )
        redirect_response.set_cookie(
            key='refresh_token',
            value=token_res["refresh_token"]
        )
        return redirect_response
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
            
            response.set_cookie(key='access_token', value=data["access_token"], expires=data["expires_in"])
            response.set_cookie(key='refresh_token', value=data["refresh_token"])

            return {"message": "tokens refreshed"}
        
    except Exception as e:
        return {"error: ", str(e)}


@app.get('/api/get_user_data')
async def get_user_data(access_token:str = Cookie(None)):
    if not access_token:
        raise ValueError("No access token provided")
    url = "https://api.spotify.com/v1/me"
    headers = {
        "Authorization" : "Bearer " + access_token
    }

    try:
        async with httpx.AsyncClient() as client:
            http_response = await client.get(url=url, headers=headers)
            data = http_response.json()

            userData = UserData()
            userData.username = data["display_name"]
            userData.email = data["email"]
            userData.profile = data["href"]
            userData.followers = data["followers"]["total"]
            userData.avatar = data["images"][0]["url"]
            print("user Data: ", userData);
            return userData
    except Exception as e:
        return {"error: ", str(e)}


@app.get('/api/get_liked_songs')
async def get_all_liked_songs(access_token: str = Cookie(None)):
    try:
        spotifySongs = await fetchAllLikedSongs("https://api.spotify.com/v1/me/tracks?limit=50", access_token=access_token)
        formattedSongs = []

        for song in spotifySongs:
            modifiedSong = {
                "name" : song["track"]["name"],
                "artist" : song["track"]["artists"][0]["name"],
                "album_art" : song["track"]["album"]["images"][0]["url"],
            }

            formattedSongs.append(modifiedSong)
        
        print("Fetched all songs: ", len(formattedSongs))
        
        try:
            folder_name = "files"
            os.makedirs(folder_name, exist_ok=True)
            file_path = os.path.join(folder_name, "liked_songs.json")

            with open(file_path, "a", encoding="utf-8") as f:
                json.dump(formattedSongs, f, ensure_ascii=False, indent=2)

        except Exception as e:
            return {"error: ", str(e)}

        return {"message":"Songs fetched"}

    except Exception as e:
        return {"error: ", str(e)}

@app.get('/api/get_lyrics')
async def getLyrics(request: Request):
    # fetchLyricsForSongs()
    vector_store = request.state.vector_store
    print("Vectoriana= ", vector_store)
    addDataToVectorStore(vector_store=vector_store)
    return {"message" : "lyrics fetched"}


@app.post("/api/chat")
async def chat(conversation:Conversation, request: Request):
    vector_store = request.state.vector_store
    ai_chatbot = ChatBot(vector_store=vector_store)
    response = ai_chatbot.enhanceText(userMessage=conversation.message)
    return {"Massage": response}