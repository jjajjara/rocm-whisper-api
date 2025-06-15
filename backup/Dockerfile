# ROCm을 지원하는 공식 PyTorch 이미지를 베이스로 사용합니다.
# 태그는 사용 가능한 ROCm 버전에 맞게 조정할 수 있습니다.
# (https://hub.docker.com/r/rocm/pytorch/tags)
FROM rocm/pytorch:rocm6.3.4_ubuntu24.04_py3.12_pytorch_release_2.4.0

# --- 시스템 의존성 설치 ---
# Whisper는 오디오 처리를 위해 ffmpeg가 필요합니다.
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# --- Python 애플리케이션 설정 ---
# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 파일을 먼저 복사하여 종속성 캐싱을 활용합니다.
COPY app/requirements.txt .

# pip를 업그레이드하고 requirements.txt에 명시된 라이브러리를 설치합니다.
# 베이스 이미지에 torch가 이미 포함되어 있으므로, 여기서는 설치하지 않습니다.
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 코드를 복사합니다.
COPY app/ .

# --- 컨테이너 실행 설정 ---
# API 서버가 사용할 포트를 노출합니다.
EXPOSE 8080

# 컨테이너가 시작될 때 실행할 명령어를 정의합니다.
# Uvicorn을 사용하여 FastAPI 애플리케이션을 실행합니다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
