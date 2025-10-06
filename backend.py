import os
import requests
import itertools
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Chat Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
API_KEY = os.getenv("API_KEY")
API_URL = os.getenv("API_URL", "https://openrouter.ai/api/v1/chat/completions")

# List of models to cycle through
MODELS = [
    "meta-llama/llama-3.3-70b-instruct",
    "meta-llama/llama-3.3-8b-instruct",
    "qwen/qwen2.5-72b-instruct",
    "qwen/qwen2.5-32b-instruct",
    "mistralai/mistral-7b-instruct-v0.2",
    "google/gemma-2-9b-it",
]

# Create a cycle iterator for models
model_cycle = itertools.cycle(MODELS)
current_model = next(model_cycle)

# Request model
class ChatRequest(BaseModel):
    message: str
    history: list = []

# Response model
class ChatResponse(BaseModel):
    response: str
    model_used: str

@app.get("/")
async def root():
    return {"status": "AI Chat Backend is running"}

@app.get("/models")
async def get_models():
    return {"models": MODELS, "current_model": current_model}

@app.get("/ask/{message}")
async def ask_direct(message: str):
    """Direct API endpoint that can be accessed via a URL link"""
    global current_model
    
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API_KEY not configured")
    
    # Prepare headers for OpenRouter API
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Create a simple message without history
    messages = [{"role": "user", "content": message}]
    
    # Try each model until one succeeds
    for _ in range(len(MODELS)):
        try:
            logger.info(f"Trying model: {current_model}")
            
            # Prepare payload for OpenRouter
            payload = {
                "model": current_model,
                "messages": messages,
                "max_tokens": 1024
            }
            
            # Make request to OpenRouter
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=30  # 30-second timeout
            )
            
            # Check if request was successful
            response.raise_for_status()
            data = response.json()
            
            # Extract the response text
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return {"response": content, "model_used": current_model}
            else:
                raise HTTPException(status_code=500, detail="Invalid response format from API")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error with model {current_model}: {str(e)}")
            # Try the next model
            current_model = next(model_cycle)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            # Try the next model
            current_model = next(model_cycle)
    
    # If all models failed
    raise HTTPException(status_code=503, detail="All models failed to respond")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    global current_model
    
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API_KEY not configured")
    
    # Prepare headers for OpenRouter API
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Convert history to OpenRouter format and add the new message
    messages = []
    for entry in request.history:
        if "user" in entry:
            messages.append({"role": "user", "content": entry["user"]})
        if "assistant" in entry:
            messages.append({"role": "assistant", "content": entry["assistant"]})
    
    # Add the current message
    messages.append({"role": "user", "content": request.message})
    
    # Try each model until one succeeds
    for _ in range(len(MODELS)):
        try:
            logger.info(f"Trying model: {current_model}")
            
            # Prepare payload for OpenRouter
            payload = {
                "model": current_model,
                "messages": messages,
                "max_tokens": 1024
            }
            
            # Make request to OpenRouter
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=30  # 30-second timeout
            )
            
            # Check if request was successful
            response.raise_for_status()
            data = response.json()
            
            # Extract the response text
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"]
                return ChatResponse(response=content, model_used=current_model)
            else:
                raise HTTPException(status_code=500, detail="Invalid response format from API")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error with model {current_model}: {str(e)}")
            # Try the next model
            current_model = next(model_cycle)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            # Try the next model
            current_model = next(model_cycle)
    
    # If all models failed
    raise HTTPException(status_code=503, detail="All models failed to respond")

@app.get("/sleep")
async def sleep_mode():
    """Endpoint to put the app to sleep (useful for free tier hosting)"""
    return {"status": "App is now in sleep mode. Send a request to wake it up."}

@app.get("/wake")
async def wake_mode():
    """Endpoint to wake the app from sleep mode"""
    return {"status": "App is now awake and ready to use!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", os.getenv("BACKEND_PORT", 8000)))
    uvicorn.run("backend:app", host="0.0.0.0", port=port, reload=True)