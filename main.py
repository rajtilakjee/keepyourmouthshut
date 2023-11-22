from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gencast import (
    gencast,
)  # Assuming you have a gencast module with the gencast function

app = FastAPI()

# Enable CORS for all origins (you can customize this based on your needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InputData(BaseModel):
    openai_api_key: str
    elevenlabs_api_key: str
    name: str
    desc: str
    topic1: str
    topic2: str
    topic3: str
    advert1: str
    advert2: str


@app.post("/process")
async def process_data(data: InputData):
    try:
        topics = [data.topic1, data.topic2, data.topic3]
        adverts = [data.advert1, data.advert2]
        gencast(
            data.openai_api_key,
            data.elevenlabs_api_key,
            data.name,
            data.desc,
            topics,
            adverts,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")


@app.get("/download/zip")
async def download_zip_file():
    file_path = "server/kyms-output.zip"
    return FileResponse(
        file_path, media_type="application/zip", filename="kyms-output.zip"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
