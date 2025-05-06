import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

app = FastAPI()
DEFAULT_AUDIO_PATH = "./audio/mp3"

audio_queue = asyncio.Queue()

streaming_active = True

async def generate_audio():
    global streaming_active
    chunk_size = 4096
    
    while streaming_active:
        with open(DEFAULT_AUDIO_PATH, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                await audio_queue.put(chunk)
                await asyncio.sleep(0.01)


async def audio_stream_generator() -> AsyncGenerator[bytes, None]:
    while True:
        chunk = await audio_queue.get()
        yield chunk

@app.on_event("startup")
async def startup():
    asyncio.create_task(generate_audio())

@app.on_event("shutdown")
async def shutdown():
    global streaming_active
    streaming_active = False

@app.get("/stream")
async def radio():
    return StreamingResponse(
        audio_stream_generator(),
        media_type="audio/mpeg",
        headers={"icy-name": "FastAPI Radio"}
    )
