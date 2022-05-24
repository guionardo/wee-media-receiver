from .setup import app


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post('/media/{media_type}/{media_id}')
async def receive_media(media_type: str, media_id: str, body: bytes = None):
    return {"media_type": media_type, "media_id": media_id, "body": body}
