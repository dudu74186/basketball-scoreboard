# Serviço de visão computacional (detecção de objetos com YOLOv11).
# Base já vem com PyTorch + CUDA prontos, evitando reinstalar uma versão
# CPU-only do torch quando o requirements.txt for instalado por cima.
FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime

# Dependências de sistema para decodificação de vídeo (OpenCV/ffmpeg).
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Dentro do container não existe display — desliga a janela do OpenCV por
# padrão (pode ser sobrescrito em tempo de execução com -e SHOW_VIDEO=true
# se houver X11 configurado, mas não é o uso recomendado em container).
ENV SHOW_VIDEO=false

CMD ["python", "main.py"]
