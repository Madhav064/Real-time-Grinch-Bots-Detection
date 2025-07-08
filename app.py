from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
from typing import Dict, Optional, List
import json
from fastapi.encoders import jsonable_encoder

# Initialize FastAPI app
app = FastAPI(
    title="Grinch Bot Detector API",
    description="API for detecting bot behavior on e-commerce websites",
    version="1.0.0"
)

# Add CORS middleware to allow requests from Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin (important for local testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the trained model and encoder
try:
    model = joblib.load("rf_bot_model.pkl")
    encoder = joblib.load("scroll_behavior_encoder.pkl")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    encoder = None

# Create a global variable to store the latest session data for Streamlit
latest_session = None

class BehaviorData(BaseModel):
    mouse_movement: float
    typing_speed: float
    click_pattern: float
    time_spent: float
    scroll_behavior: str
    captcha_success: int
    form_fill_time: float

class SessionData(BaseModel):
    mouse_movement_units: float
    typing_speed_cpm: float
    click_pattern_score: float
    time_spent_on_page_sec: float
    scroll_behavior_encoded: int
    captcha_success: int
    form_fill_time_sec: float

class PredictionResponse(BaseModel):
    is_bot: bool
    probability: float
    confidence_metrics: Dict[str, float]
    risk_factors: List[str]

class SessionPredictionResponse(BaseModel):
    is_bot: bool
    probability: float
    confidence_metrics: Dict[str, float]
    risk_factors: List[str]
    session_id: str

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "online", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionResponse)
async def predict_bot(data: BehaviorData):
    """
    Predict whether the behavior is from a bot or human
    """
    if model is None or encoder is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        # Encode scroll behavior
        scroll_encoded = encoder.transform([data.scroll_behavior])[0]

        # Prepare features in the correct order
        features = np.array([[
            data.mouse_movement,
            data.typing_speed,
            data.click_pattern,
            data.time_spent,
            scroll_encoded,
            data.captcha_success,
            data.form_fill_time
        ]])

        # Get prediction and probability
        is_bot = bool(model.predict(features)[0])
        bot_probability = float(model.predict_proba(features)[0][1])

        # Calculate confidence metrics
        confidence_metrics = {
            "mouse_movement_score": min(1.0, data.mouse_movement / 10.0),
            "typing_pattern_score": min(1.0, max(0, 1 - (data.typing_speed / 1000.0))),
            "click_pattern_score": data.click_pattern,
            "time_spent_score": min(1.0, data.time_spent / 30.0)
        }

        # Identify risk factors
        risk_factors = []
        if data.mouse_movement < 2.0:
            risk_factors.append("Unusually low mouse movement")
        if data.typing_speed > 800:
            risk_factors.append("Suspiciously fast typing speed")
        if data.click_pattern < 0.3:
            risk_factors.append("Regular click pattern detected")
        if data.time_spent < 5:
            risk_factors.append("Very short page interaction time")
        if data.captcha_success == 0:
            risk_factors.append("Failed CAPTCHA")
        if data.form_fill_time < 3.0:
            risk_factors.append("Suspiciously quick form filling")

        return PredictionResponse(
            is_bot=is_bot,
            probability=bot_probability,
            confidence_metrics=confidence_metrics,
            risk_factors=risk_factors
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict_session", response_model=SessionPredictionResponse)
async def predict_session(data: SessionData):
    """
    Predict whether a session is from a bot or human
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        # Prepare features in the correct order
        features = np.array([[
            data.mouse_movement_units,
            data.typing_speed_cpm,
            data.click_pattern_score,
            data.time_spent_on_page_sec,
            data.scroll_behavior_encoded,
            data.captcha_success,
            data.form_fill_time_sec
        ]])

        # Get prediction and probability
        is_bot = bool(model.predict(features)[0])
        bot_probability = float(model.predict_proba(features)[0][1])

        # Calculate confidence metrics based on the features
        confidence_metrics = {
            "mouse_movement_score": min(1.0, data.mouse_movement_units / 10.0),
            "typing_pattern_score": min(1.0, max(0, 1 - (data.typing_speed_cpm / 1000.0))),
            "click_pattern_score": data.click_pattern_score,
            "time_spent_score": min(1.0, data.time_spent_on_page_sec / 30.0)
        }

        # Identify risk factors
        risk_factors = []
        if data.mouse_movement_units < 2.0:
            risk_factors.append("Unusually low mouse movement")
        if data.typing_speed_cpm > 800:
            risk_factors.append("Suspiciously fast typing speed")
        if data.click_pattern_score < 0.3:
            risk_factors.append("Regular click pattern detected")
        if data.time_spent_on_page_sec < 5:
            risk_factors.append("Very short page interaction time")
        if data.captcha_success == 0:
            risk_factors.append("Failed CAPTCHA")
        if data.form_fill_time_sec < 3.0:
            risk_factors.append("Suspiciously quick form filling")

        # Generate a unique session ID based on timestamp
        import time
        session_id = f"session_{int(time.time())}"
        
        # Store the session data and results for Streamlit
        global latest_session
        latest_session = {
            "session_id": session_id,
            "timestamp": time.time(),
            "features": {
                "mouse_movement_units": data.mouse_movement_units,
                "typing_speed_cpm": data.typing_speed_cpm,
                "click_pattern_score": data.click_pattern_score,
                "time_spent_on_page_sec": data.time_spent_on_page_sec,
                "scroll_behavior_encoded": data.scroll_behavior_encoded,
                "captcha_success": data.captcha_success,
                "form_fill_time_sec": data.form_fill_time_sec
            },
            "prediction": {
                "is_bot": is_bot,
                "probability": bot_probability,
                "confidence_metrics": confidence_metrics,
                "risk_factors": risk_factors
            }
        }
        
        # Save the session data to a file for persistence
        try:
            with open("latest_session.json", "w") as f:
                json.dump(latest_session, f)
        except Exception as e:
            print(f"Error saving session data: {e}")

        return SessionPredictionResponse(
            is_bot=is_bot,
            probability=bot_probability,
            confidence_metrics=confidence_metrics,
            risk_factors=risk_factors,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session prediction error: {str(e)}")

@app.get("/latest_session")
async def get_latest_session():
    """Get the latest session data for Streamlit app"""
    if latest_session is None:
        try:
            with open("latest_session.json", "r") as f:
                return json.load(f)
        except Exception:
            return {"error": "No session data available"}
    return latest_session

@app.get("/model-info")
async def model_info():
    """Get information about the loaded model"""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    return {
        "model_type": type(model).__name__,
        "features": [
            "mouse_movement_units",
            "typing_speed_cpm",
            "click_pattern_score",
            "time_spent_on_page_sec",
            "scroll_behavior_encoded",
            "captcha_success",
            "form_fill_time_sec"
        ],
        "scroll_behaviors": list(encoder.classes_) if encoder else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
