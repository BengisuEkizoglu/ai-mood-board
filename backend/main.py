from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
import openai
from dotenv import load_dotenv
import json
import random
import re
import base64
import io
from PIL import Image
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Mood Board API",
    description="AI-powered mood board creation API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Global Stable Diffusion pipeline
sd_pipeline = None

def initialize_stable_diffusion():
    """Initialize Stable Diffusion pipeline with CUDA support"""
    global sd_pipeline
    try:
        print("🔄 Initializing Stable Diffusion pipeline...")
        
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"📱 Using device: {device}")
        
        # Load the pipeline
        model_id = "runwayml/stable-diffusion-v1-5"
        sd_pipeline = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            safety_checker=None,
            requires_safety_checker=False
        )
        
        # Use DPM++ 2M scheduler for faster generation
        sd_pipeline.scheduler = DPMSolverMultistepScheduler.from_config(sd_pipeline.scheduler.config)
        
        # Move to device
        sd_pipeline = sd_pipeline.to(device)
        
        # Enable memory efficient attention if available
        if device == "cuda":
            try:
                sd_pipeline.enable_xformers_memory_efficient_attention()
                print("✅ XFormers memory efficient attention enabled")
            except:
                print("⚠️ XFormers not available, using standard attention")
        
        print("✅ Stable Diffusion pipeline initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize Stable Diffusion: {e}")
        return False

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    initialize_stable_diffusion()

# Pydantic models
class MoodRequest(BaseModel):
    description: str
    style: Optional[str] = "modern"

class ImageRequest(BaseModel):
    prompt: str
    style: Optional[str] = "realistic"

class MoodBoardResponse(BaseModel):
    images: List[dict]
    color_palette: List[str]
    inspiration_text: str
    mood_analysis: dict

# Color palettes for different moods
MOOD_COLORS = {
    "romantic": ["#FF6B9D", "#FFB3D1", "#FFE5F1", "#8B5A96", "#4A4A4A"],
    "peaceful": ["#87CEEB", "#98FB98", "#F0E68C", "#DDA0DD", "#F5F5DC"],
    "energetic": ["#FF4500", "#FFD700", "#32CD32", "#4169E1", "#FF1493"],
    "melancholic": ["#2F4F4F", "#696969", "#708090", "#B0C4DE", "#E6E6FA"],
    "nature": ["#228B22", "#8FBC8F", "#F4A460", "#DEB887", "#CD853F"],
    "urban": ["#708090", "#2F4F4F", "#FF6347", "#FFD700", "#4169E1"],
    "vintage": ["#8B4513", "#DEB887", "#F4A460", "#D2B48C", "#CD853F"],
    "modern": ["#000000", "#FFFFFF", "#808080", "#C0C0C0", "#FF6B35"]
}

def analyze_mood_with_ai(description: str) -> dict:
    """Analyzes mood with AI (Ollama Qwen or fallback)"""
    try:
        # Try Ollama API first
        try:
            prompt = f"""You are a mood analysis expert. Analyze this description: "{description}"

Determine:
1. Main emotion/mood (romantic/peaceful/energetic/melancholic/nature/urban/vintage/modern)
2. Color palette suggestion
3. Keywords for visual search
4. Inspiring sentence

Return only a JSON object:
{{
    "mood": "romantic",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "inspiration_text": "Inspiring sentence",
    "color_palette": "romantic"
}}"""

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:7b",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result_text = response.json()["response"]
                # Extract JSON from response
                json_start = result_text.find("{")
                json_end = result_text.rfind("}") + 1
                if json_start != -1 and json_end != -1:
                    json_str = result_text[json_start:json_end]
                    result = json.loads(json_str)
                    return result
                else:
                    print("Could not extract JSON from Ollama response")
                    return analyze_mood_fallback(description)
            else:
                print(f"Ollama API Error: {response.status_code}")
                return analyze_mood_fallback(description)
                
        except requests.exceptions.ConnectionError:
            print("Ollama not running, using fallback")
            return analyze_mood_fallback(description)
        except Exception as e:
            print(f"Ollama API Error: {e}")
            return analyze_mood_fallback(description)
            
    except Exception as e:
        print(f"Mood Analysis Error: {e}")
        # Fallback response
        return analyze_mood_fallback(description)

