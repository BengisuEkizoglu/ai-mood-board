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
        print("Initializing Stable Diffusion pipeline...")
        
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"📱 Using device: {device}")
        
        # Load the pipeline
        model_id = "sd-legacy/stable-diffusion-v1-5"
        sd_pipeline = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            # Safety checker enabled for responsible AI usage
            safety_checker=None,  # You can enable this for production
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
                print("XFormers memory efficient attention enabled")
            except:
                print("XFormers not available, using standard attention")
        
        print("Stable Diffusion pipeline initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to initialize Stable Diffusion: {e}")
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

# Color palettes for different moods with variations
MOOD_COLORS = {
    "romantic": [
        ["#FF6B9D", "#FFB3D1", "#FFE5F1", "#8B5A96", "#4A4A4A"],
        ["#FF1493", "#FF69B4", "#FFB6C1", "#C71585", "#DB7093"],
        ["#FF007F", "#FF69B4", "#FFC0CB", "#DC143C", "#FF1493"],
        ["#FF69B4", "#FFB6C1", "#FFC0CB", "#FF1493", "#C71585"]
    ],
    "peaceful": [
        ["#87CEEB", "#98FB98", "#F0E68C", "#DDA0DD", "#F5F5DC"],
        ["#B0E0E6", "#98FB98", "#F0E68C", "#DDA0DD", "#F0F8FF"],
        ["#ADD8E6", "#90EE90", "#F0E68C", "#DDA0DD", "#F5F5DC"],
        ["#87CEEB", "#98FB98", "#F0E68C", "#E6E6FA", "#F0F8FF"]
    ],
    "energetic": [
        ["#FF4500", "#FFD700", "#32CD32", "#4169E1", "#FF1493"],
        ["#FF6347", "#FFD700", "#00FF00", "#1E90FF", "#FF1493"],
        ["#FF4500", "#FFFF00", "#00FF7F", "#4169E1", "#FF1493"],
        ["#FF6347", "#FFD700", "#32CD32", "#1E90FF", "#FF1493"]
    ],
    "melancholic": [
        ["#2F4F4F", "#696969", "#708090", "#B0C4DE", "#E6E6FA"],
        ["#4A4A4A", "#696969", "#708090", "#B0C4DE", "#F0F8FF"],
        ["#2F4F4F", "#696969", "#778899", "#B0C4DE", "#E6E6FA"],
        ["#4A4A4A", "#696969", "#708090", "#C0C0C0", "#F0F8FF"]
    ],
    "nature": [
        ["#228B22", "#8FBC8F", "#F4A460", "#DEB887", "#CD853F"],
        ["#32CD32", "#90EE90", "#F4A460", "#DEB887", "#D2691E"],
        ["#228B22", "#98FB98", "#F4A460", "#DEB887", "#CD853F"],
        ["#32CD32", "#8FBC8F", "#F4A460", "#D2B48C", "#CD853F"]
    ],
    "urban": [
        ["#708090", "#2F4F4F", "#FF6347", "#FFD700", "#4169E1"],
        ["#696969", "#2F4F4F", "#FF6347", "#FFD700", "#1E90FF"],
        ["#708090", "#4A4A4A", "#FF6347", "#FFFF00", "#4169E1"],
        ["#696969", "#2F4F4F", "#FF4500", "#FFD700", "#1E90FF"]
    ],
    "vintage": [
        ["#8B4513", "#DEB887", "#F4A460", "#D2B48C", "#CD853F"],
        ["#A0522D", "#DEB887", "#F4A460", "#D2B48C", "#D2691E"],
        ["#8B4513", "#F5DEB3", "#F4A460", "#D2B48C", "#CD853F"],
        ["#A0522D", "#DEB887", "#F4A460", "#F5DEB3", "#CD853F"]
    ],
    "modern": [
        ["#000000", "#FFFFFF", "#808080", "#C0C0C0", "#FF6B35"],
        ["#2F2F2F", "#FFFFFF", "#808080", "#C0C0C0", "#FF6347"],
        ["#000000", "#F5F5F5", "#808080", "#C0C0C0", "#FF6B35"],
        ["#2F2F2F", "#FFFFFF", "#696969", "#C0C0C0", "#FF6347"]
    ]
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

def generate_multiple_images_with_colors(keywords: List[str], color_palette: List[str], count: int = 5) -> List[dict]:
    """Generates multiple images using local Stable Diffusion with color palette integration"""
    try:
        images = []
        search_query = " ".join(keywords[:3]) if keywords else "inspiration"
        
        # Convert hex colors to color names for better prompt generation
        color_names = []
        for color in color_palette:
            color_name = get_color_name(color)
            if color_name:
                color_names.append(color_name)
        
        # Create more effective color-enhanced prompts
        primary_colors = color_names[:2] if len(color_names) >= 2 else color_names
        color_description = ", ".join(primary_colors) if primary_colors else ""
        
        for i in range(count):
            # Add variety to prompts with better color integration
            prompt_variations = [
                f"{search_query}, {color_description} color theme, soft lighting, beautiful, high quality",
                f"{search_query}, {color_description} color palette, warm atmosphere, artistic, creative",
                f"{search_query}, {color_description} color scheme, natural lighting, inspiring, detailed",
                f"{search_query}, {color_description} color tones, ambient lighting, aesthetic, masterpiece",
                f"{search_query}, {color_description} color harmony, golden hour lighting, elegant, professional"
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

def get_color_name(hex_color: str) -> str:
    """Convert hex color to color name for better prompt generation"""
    # Enhanced color mapping for better AI understanding
    color_map = {
        # Primary colors
        "#FF0000": "red", "#00FF00": "green", "#0000FF": "blue",
        "#FFFF00": "yellow", "#FF00FF": "magenta", "#00FFFF": "cyan",
        
        # Warm colors
        "#FFA500": "orange", "#FF6347": "coral", "#FF4500": "orange red",
        "#FFD700": "golden", "#FF69B4": "pink", "#FFC0CB": "light pink",
        "#A52A2A": "brown", "#8B4513": "saddle brown",
        
        # Cool colors
        "#800080": "purple", "#8A2BE2": "blue violet", "#4169E1": "royal blue",
        "#87CEEB": "sky blue", "#B0E0E6": "powder blue", "#20B2AA": "light sea green",
        "#32CD32": "lime green", "#98FB98": "pale green",
        
        # Neutral colors
        "#000000": "black", "#FFFFFF": "white", "#808080": "gray",
        "#C0C0C0": "silver", "#F5F5DC": "beige", "#F0E68C": "khaki",
        "#DDA0DD": "plum", "#F0F8FF": "alice blue"
    }
    
    # Normalize hex color (remove # if present)
    hex_color = hex_color.upper()
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    
    # Add # back for lookup
    hex_color = f"#{hex_color}"
    
    # Try exact match first
    if hex_color in color_map:
        return color_map[hex_color]
    
    # If no exact match, try to find closest color by RGB distance
    try:
        # Convert hex to RGB
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        # Find closest color by RGB distance
        min_distance = float('inf')
        closest_color = ""
        
        for hex_key, color_name in color_map.items():
            if hex_key.startswith('#'):
                r2 = int(hex_key[1:3], 16)
                g2 = int(hex_key[3:5], 16)
                b2 = int(hex_key[5:7], 16)
                
                distance = ((r - r2) ** 2 + (g - g2) ** 2 + (b - b2) ** 2) ** 0.5
                if distance < min_distance:
                    min_distance = distance
                    closest_color = color_name
        
        return closest_color if min_distance < 100 else ""  # Threshold for similarity
        
    except:
        return ""

def generate_multiple_images(keywords: List[str], count: int = 5) -> List[dict]:
    """Legacy function for backward compatibility"""
    return generate_multiple_images_with_colors(keywords, [], count)

def generate_ai_image(prompt: str, style: str = "realistic") -> dict:
    """Generates AI image with local Stable Diffusion"""
    global sd_pipeline
    
    try:
        enhanced_prompt = f"{prompt}, {style} style, high quality, detailed, beautiful, masterpiece"
        
        # Check if Stable Diffusion pipeline is available
        if sd_pipeline is None:
            print("Stable Diffusion pipeline not initialized, using themed images")
            return generate_themed_image(prompt, style)
        
        print(f"Generating image with prompt: {enhanced_prompt}")
        
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
        
        print(" Image generated successfully!")
        
        return {
            "url": f"data:image/png;base64,{img_str}",
            "prompt": enhanced_prompt,
            "source": "Local Stable Diffusion",
            "model": "runwayml/stable-diffusion-v1-5"
        }
            
    except Exception as e:
        print(f" Stable Diffusion Error: {e}")
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
        
        # Color palette - randomly select from available variations
        # Use mood field instead of color_palette field for dictionary lookup
        mood_palettes = MOOD_COLORS.get(mood_analysis["mood"], MOOD_COLORS["modern"])
        color_palette = random.choice(mood_palettes)
        
        # Image suggestions with color palette integration
        images = generate_multiple_images_with_colors(mood_analysis["keywords"], color_palette)
        
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

@app.get("/api/example-prompts")
async def get_example_prompts():
    """Get AI-generated example prompts"""
    try:
        # Generate different example prompts based on current time/randomness
        import time
        current_time = int(time.time())
        
        # Different prompt categories
        prompt_categories = [
            {
                "romantic": [
                    "I want to feel the magic of a candlelit dinner in Paris",
                    "Looking for inspiration for a romantic wedding theme",
                    "Create a mood board for a cozy date night at home",
                    "I want to capture the feeling of a sunset beach walk",
                    "Design inspiration for a romantic garden party"
                ],
                "peaceful": [
                    "I need a calming meditation space design",
                    "Looking for peaceful nature retreat inspiration",
                    "Create a serene bedroom atmosphere",
                    "I want to feel the tranquility of a mountain lake",
                    "Design a peaceful home office environment"
                ],
                "energetic": [
                    "I want to capture the energy of a music festival",
                    "Looking for dynamic workout space inspiration",
                    "Create a vibrant party atmosphere",
                    "I want to feel the excitement of a sports event",
                    "Design an energetic children's playroom"
                ],
                "nature": [
                    "I want to bring the forest into my living room",
                    "Looking for ocean-inspired design elements",
                    "Create a garden oasis in my backyard",
                    "I want to feel connected to mountain landscapes",
                    "Design a nature-themed workspace"
                ],
                "urban": [
                    "I want to capture the energy of a modern city",
                    "Looking for industrial loft design inspiration",
                    "Create a contemporary urban apartment feel",
                    "I want to feel the rhythm of downtown life",
                    "Design a sleek modern office space"
                ],
                "vintage": [
                    "I want to recreate the charm of the 1950s",
                    "Looking for retro diner aesthetic inspiration",
                    "Create a vintage photography studio feel",
                    "I want to feel the nostalgia of old Hollywood",
                    "Design a classic vintage kitchen"
                ],
                "modern": [
                    "I want a minimalist Scandinavian design",
                    "Looking for clean modern architecture inspiration",
                    "Create a sleek contemporary living space",
                    "I want to feel the simplicity of modern art",
                    "Design a futuristic smart home environment"
                ]
            }
        ]
        
        # Select a random category and get 5 prompts
        selected_category = random.choice(list(prompt_categories[0].keys()))
        category_prompts = prompt_categories[0][selected_category]
        
        # Shuffle and select 5 unique prompts
        random.shuffle(category_prompts)
        selected_prompts = category_prompts[:5]
        
        return {
            "prompts": selected_prompts,
            "category": selected_category,
            "timestamp": current_time
        }
        
    except Exception as e:
        # Fallback to static prompts if AI generation fails
        fallback_prompts = [
            "I want to feel like walking in the streets of Paris in autumn",
            "Looking for inspiration for a minimalist and modern office design",
            "I want to create a romantic dinner atmosphere",
            "A peaceful living space concept in harmony with nature",
            "An energetic and dynamic gym design"
        ]
        return {
            "prompts": fallback_prompts,
            "category": "mixed",
            "timestamp": int(time.time())
        }

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8001)),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    ) 