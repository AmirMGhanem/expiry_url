from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
import time
import hashlib

app = FastAPI()
store = {}

class LinkRequest(BaseModel):
    url: str
    expiry_seconds: int

@app.post("/generate")
def generate_link(data: LinkRequest, request: Request):
    short_id = hashlib.md5((data.url + str(time.time())).encode()).hexdigest()[:6]
    expires_at = int(time.time()) + data.expiry_seconds
    store[short_id] = {"url": data.url, "expires_at": expires_at}
    
    return {
        "short_url": f"https://expiry-url.onrender.com/{short_id}",
        "expires_at": expires_at
    }


@app.get("/{short_id}")
def redirect(short_id: str):
    entry = store.get(short_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Not found api")
    if time.time() > entry["expires_at"]:
        return JSONResponse(content={"message": "This link has expired."}, status_code=410)
    return RedirectResponse(url=entry["url"])