def analyze_mood_fallback(description: str) -> dict:
    """Simple keyword analysis for mood detection"""
    description_lower = description.lower()
    
    # Mood keyword mapping
    mood_keywords = {
        "romantic": ["romantic", "love", "heart", "flower", "candle", "wine", "passion", "romance"],
        "peaceful": ["peaceful", "calm", "serene", "meditation", "yoga", "tranquil", "quiet"],
        "energetic": ["energetic", "dynamic", "vibrant", "active", "sport", "energetic", "lively"],
        "melancholic": ["melancholic", "sad", "nostalgic", "melancholy", "sorrow", "blue"],
        "nature": ["nature", "forest", "sea", "mountain", "flower", "tree", "outdoor", "natural"],
        "urban": ["urban", "city", "modern", "building", "street", "metropolitan", "downtown"],
        "vintage": ["vintage", "retro", "old", "classic", "nostalgic", "antique", "traditional"],
        "modern": ["modern", "minimalist", "clean", "simple", "contemporary", "sleek"]
    }
    
    # Mood detection
    detected_mood = "modern"  # default
    max_score = 0
    
    for mood, keywords in mood_keywords.items():
        score = sum(1 for keyword in keywords if keyword in description_lower)
        if score > max_score:
            max_score = score
            detected_mood = mood
    
    # Extract keywords
    words = re.findall(r'\b\w+\b', description_lower)
    filtered_words = [word for word in words if len(word) > 3 and word not in ['the', 'and', 'with', 'for', 'like', 'feel', 'want', 'wanting']]
    keywords = filtered_words[:3] if filtered_words else ["inspiration", "creative", "design"]
    
    # Generate inspiration sentence
    inspiration_phrases = {
        "romantic": "The dance of love and passion, in harmony with your heart's rhythm",
        "peaceful": "The silent call of tranquility, soothing your soul",
        "energetic": "The excitement of energy, reflecting life's dynamic flow",
        "melancholic": "In the depths of melancholy lies the hidden treasure of beauty",
        "nature": "The pure beauty of nature, renewing your spirit",
        "urban": "The modern rhythm of the city, carrying life's dynamic energy",
        "vintage": "The elegance of the past meets today's creativity",
        "modern": "The minimal elegance of modernity, exploring the boundaries of creativity"
    }
    
    inspiration_text = inspiration_phrases.get(detected_mood, "Explore the boundaries of creativity")
    
    return {
        "mood": detected_mood,
        "keywords": keywords,
        "inspiration_text": inspiration_text,
        "color_palette": detected_mood
    }

def generate_multiple_images(keywords: List[str], count: int = 5) -> List[dict]:
    """Generates multiple images using local Stable Diffusion or themed images"""
    try:
        images = []
        search_query = " ".join(keywords[:3]) if keywords else "inspiration"
        
        for i in range(count):
            # Add variety to prompts
            prompt_variations = [
                f"{search_query}, beautiful, high quality",
                f"{search_query}, artistic, creative",
                f"{search_query}, inspiring, detailed",
                f"{search_query}, aesthetic, masterpiece",
                f"{search_query}, elegant, professional"
            ]
            
            prompt = prompt_variations[i % len(prompt_variations)]
            
            # Try local Stable Diffusion first, fallback to themed images
            try:
                result = generate_ai_image(prompt, "realistic")
                images.append({
                    "id": f"ai_{i}",
                    "urls": {"regular": result["url"]},
                    "alt_description": keywords[0] if keywords else "inspiration",
                    "user": {"name": "AI Generated"},
                    "source": result["source"]
                })
            except Exception as e:
                print(f"AI generation failed for image {i}, using themed image: {e}")
                # Fallback to themed image
                themed_result = generate_themed_image(prompt, "realistic")
                images.append({
                    "id": f"themed_{i}",
                    "urls": {"regular": themed_result["url"]},
                    "alt_description": keywords[0] if keywords else "inspiration",
                    "user": {"name": "Themed Image"},
                    "source": themed_result["source"]
                })
        
        return images
        
    except Exception as e:
        print(f"Multiple Image Generation Error: {e}")
        # Ultimate fallback: Picsum images
        return [
            {
                "id": f"fallback_{i}",
                "urls": {"regular": f"https://picsum.photos/400/300?random={i+300}"},
                "alt_description": keywords[0] if keywords else "inspiration",
                "user": {"name": "Fallback Image"}
            }
            for i in range(count)
        ]

