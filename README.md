# 🎬 Hyper Editor Pro - Editor de Vídeo 9:16 Automatizado

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![GPU](https://img.shields.io/badge/Hardware-NVIDIA%20%7C%20AMD%20%7C%20MPS-green)
![GFPGAN](https://img.shields.io/badge/IA-GFPGAN%20Enabled-orange)
![License](https://img.shields.io/badge/License-Open%20Source-brightgreen)

Um editor de vídeo profissional e automatizado, desenvolvido especificamente para criadores de conteúdo (TikTok, Reels, Shorts). O **Satoru Editor Pro** combina facilidade de uso com tecnologias avançadas de processamento de imagem e IA.

---

## 🔥 Funcionalidades Principais

- **📐 Layout Nativo 9:16:** Criação automática de composições verticais com bordas dinâmicas, fundos desfocados (Blur) ou cores sólidas.
- **💬 Legendas Inteligentes:** Renderização de legendas com suporte completo a fontes customizadas, cores, bordas e fundos.
- **🎭 Sistema de Emojis:** Adição de emojis dinâmicos que acompanham o conteúdo do vídeo.
- **🖼️ Marca d'Água:** Proteção de conteúdo com suporte a logos (PNG) e marcas d'água de texto com opacidade ajustável.
- **🎵 Gestão de Áudio:** Remoção de áudio original, sincronização automática com pastas de clipes musicais e ajuste de duração.
- **📂 Processamento em Lote:** Sistema de abas que permite configurar múltiplos vídeos para renderização sequencial.

---

## 🚀 Diferenciais Técnicos

### ⚡ Aceleração por Hardware (GPU)
Diferente de outros editores simples, o Satoru Editor Pro foi construído para performance. Ele detecta automaticamente e utiliza o máximo do seu hardware:
- **NVIDIA:** Suporte total a **CUDA** para processamento ultrarrápido.
- **AMD:** Suporte a **ROCm**, garantindo performance em placas gráficas AMD.
- **Apple Silicon:** Suporte nativo a **MPS** (Metal Performance Shaders) para usuários de Mac M1/M2/M3.
- **CPU:** Fallback inteligente para processamento em processadores caso nenhuma GPU compatível seja detectada.

### 🌟 Melhoria de Imagem com IA (GFPGAN)
Integramos a tecnologia **GFPGANv1.4** (Generative Facial Prior GAN) para garantir que seus vídeos tenham a melhor qualidade possível.
- **Restauração Facial:** Recupera detalhes de rostos em vídeos de baixa resolução.
- **Remoção de Artefatos:** Limpa o ruído e artefatos de compressão, deixando o vídeo com aspecto profissional.
- **Nitidez:** Melhora a definição geral do vídeo durante o processo de exportação.

---

## 🛠️ Instalação

### Pré-requisitos
Certifique-se de ter o Python 3.8 ou superior instalado.

1. **Clone o repositório:**
```bash
git clone https://github.com/sr-satoru/editor-videos-com-bordas.git
cd editor-videos-com-bordas
```

2. **Crie um ambiente virtual (recomendado):**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **(Opcional) Instale o suporte a IA:**
Para usar o GFPGAN, instale as dependências extras:
```bash
pip install torch torchvision gfpgan
```

---

## 📖 Como Usar

Para iniciar a interface gráfica, execute o arquivo principal:

```bash
python run.py
```

### Comandos de Inicialização (Forçar Hardware)
Você pode forçar o uso de um hardware específico via linha de comando:

- **Forçar NVIDIA:** `python run.py --nvidia`
- **Forçar AMD:** `python run.py --amd`
- **Forçar CPU:** `python run.py --cpu`

---

## 🤝 Contribuição

Este é um projeto **Open Source**! Sinta-se à vontade para:
- Abrir Issues para reportar bugs ou sugestões.
- Enviar Pull Requests com melhorias de código.
- Sugerir novos estilos de bordas ou fontes.

---

## 📝 Licença

Distribuído sob a licença Open Source. Veja `LICENSE` para mais informações.

---
*Desenvolvido com ❤️ para a comunidade de criadores.*
