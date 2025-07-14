# 🛡️ Real-Time Bot Detection System for E-Commerce

## 📖 Project Overview

During high-traffic holiday seasons, e-commerce websites face attacks from **Grinch Bots** – automated scripts that purchase high-demand items faster than any human customer. These bots resell items at inflated prices or manipulate demand by hoarding products, leading to unfair user experiences and revenue loss.

Our solution is a **real-time bot detection system** that identifies and blocks bots during checkout, ensuring purchases are completed only by genuine users.

---

## 🔍 Problem Statement

- Grinch Bots dominate checkout processes during flash sales.
- Human customers lose access to products.
- Businesses face inventory issues and reputational damage.

---

## 🔑 Solution Summary

We built a modular system with:

- 🖥️ **E-commerce Website** (user interface)
- ⚙️ **Backend API** (handles session data)
- 🧠 **ML Model Backend** (classifies human vs. bot)
- 📊 **Admin Dashboard** (live monitoring)

The system uses machine learning models trained on a Kaggle dataset to analyze session data and predict bot activity. If a bot is detected, the system blocks payment and logs the attempt.

---

## 🔗 Live Demo Links

| Component             | Link                                                                                            |
| --------------------- | ----------------------------------------------------------------------------------------------- |
| 🛒 E-commerce Website | [walmart-dp.vercel.app](https://walmart-dp.vercel.app/)                                         |
| 🔗 Backend API        | [walmart-app.onrender.com](https://walmart-app.onrender.com)                                    |
| 🤖 ML Model Backend   | [bot-detector-model-backend.onrender.com](https://bot-detector-model-backend.onrender.com)      |
| 📊 Admin Dashboard    | [bot-detector-model-dashboard.onrender.com](https://bot-detector-model-dashboard.onrender.com/) |

---

## 🏗️ System Architecture

### 📐 Architecture Diagram



### 🔄 Data Flow Diagram



1. **Session Tracking** – Tracks user behavior: clicks, navigation, response times.
2. **Data Transfer** – Frontend sends session data to backend API.
3. **Classification** – ML backend evaluates data and predicts user type.
4. **Action** – Human: Payment processed; Bot: Payment blocked and flagged.
5. **Live Monitoring** – Admin dashboard shows detection results in real time.

---

## 📊 Dataset

- **Source:** [IRCTC Bot Detection Dataset (Kaggle)](https://www.kaggle.com/datasets/subradeepdas02/irctc-bot-detection-dataset)
- **Features Used:**
  - Session duration
  - Number of clicks
  - Time between requests
  - Navigation depth
  - Response time

---

## 🛠️ Tech Stack

| Component        | Technology           |
| ---------------- | -------------------- |
| Frontend         | Next.js              |
| Backend API      | Node.js, Express.js  |
| ML Model Backend | Python, Fastapi      |
| Dashboard        | Streamlit            |
| Bot Simulation   | Python               |
| ML Libraries     | Scikit-learn, Pandas |

---

## 🌟 Key Features

- ⏱️ Real-time detection and prevention.
- 🛠️ Custom Grinch Bot simulator for testing.
- 📊 Dashboard with live detection results.
- 🔄 Modular architecture for easy scaling.

---

## 👥 Team Contributions

| Name              | Role                        |
| ----------------- | --------------------------- |
| Madhav Raj Sharma | Detection System & ML Model |
| Dilpreet Singh    | E-commerce Website Developer|
| Ayush Karn        | Grinch Bot Developer [(Link to Repo)](https://github.com/AyushKarn69/grinch-bot)        |

---

## 🚀 Future Improvements

- Dockerize all components for scalable deployment.
- Integrate CAPTCHA fallback for flagged users.
- Collect live traffic data to enhance model accuracy.
- Add integration with payment gateways for direct blocking.

---

## ⚙️ Installation (For Developers)

1. **Clone Repository**

```bash
git clone https://github.com/<your-username>/bot-detection-system.git
cd bot-detection-system
```

2. **Frontend**

```bash
cd frontend
npm install
npm run dev
```

3. **Backend API**

```bash
cd backend
npm install
npm start
```

4. **ML Model Backend**

```bash
cd ml-backend
pip install -r requirements.txt
python app.py
```

5. **Dashboard**

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

---

## Deployment

### 1. Configure Environment Variables

Create a `.env` file in the project root (see example below):

```
API_HOST=0.0.0.0
API_PORT=8000
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8501
MODEL_PATH=bot_detection_model.pkl
ENCODER_PATH=label_encoder.pkl
BACKEND_API_URL=http://localhost:8000
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run FastAPI Backend

```bash
uvicorn app:app --host %API_HOST% --port %API_PORT%
```

### 4. Run Streamlit Dashboard

```bash
streamlit run grinch_bot_streamlit.py --server.port %DASHBOARD_PORT% --server.address %DASHBOARD_HOST%
```

- The dashboard will connect to the backend using the `BACKEND_API_URL` specified in `.env`.
- You can deploy these on separate servers/services for scalability and security.

---

## Usage

| Method | Endpoint       | Description                            |
| ------ | -------------- | -------------------------------------- |
| POST   | `/api/detect`  | Sends session data for classification. |
| GET    | `/api/results` | Fetches real-time detection results.   |

---

## 🏅 Recognition

Built for Walmart Sparkathon to solve a real-world problem of unfair e-commerce practices during high-demand events.