def generate_ai_image(prompt: str, style: str = "realistic") -> dict:
    """Generates AI image with local Stable Diffusion"""
    global sd_pipeline
    
    try:
        enhanced_prompt = f"{prompt}, {style} style, high quality, detailed, beautiful, masterpiece"
        
        # Check if Stable Diffusion pipeline is available
        if sd_pipeline is None:
            print("⚠️ Stable Diffusion pipeline not initialized, using themed images")
            return generate_themed_image(prompt, style)
        
        print(f"🎨 Generating image with prompt: {enhanced_prompt}")
        
        # Generate image with Stable Diffusion
        with torch.no_grad():
            image = sd_pipeline(
                prompt=enhanced_prompt,
                num_inference_steps=20,
                guidance_scale=7.5,
                width=512,
                height=512
            ).images[0]
        
        # Convert PIL image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        print("✅ Image generated successfully!")
        
        return {
            "url": f"data:image/png;base64,{img_str}",
            "prompt": enhanced_prompt,
            "source": "Local Stable Diffusion",
            "model": "runwayml/stable-diffusion-v1-5"
        }
            
    except Exception as e:
        print(f"❌ Stable Diffusion Error: {e}")
        return generate_themed_image(prompt, style)

def generate_themed_image(prompt: str, style: str = "realistic") -> dict:
    """Generate themed images using Picsum with better categorization"""
    try:
        # Extract keywords from prompt for better image selection
        keywords = prompt.lower().split()
        
        # Map keywords to Picsum categories
        category_map = {
            "nature": ["forest", "mountain", "sea", "ocean", "tree", "flower", "landscape"],
            "urban": ["city", "building", "street", "architecture", "modern"],
            "romantic": ["love", "heart", "romantic", "candle", "wine", "rose"],
            "peaceful": ["calm", "serene", "peaceful", "meditation", "yoga"],
            "energetic": ["sport", "fitness", "dynamic", "energetic", "active"],
            "vintage": ["retro", "vintage", "old", "classic", "nostalgic"],
            "modern": ["modern", "minimalist", "clean", "simple", "contemporary"]
        }
        
        # Find matching category
        selected_category = "nature"  # default
        for category, words in category_map.items():
            if any(word in keywords for word in words):
                selected_category = category
                break
        
        # Use category-specific random seeds for consistent themed images
        category_seeds = {
            "nature": [100, 200, 300, 400, 500],
            "urban": [600, 700, 800, 900, 1000],
            "romantic": [1100, 1200, 1300, 1400, 1500],
            "peaceful": [1600, 1700, 1800, 1900, 2000],
            "energetic": [2100, 2200, 2300, 2400, 2500],
            "vintage": [2600, 2700, 2800, 2900, 3000],
            "modern": [3100, 3200, 3300, 3400, 3500]
        }
        
        seed = random.choice(category_seeds[selected_category])
        
        return {
            "url": f"https://picsum.photos/512/512?random={seed}",
            "prompt": prompt,
            "source": f"Themed {selected_category} image",
            "category": selected_category
        }
        
    except Exception as e:
        print(f"Themed Image Generation Error: {e}")
        return {
            "url": f"https://picsum.photos/512/512?random={random.randint(1000, 9999)}",
            "prompt": prompt,
            "source": "Fallback random image"
        }

@app.get("/")
async def root():
    """Ana endpoint"""
    return {
        "message": "AI Mood Board API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/analyze-mood", response_model=MoodBoardResponse)
async def analyze_mood(request: MoodRequest):
    """Mood analysis and mood board creation"""
    try:
        # AI mood analysis
        mood_analysis = analyze_mood_with_ai(request.description)
        
        # Image suggestions
        images = generate_multiple_images(mood_analysis["keywords"])
        
        # Color palette
        color_palette = MOOD_COLORS.get(mood_analysis["color_palette"], MOOD_COLORS["modern"])
        
        return MoodBoardResponse(
            images=images,
            color_palette=color_palette,
            inspiration_text=mood_analysis["inspiration_text"],
            mood_analysis=mood_analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/images")
async def search_images(query: str, count: int = 5):
    """Image search"""
    try:
        keywords = query.split()
        images = generate_multiple_images(keywords, count)
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image search error: {str(e)}")

@app.post("/api/generate-image")
async def generate_image(request: ImageRequest):
    """AI image generation"""
    try:
        result = generate_ai_image(request.prompt, request.style)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation error: {str(e)}")

@app.post("/api/save-board")
async def save_board(board_data: dict):
    """Save mood board (mock for now)"""
    try:
        # Here a real database save could be done
        return {
            "message": "Mood board saved successfully",
            "board_id": f"board_{random.randint(1000, 9999)}",
            "data": board_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    ) 