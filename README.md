# 🎨 AI Mood Board - AI-Powered Inspiration Board

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0+-blue.svg)](https://tailwindcss.com/)

AI-powered creative mood board creation application. Analyzes user emotions and mood to create visual inspiration boards with local AI image generation.

## ✨ Features

- 🤖 **AI Mood Analysis**: Analyzes user input with intelligent keyword detection
- 🖼️ **Smart Visual Suggestions**: Themed images using local Stable Diffusion
- 🎨 **Automatic Color Palette**: Theme-based color recommendations
- 💭 **Inspiration Sentences**: Personalized inspiring texts
- 🎯 **AI Image Generation**: Custom images with local Stable Diffusion (CUDA support)
- 📱 **Responsive Design**: Modern and user-friendly interface
- 💾 **Mood Board Saving**: Save user boards
- 🚀 **No API Keys Required**: Works completely offline with local AI models

## 🚀 Quick Start

### Requirements

- Python 3.8+
- Node.js 16+
- CUDA-compatible GPU (optional, for faster image generation)
- 8GB+ RAM (for local AI models)
- Ollama (optional, for local text analysis)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/BengisuEkizoglu/ai-mood-board.git
cd ai-mood-board
```

2. **Backend setup**
```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# Optional: Install Ollama for local AI text analysis
# curl -fsSL https://ollama.ai/install.sh | sh
# ollama pull qwen2.5:7b
```

3. **Frontend setup**
```bash
cd ../frontend
npm install
```

4. **Run the application**
```bash
# Backend (Terminal 1)
cd backend
python main.py

# Frontend (Terminal 2)
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Documentation: http://localhost:8001/docs

## 🛠️ Technologies

### Backend
- **FastAPI**: Modern Python web framework
- **Local Stable Diffusion**: AI image generation with CUDA support
- **Ollama Qwen**: Local AI text analysis (optional)
- **PyTorch**: Deep learning framework
- **Diffusers**: HuggingFace diffusion models
- **Smart Fallback**: Themed image generation with Picsum
- **Keyword Analysis**: Simple mood detection without external APIs
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### Frontend
- **React 18**: Modern UI framework
- **TailwindCSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **React Router**: Page routing
- **Framer Motion**: Smooth animations
- **React Hot Toast**: User notifications

## 📁 Project Structure

```
ai-mood-board/
├── backend/
│   ├── main.py              # FastAPI application with local AI
│   ├── requirements.txt     # Python dependencies
│   └── env.example         # Example environment variables
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── Header.jsx
│   │   │   ├── Home.jsx
│   │   │   ├── MoodBoard.jsx
│   │   │   ├── ColorPalette.jsx
│   │   │   ├── ImageGrid.jsx
│   │   │   ├── InspirationCard.jsx
│   │   │   └── Footer.jsx
│   │   ├── App.jsx         # Main application
│   │   └── index.js        # Entry point
│   ├── public/             # Static files
│   └── package.json        # Node.js dependencies
└── README.md
```

## 🎯 Usage Example

1. **Enter mood description**: "I want to feel like walking in the streets of Paris in autumn"
2. **AI Analysis**: System analyzes emotion and theme using keyword detection
3. **Visual Suggestions**: 4-5 related images are generated using local Stable Diffusion
4. **Color Palette**: Theme-matching colors are suggested
5. **Inspiration Text**: AI generates personalized text
6. **AI Image**: Custom image generation with local model

## 🔑 Optional Local AI Setup

The application works completely offline, but you can enhance it with local AI models:

### Ollama Setup (Optional - for better text analysis)
1. Install Ollama: `curl -fsSL https://ollama.ai/install.sh | sh`
2. Pull the Qwen model: `ollama pull qwen2.5:7b`
3. Start Ollama service: `ollama serve`
4. The application will automatically use Ollama for mood analysis

### Benefits of Ollama
- **Completely local**: No internet required after setup
- **Free**: No API costs
- **Privacy**: All data stays on your machine
- **Better analysis**: More sophisticated mood detection than keyword matching

## 🔧 API Endpoints

- `POST /api/analyze-mood`: Mood analysis and recommendations
- `GET /api/images`: Image search
- `POST /api/generate-image`: AI image generation with local Stable Diffusion
- `POST /api/save-board`: Save mood board
- `GET /docs`: Interactive API documentation

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

⭐ If you like this project, don't forget to give it a star! 