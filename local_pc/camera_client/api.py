import asyncio
import stream
import analyzer
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

_shutdown = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _shutdown
    _shutdown = False
    yield
    _shutdown = True


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"])


@app.get("/stream")
async def mjpeg_stream():
    async def generate():
        while not _shutdown:
            frame = stream.latest_frame
            if frame:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" +
                    frame +
                    b"\r\n"
                )
            await asyncio.sleep(0.033)  # ~30fps

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace;boundary=frame")


@app.get("/analysis")
async def get_analysis():
    return {"result": analyzer.latest_analysis, "is_analyzing": analyzer.is_analyzing}


@app.get("/analysis/image")
async def get_analyzed_image():
    if analyzer.analyzed_image is None:
        raise HTTPException(status_code=404, detail="No image analyzed yet")
    return Response(content=analyzer.analyzed_image, media_type="image/jpeg")
