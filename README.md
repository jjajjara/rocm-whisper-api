# 🚀 ROCm-Whisper-API

A Dockerized API server for OpenAI's Whisper, meticulously optimized for **AMD GPUs (ROCm)**. This project simplifies the deployment and utilization of the powerful Whisper model for speech-to-text transcription on AMD's accelerated hardware.

---

## ✨ Overview

This repository provides a streamlined solution to run the Whisper API leveraging the performance benefits of AMD's ROCm platform. It's designed for developers and enthusiasts looking to integrate high-performance audio transcription into their applications with AMD GPUs.

---

## 🔗 Project Links

* **GitHub Repository:** For the complete source code, detailed development insights, and the `Dockerfile`, please visit:
    👉 [**https://github.com/jjajjara/rocm-whisper-api**](https://github.com/jjajjara/rocm-whisper-api)

* **Docker Hub Image:** Pull the pre-built Docker image directly from Docker Hub:
    🐳 [**https://hub.docker.com/r/jjajjara/rocm-whisper-api**](https://hub.docker.com/r/jjajjara/rocm-whisper-api)

---

## 🛠️ Base PyTorch Container & Customization

This container is built upon a robust ROCm-enabled PyTorch image:
`rocm/pytorch:rocm6.3.4_ubuntu24.04_py3.12_pytorch_release_2.4.0`

**Want to use a different PyTorch version or a custom base image?**
No problem! You can easily modify the `Dockerfile` in the [GitHub repository](https://github.com/jjajjara/rocm-whisper-api). Explore other compatible PyTorch images on the [PyTorch Docker Hub repository](https://hub.docker.com/r/rocm/pytorch) to suit your specific needs.

---

## ⚙️ Configuration & Environment Variables

Proper configuration through environment variables is essential for optimal performance. These variables are typically set within your `docker-compose.yml` file.

**Crucial Note on `HSA_OVERRIDE_GFX_VERSION`:**
It is vital to specify this variable if your AMD GPU model requires it for proper ROCm compatibility and performance. For example, users with an **AMD Radeon 780M** GPU **must** set this to `11.0.0` for correct operation.

**Whisper Model:**
Due to the constraints of the testing environment during development, the `base` Whisper model was used. You can adjust this to other models like `small`, `medium`, or `large` as per your requirements.

### Key Environment Variables:

* `HSA_OVERRIDE_GFX_VERSION`: Required for specific ROCm compatibility.
    * **Example:** `HSA_OVERRIDE_GFX_VERSION=11.0.0` (for AMD Radeon 780M)
* `WHISPER_MODEL`: Specifies the Whisper model to load.
    * **Example:** `WHISPER_MODEL=base`

---

## 🐳 Docker Compose Example

For simplified deployment and management of the ROCm-Whisper-API service, using a `docker-compose.yml` file is highly recommended. Below is a comprehensive example:

```yaml
services:
  rocm-whisper-api-service:
    image: jjajjara/rocm-whisper-api:latest # Ensure this matches your pushed Docker Hub image tag (e.g., your_username/rocm-whisper-api:latest)
    container_name: rocm-whisper-api
    restart: unless-stopped
    ports:
      - "8080:8080" # Maps container port 8080 on the host to container port 8080
    environment:
      - HSA_OVERRIDE_GFX_VERSION=11.0.0 # <<< IMPORTANT: Adjust this based on your specific AMD GPU model if needed
      - WHISPER_MODEL=base             # Change to 'small', 'medium', 'large', etc., as required
    devices:
      - "/dev/kfd:/dev/kfd" # Essential for ROCm Kernel Fusion Device access
      - "/dev/dri:/dev/dri" # Essential for Direct Rendering Infrastructure access for GPU
    # (Optional) Volume setup for model caching.
    # Uncomment the following lines to persist downloaded Whisper models on your host PC
    # to prevent re-downloading on container restarts and save bandwidth/time.
    # volumes:
    #   - ~/.cache/whisper:/root/.cache/whisper
```
---
## 🧪 How to Test

After successfully running the Docker container, you can test the API using the following methods:

### 1. cURL Test

You can send an audio file (e.g., `test.m4a`) to the API endpoint using `curl`:

```bash
curl -X POST -F "file=@test.m4a" http://localhost:8080/transcribe
```

### 2. Python Client Example

If your GitHub repository includes a `client_example.py` script, you can use it to test the API. Make sure `test.m4a` is in the same directory or provide the correct path.

```bash
python3 client_example.py test.m4a
```
