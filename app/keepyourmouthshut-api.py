from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from keepyourmouthshut import generate_podcast

app = FastAPI()


class InputData(BaseModel):
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
        result_url = generate_podcast(
            data.name,
            data.desc,
            topics,
            adverts,
        )
        return {"message": "Processing complete", "result_url": result_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")
