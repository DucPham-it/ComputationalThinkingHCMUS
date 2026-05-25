from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
import io

try:
    from gtts import gTTS
except ImportError:  # pragma: no cover - depends on local optional package install
    gTTS = None

router = APIRouter()

@router.get("")
def text_to_speech(text: str):
    """
    Generate Text-to-Speech audio using Google TTS.
    Returns an MP3 audio stream.
    """
    if gTTS is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Text-to-speech is unavailable because gTTS is not installed.",
        )

    try:
        tts = gTTS(text, lang="vi")
        fp = io.BytesIO()
        tts.write_to_fp(fp)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Text-to-speech service is temporarily unavailable.",
        ) from error

    fp.seek(0)
    return StreamingResponse(fp, media_type="audio/mpeg")
