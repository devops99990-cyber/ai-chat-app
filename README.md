# 🧠 AI Chat App — Streamlit + FastAPI + OpenRouter Integration

A fully functional AI chat application built using Streamlit (frontend) and FastAPI (backend), connected to the OpenRouter API for access to multiple state-of-the-art language models.

## 🚀 Features

- **Model Auto-Rotation System**: Automatically retries the next model when one fails
- **Seamless Frontend–Backend Communication**: Streamlit interacts with FastAPI using HTTP requests
- **Multi-Model Support**: Easily customizable by adding or removing models in the MODELS list
- **Timeout & Error Handling**: Prevents app freezes with built-in request timeout logic
- **Portable Deployment**: Can run locally or be deployed on cloud platforms

## 🧩 Supported Models

- 🦙 Meta LLaMA 3.3 (70B, 8B)
- 🧠 Qwen 2.5 (32B, 72B)
- 🌪️ Mistral (7B)
- 💎 Google Gemma 2 (9B)

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8 or higher
- OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))

### Installation

1. Clone this repository or download the files
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your environment variables by editing the `.env` file:

```
API_KEY=your_openrouter_api_key_here
API_URL=https://openrouter.ai/api/v1/chat/completions
BACKEND_PORT=8000
BACKEND_URL=http://localhost:8000
```

## 🚀 Running the Application

### Start the Backend Server

```bash
uvicorn backend:app --host 0.0.0.0 --port 8000 --reload
```

### Start the Frontend

```bash
streamlit run frontend.py
```

The application will be available at:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000

## 🌍 Deployment Options

### Local Development
Run both servers locally as described above.

### Free 24/7 Hosting on Render.com

You can host this application for free on Render.com with these simple steps:

1. **Create a Render account**
   - Sign up at [render.com](https://render.com) (no credit card required)

2. **Deploy the Backend**
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository or use "Deploy from Git Repo"
   - Enter your repository URL
   - Name: `myai-backend` (or any name you prefer)
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend:app --host 0.0.0.0 --port $PORT`
   - Plan: Select the `Free` tier

3. **Set Environment Variables**
   - In your Render dashboard, go to the web service you just created
   - Navigate to "Environment" tab
   - Add the following environment variables:
     - `API_KEY`: Your OpenRouter API key
     - `API_URL`: https://openrouter.ai/api/v1/chat/completions

4. **Access Your App**
   - Once deployed, Render will provide a URL like `https://myai-backend.onrender.com`
   - You can access your AI directly through:
     - `https://myai-backend.onrender.com/ask/your_question_here`

5. **Start/Stop Your App Anytime**
   - To manually sleep the app: Visit `https://myai-backend.onrender.com/sleep`
   - To wake it up: Visit `https://myai-backend.onrender.com/wake`
   - You can also pause/resume from the Render dashboard

> **Note**: Free tier on Render has some limitations:
> - The app will sleep after 15 minutes of inactivity
> - Limited to 750 hours of runtime per month
> - Automatically wakes up when receiving a request

### Other Cloud Options
- **Railway**: Similar to Render with a free tier
- **Netlify**: Host only the frontend, while the backend runs on Render or Railway

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| API Gateway | OpenRouter |
| Programming Language | Python |
| Deployment | Render / Netlify / Railway |
| Libraries | requests, itertools, uvicorn |

## 🔄 How It Works

1. User enters a message in Streamlit chat
2. Streamlit sends the request to the FastAPI backend at `/chat`
3. The backend picks the next available OpenRouter model from the list
4. If the model fails (e.g., 401 error), it automatically switches to the next one
5. The AI response is sent back to Streamlit and displayed in the chat

## 🧠 Future Enhancements

- Add session memory for contextual conversations
- Integrate voice input/output using Speech APIs
- Allow user model selection from dropdown
- Add database logging for conversation history