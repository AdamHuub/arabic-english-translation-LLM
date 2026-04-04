from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from translation.gemini_api import translate_text, translate_text_stream
import uvicorn

app = FastAPI(title="Arabic-English Translation API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str
    prompt_type: str = "detailed"

class TranslationResponse(BaseModel):
    translated_text: str

@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    try:
        translated = translate_text(
            request.text, 
            request.source_lang, 
            request.target_lang, 
            request.prompt_type
        )
        return TranslationResponse(translated_text=translated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stream-translate")
async def stream_translate(request: TranslationRequest):
    """
    Endpoint de streaming en temps réel. Renvoie les tokens au fur et à mesure.
    """
    try:
        generator = translate_text_stream(
            request.text, 
            request.source_lang, 
            request.target_lang, 
            request.prompt_type
        )
        return StreamingResponse(generator, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
