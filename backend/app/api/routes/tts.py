from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from gtts import gTTS
import io

router = APIRouter()

@router.get("")
def text_to_speech(text: str):
    """
    Generate Text-to-Speech audio using Google TTS.
    Returns an MP3 audio stream.
    """
    tts = gTTS(text, lang='vi')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return StreamingResponse(fp, media_type="audio/mpeg")
