# Skills do Gemini

Este arquivo registra resoluções técnicas e aprendizados aplicados no projeto.

## 🛠️ Configuração de Ambiente (Deep Learning)
Para este projeto, estabelecemos a seguinte base técnica para garantir performance e isolamento:

1. **Gerenciamento de Ambiente:** Uso do `Conda` para isolar dependências de Visão Computacional.
   - Comando: `conda create -n placar_basquete python=3.10`
2. **Aceleração por GPU (CUDA):** Instalação do PyTorch vinculada à versão do CUDA disponível no sistema (v13.2 detectada).
   - Comando base: `pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`
3. **Bibliotecas Core:**
   - `ultralytics` (YOLOv11): Para detecção de objetos em tempo real.
   - `opencv-python`: Para manipulação de frames de vídeo.
   - `flask`: Para o servidor web da súmula.
