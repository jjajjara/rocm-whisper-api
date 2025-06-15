import whisper
import torch
import os
import traceback
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

# --------------------------------------------------------------------------
# 1. 모델 및 장치 설정
# --------------------------------------------------------------------------

# ROCm 지원이 가능한지 확인하고 장치를 설정합니다.
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 사용할 Whisper 모델을 선택합니다.
MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
model = None

# --------------------------------------------------------------------------
# 2. FastAPI 애플리케이션 초기화 및 모델 로드
# --------------------------------------------------------------------------
app = FastAPI(
    title="ROCm Whisper API",
    description="An API to transcribe audio files using OpenAI's Whisper on ROCm.",
    version="1.0.0"
)

@app.on_event("startup")
def load_whisper_model():
    """
    FastAPI 앱이 시작될 때 Whisper 모델을 로드합니다.
    오류 발생 시 구체적인 내용을 콘솔에 출력합니다.
    """
    global model
    try:
        print("="*50)
        print(f"PyTorch version: {torch.__version__}")
        print(f"Torch is built with ROCm: {torch.version.hip}")
        print(f"Is ROCm (GPU) available? -> {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"Current device: {torch.cuda.current_device()}")
            print(f"Device name: {torch.cuda.get_device_name(0)}")
        print(f"Attempting to load Whisper model: '{MODEL_NAME}'")
        print("="*50)
        
        # 1단계: 모델을 CPU에 먼저 로드합니다.
        print(f"Step 1: Loading model '{MODEL_NAME}' onto CPU...")
        cpu_model = whisper.load_model(MODEL_NAME, device="cpu")
        print("Step 1: Model loaded on CPU successfully.")

        # 2단계: GPU가 사용 가능하면 모델을 GPU로 이동시킵니다.
        if DEVICE == "cuda":
            print(f"Step 2: Moving model to GPU ({DEVICE})...")
            model = cpu_model.to(DEVICE)
            print("Step 2: Model moved to GPU successfully.")
        else:
            model = cpu_model
        
        print(f"\n✅ Whisper model '{MODEL_NAME}' is ready on device: {DEVICE}.\n")

    except Exception as e:
        print("="*50)
        print("❌ FAILED TO LOAD WHISPER MODEL ❌")
        print("="*50)
        # traceback을 사용하여 훨씬 더 상세한 에러 정보를 출력합니다.
        traceback.print_exc()
        print("="*50)
        # model 변수를 None으로 유지하여 /transcribe 엔드포인트가 오류를 반환하도록 합니다.
        model = None


@app.get("/", summary="Health Check", description="API 서버의 상태를 확인합니다.")
def read_root():
    """
    루트 엔드포인트는 API가 정상적으로 실행 중인지 간단히 확인할 수 있는 경로입니다.
    """
    status = "running"
    model_status = "loaded"
    if not model:
        status = "running_with_errors"
        model_status = "failed_to_load"
        
    return {"status": status, "model_status": model_status, "model_name": MODEL_NAME}


@app.post("/transcribe", summary="Transcribe Audio File", description="오디오 파일을 텍스트로 변환합니다.")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    음성 파일을 업로드하면 해당 파일의 내용을 텍스트로 변환하여 반환합니다.

    - **file**: 변환할 오디오 파일 (mp3, wav, m4a 등)
    """
    if not model:
        raise HTTPException(status_code=503, detail="Whisper model is not available. Check server logs for details.")
    
    contents = await file.read()

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_audio_file:
            temp_audio_file.write(contents)
            temp_path = temp_audio_file.name
        
        print(f"Transcribing file: {file.filename}")
        
        # Whisper 모델을 사용하여 오디오 파일을 텍스트로 변환합니다.
        # GPU 호환성 문제를 피하기 위해 fp16 옵션을 비활성화합니다.
        result = model.transcribe(temp_path, fp16=False)

        print("Transcription successful.")

        return JSONResponse(content={
            "filename": file.filename,
            "language": result["language"],
            "text": result["text"]
        })
    except Exception as e:
        print(f"❌ An error occurred during transcription: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)

