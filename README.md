# Grinch Bot Detection on E-commerce Website

## Overview

**Grinch Bot Detection** is a full-stack project designed to detect and analyze bot-like behavior on e-commerce websites. It consists of a Chrome extension for real-time user behavior monitoring, a Python backend for ML-based bot detection, and a Streamlit dashboard for visualization and analysis.

---

## Features

- **Chrome Extension**: Monitors user sessions (mouse, typing, clicks, scroll, etc.) from "add to cart" to "purchase".
- **Backend (FastAPI)**: Receives session data, runs a trained ML model, and returns bot/human predictions.
- **Streamlit Dashboard**: Visualizes live session results, supports batch CSV analysis, and allows manual session analysis.
- **Feature Importance**: Visualizes which behaviors are most indicative of bots.

---

## Project Structure

```
bot detection on e-commerce website/
├── app.py                        # FastAPI backend server
├── bot_detection_model.py        # (Optional) Model training script
├── grinch_bot_streamlit.py       # Streamlit dashboard
├── requirements.txt              # Python dependencies
├── rf_bot_model.pkl              # Trained Random Forest model
├── scroll_behavior_encoder.pkl   # Label encoder for scroll behavior
├── feature_importance.png        # Feature importance plot
├── bot_human_behavior.csv        # Example dataset
├── grinch-bot-extension/         # Chrome extension source
│   ├── background.js
│   ├── content.js
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   └── images/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
└── ...
```

---

## Setup Instructions

### 1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd "bot detection on e-commerce website"
```

### 2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Start the Backend Server**
```bash
python app.py
```
- The FastAPI server will run at `http://localhost:8000`.

### 4. **Start the Streamlit Dashboard**
```bash
streamlit run grinch_bot_streamlit.py
```
- The dashboard will be available at `http://localhost:8501`.

### 5. **Load the Chrome Extension**
1. Open Chrome and go to `chrome://extensions`.
2. Enable **Developer mode**.
3. Click **Load unpacked** and select the `grinch-bot-extension` folder.
4. The "Grinch Bot Detector" icon should appear in your browser toolbar.

---

## Usage

### **Live Session Monitoring**
1. Go to any e-commerce website.
2. Click the extension icon and select **Start Monitoring Session**.
3. Perform actions (add to cart, checkout, purchase).
4. The extension collects behavioral data and sends it to the backend.
5. View real-time results in the Streamlit dashboard under **Live Session Monitoring**.

### **Batch Prediction**
- Upload a CSV file with session data in the dashboard's **Batch Prediction** tab to analyze multiple sessions at once.

### **Single Session Analysis**
- Manually enter session metrics in the dashboard's **Single Session Analysis** tab to get an instant prediction.

---

## File Explanations

### **Chrome Extension**
- `manifest.json`: Extension configuration and permissions.
- `background.js`: Handles background tasks, badge updates, and session state.
- `content.js`: Injected into web pages; tracks user behavior and sends data to backend.
- `popup.html` / `popup.js`: User interface for starting/stopping monitoring and viewing results.
- `images/`: Extension icons.

### **Backend**
- `app.py`: FastAPI server; receives data, runs ML model, returns predictions.
- `rf_bot_model.pkl`: Trained Random Forest model for bot detection.
- `scroll_behavior_encoder.pkl`: Label encoder for scroll behavior feature.

### **Streamlit Dashboard**
- `grinch_bot_streamlit.py`: Interactive dashboard for live, batch, and manual analysis.
- `feature_importance.png`: Visualizes which features are most important for detection.

### **Data & Model**
- `bot_human_behavior.csv`: Example dataset for training/testing.
- `bot_detection_model.py`: (Optional) Script for training the ML model.

---

## Customization & Development
- **Model Training**: Use `bot_detection_model.py` to retrain or improve the ML model.
- **Extension Logic**: Modify `content.js` to track additional behaviors or improve feature extraction.
- **Dashboard**: Customize `grinch_bot_streamlit.py` for new visualizations or analytics.

---

## License
MIT License (or your preferred license)

---

## Credits
- Developed by [Your Name]
- Special thanks to open-source contributors and the Streamlit, FastAPI, and Chrome Extension communities.