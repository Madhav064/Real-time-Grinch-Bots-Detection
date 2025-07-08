import streamlit as st
import pandas as pd
import joblib
import requests
import json
import time
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Set page configuration first
st.set_page_config(page_title="Grinch Bot Detector", layout="wide")

# Force dark theme and adjust padding
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stFileUploader {
        padding: 1rem;
        border: 1px dashed #4CAF50;
        border-radius: 5px;
        background-color: rgba(76, 175, 80, 0.1);
    }
    .stForm {
        padding: 1rem;
        border: 1px solid #2196F3;
        border-radius: 5px;
        background-color: rgba(33, 150, 243, 0.1);
    }
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    div.stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Load trained model and encoder
try:
    rf_model = joblib.load("rf_bot_model.pkl")
    le = joblib.load("scroll_behavior_encoder.pkl")
    model_loaded = True
except Exception as e:
    st.error(f"Error loading model: {e}")
    model_loaded = False

# Set title and description
st.title("🛡️ Grinch Bot Detection Dashboard")
st.markdown("""
Welcome to the Grinch Bot Detector! Monitor real-time e-commerce sessions, upload batch data, or analyze individual sessions.
""")

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["📊 Live Session Monitoring", "📂 Batch Prediction", "🔍 Single Session Analysis"])

# Tab 1: Live Session Monitoring
with tab1:
    st.header("📊 Live Session Monitoring")
    st.markdown("""
    This section shows real-time data from the Chrome extension monitoring. 
    Start a session in the extension and complete a purchase flow to see results here.
    """)
    
    # Create a container for the session data
    session_container = st.container()
    
    # Add auto-refresh option
    auto_refresh = st.checkbox("Auto-refresh (every 5 seconds)", value=True)
    
    # Function to fetch latest session data
    def fetch_latest_session():
        try:
            response = requests.get("http://localhost:8000/latest_session")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            st.error(f"Error connecting to API: {e}")
            return None
    
    # Display latest session data
    def display_session_data(session_data):
        if not session_data or "error" in session_data:
            st.info("No active session data available. Start a session using the Chrome extension.")
            return
        
        # Extract data
        session_id = session_data.get("session_id", "Unknown")
        timestamp = session_data.get("timestamp", 0)
        features = session_data.get("features", {})
        prediction = session_data.get("prediction", {})
        
        # Create two columns
        col1, col2 = st.columns(2)
        
        # Session info in left column
        with col1:
            st.subheader("Session Information")
            st.markdown(f"**Session ID:** {session_id}")
            st.markdown(f"**Timestamp:** {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Create metrics visualization
            st.subheader("Session Metrics")
            metrics_df = pd.DataFrame({
                "Metric": [
                    "Mouse Movement",
                    "Typing Speed",
                    "Click Pattern",
                    "Time Spent",
                    "Scroll Behavior",
                    "CAPTCHA Success",
                    "Form Fill Time"
                ],
                "Value": [
                    f"{features.get('mouse_movement_units', 0):.2f} units",
                    f"{features.get('typing_speed_cpm', 0):.0f} CPM",
                    f"{features.get('click_pattern_score', 0):.2f}",
                    f"{features.get('time_spent_on_page_sec', 0):.1f} seconds",
                    str(features.get('scroll_behavior_encoded', 0)),
                    "Yes" if features.get('captcha_success', 0) == 1 else "No",
                    f"{features.get('form_fill_time_sec', 0):.1f} seconds"
                ]
            })
            st.table(metrics_df)
        
        # Prediction results in right column
        with col2:
            st.subheader("Prediction Results")
            
            # Bot probability as a gauge chart
            bot_probability = prediction.get("probability", 0)
            fig, ax = plt.subplots(figsize=(4, 0.5))
            ax.barh([0], [bot_probability], color='red')
            ax.barh([0], [1-bot_probability], left=[bot_probability], color='green')
            ax.set_xlim(0, 1)
            ax.set_ylim(-0.5, 0.5)
            ax.set_yticks([])
            ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
            ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
            ax.set_title(f'Bot Probability: {bot_probability*100:.1f}%')
            st.pyplot(fig)
            
            # Bot or human classification
            is_bot = prediction.get("is_bot", False)
            if is_bot:
                st.error("⚠️ This session is likely a BOT!")
            else:
                st.success("✅ This session is likely HUMAN.")
            
            # Risk factors
            risk_factors = prediction.get("risk_factors", [])
            if risk_factors:
                st.subheader("Risk Factors")
                for factor in risk_factors:
                    st.warning(factor)
            
            # Confidence metrics
            st.subheader("Confidence Metrics")
            confidence_metrics = prediction.get("confidence_metrics", {})
            if confidence_metrics:
                metrics_data = {
                    "Metric": list(confidence_metrics.keys()),
                    "Confidence": [f"{v*100:.0f}%" for v in confidence_metrics.values()]
                }
                st.table(pd.DataFrame(metrics_data))
    
    # Main display function
    def update_session_display():
        with session_container:
            latest_session = fetch_latest_session()
            display_session_data(latest_session)
    
    # Initial display
    update_session_display()
    
    # Auto-refresh logic
    if auto_refresh:
        refresh_placeholder = st.empty()
        refresh_placeholder.info("Auto-refreshing...")
        time.sleep(5)  # Wait 5 seconds
        refresh_placeholder.empty()  # Remove the message
        st.rerun()  # Rerun the app

# Tab 2: Batch Prediction via CSV Upload
with tab2:
    try:
        st.write("Batch Prediction tab loaded")
        st.header("📂 Batch Prediction via CSV Upload")
        # Sample data display for guidance
        st.subheader("Expected CSV Format")
        sample_df = pd.DataFrame({
            'mouse_movement_units': [5.23, 12.45, 0.75],
            'typing_speed_cpm': [65.2, 120.5, 500.2],
            'click_pattern_score': [0.75, 0.82, 0.12],
            'time_spent_on_page_sec': [125.3, 45.2, 12.5],
            'scroll_behavior': ['normal', 'minimal', 'rapid'],
            'captcha_success': [1, 1, 0],
            'form_fill_time_sec': [15.3, 12.1, 2.5]
        })
        st.dataframe(sample_df)
        st.markdown("---")
        st.subheader("Upload Your CSV File")
        st.markdown("""
        Please upload a CSV file containing session data with the columns shown above.
        The file should contain at least the following columns:
        - `mouse_movement_units`
        - `typing_speed_cpm`
        - `click_pattern_score`
        - `time_spent_on_page_sec`
        - `scroll_behavior`
        - `captcha_success`
        - `form_fill_time_sec`
        """)
        with st.container():
            uploaded_file = st.file_uploader(
                "Choose a CSV file", 
                type=["csv"], 
                help="Upload a CSV file with the required columns"
            )
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"File uploaded successfully: {uploaded_file.name}")
                required_cols = ['mouse_movement_units', 'typing_speed_cpm', 'click_pattern_score',
                               'time_spent_on_page_sec', 'scroll_behavior', 'captcha_success', 
                               'form_fill_time_sec']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    st.error(f"Missing required columns: {', '.join(missing_cols)}")
                    st.stop()
                else:
                    st.write("Preview of uploaded data:")
                    st.dataframe(df.head())
                    if model_loaded:
                        with st.spinner('Processing data...'):
                            try:
                                df['scroll_behavior_encoded'] = le.transform(df['scroll_behavior'])
                                feature_cols = ['mouse_movement_units', 'typing_speed_cpm', 'click_pattern_score',
                                              'time_spent_on_page_sec', 'scroll_behavior_encoded',
                                              'captcha_success', 'form_fill_time_sec']
                                df['Bot Probability (%)'] = rf_model.predict_proba(df[feature_cols])[:, 1] * 100
                                df['Is Bot'] = rf_model.predict(df[feature_cols]).astype(bool)
                                st.success("✅ Predictions Completed")
                                st.subheader("Prediction Results")
                                display_cols = ['mouse_movement_units', 'typing_speed_cpm', 'click_pattern_score',
                                              'time_spent_on_page_sec', 'scroll_behavior', 'captcha_success',
                                              'form_fill_time_sec', 'Bot Probability (%)', 'Is Bot']
                                st.dataframe(df[display_cols])
                                st.subheader("Summary Visualizations")
                                col1, col2 = st.columns(2)
                                with col1:
                                    fig, ax = plt.subplots(figsize=(6, 6))
                                    bot_count = df['Is Bot'].sum()
                                    human_count = len(df) - bot_count
                                    ax.pie([human_count, bot_count], 
                                          labels=['Human', 'Bot'], 
                                          autopct='%1.1f%%', 
                                          colors=['#4CAF50', '#F44336'],
                                          startangle=90)
                                    ax.set_title('Detection Results')
                                    st.pyplot(fig)
                                with col2:
                                    fig, ax = plt.subplots(figsize=(6, 6))
                                    ax.hist(df['Bot Probability (%)'], bins=10, color='#2196F3')
                                    ax.set_xlabel('Bot Probability (%)')
                                    ax.set_ylabel('Count')
                                    ax.set_title('Probability Distribution')
                                    st.pyplot(fig)
                            except Exception as e:
                                st.error(f"Error processing data: {str(e)}")
                    else:
                        st.error("Model not loaded. Cannot make predictions.")
            except Exception as e:
                st.error(f"Error reading CSV file: {str(e)}")
        else:
            st.info("Please upload a CSV file to proceed with batch prediction.")
    except Exception as e:
        st.error(f"Error in Batch Prediction tab: {e}")

# Tab 3: Single Session Analysis
with tab3:
    try:
        st.write("Single Session Analysis tab loaded")
        st.header("🔍 Single Session Analysis")
        if not model_loaded:
            st.error("Model not loaded. Cannot make predictions.")
        else:
            st.markdown("""
            Enter session metrics to analyze a single user session. This helps you determine if a 
            particular shopping session exhibits bot-like or human-like behavior.
            """)
            with st.form("session_analysis_form", clear_on_submit=False):
                st.markdown("### Enter Session Metrics")
                col1, col2 = st.columns(2)
                with col1:
                    mouse_movement = st.number_input("Mouse Movement Units", 
                                                  min_value=0.0, 
                                                  max_value=1000.0, 
                                                  value=5.0,
                                                  help="Total units of mouse movement during session")
                    typing_speed = st.number_input("Typing Speed (CPM)", 
                                                min_value=0.0, 
                                                max_value=5000.0, 
                                                value=250.0,
                                                help="Characters typed per minute")
                    click_pattern = st.number_input("Click Pattern Score", 
                                                 min_value=0.0, 
                                                 max_value=1.0, 
                                                 value=0.5,
                                                 help="Randomness of click patterns (0=regular, 1=random)")
                    time_spent = st.number_input("Time Spent on Page (seconds)", 
                                              min_value=0.0, 
                                              max_value=3600.0, 
                                              value=60.0,
                                              help="Total time spent on the page")
                with col2:
                    scroll_behavior = st.selectbox("Scroll Behavior", 
                                                options=le.classes_,
                                                help="Type of scrolling behavior observed")
                    captcha_success = st.selectbox("CAPTCHA Success", 
                                                options=[1, 0],
                                                format_func=lambda x: "Yes" if x == 1 else "No",
                                                help="Whether CAPTCHA was completed successfully")
                    form_fill_time = st.number_input("Form Fill Time (seconds)", 
                                                  min_value=0.0, 
                                                  max_value=300.0, 
                                                  value=10.0,
                                                  help="Time taken to fill out forms")
                submit_button = st.form_submit_button("Analyze Session", use_container_width=True)
            if submit_button:
                try:
                    with st.spinner('Analyzing session data...'):
                        scroll_encoded = le.transform([scroll_behavior])[0]
                        features = np.array([[
                            mouse_movement,
                            typing_speed,
                            click_pattern,
                            time_spent,
                            scroll_encoded,
                            captcha_success,
                            form_fill_time
                        ]])
                        is_bot = bool(rf_model.predict(features)[0])
                        bot_probability = float(rf_model.predict_proba(features)[0][1])
                        st.markdown("### Analysis Results")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Bot Probability", f"{bot_probability * 100:.2f}%")
                            if is_bot:
                                st.error("⚠️ This session is likely a BOT!")
                            else:
                                st.success("✅ This session is likely HUMAN.")
                            fig, ax = plt.subplots(figsize=(4, 0.5))
                            ax.barh([0], [bot_probability], color='red')
                            ax.barh([0], [1-bot_probability], left=[bot_probability], color='green')
                            ax.set_xlim(0, 1)
                            ax.set_ylim(-0.5, 0.5)
                            ax.set_yticks([])
                            ax.set_xticks([0, 0.25, 0.5, 0.75, 1])
                            ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
                            st.pyplot(fig)
                        with col2:
                            st.markdown("### Risk Analysis")
                            risk_factors = []
                            if mouse_movement < 2.0:
                                risk_factors.append("Unusually low mouse movement")
                            if typing_speed > 800:
                                risk_factors.append("Suspiciously fast typing speed")
                            if click_pattern < 0.3:
                                risk_factors.append("Regular click pattern detected")
                            if time_spent < 5:
                                risk_factors.append("Very short page interaction time")
                            if captcha_success == 0:
                                risk_factors.append("Failed CAPTCHA")
                            if form_fill_time < 3.0:
                                risk_factors.append("Suspiciously quick form filling")
                            if risk_factors:
                                for factor in risk_factors:
                                    st.warning(factor)
                            else:
                                st.info("No specific risk factors identified")
                        st.markdown("### Feature Contributions")
                        feature_names = ['Mouse Movement', 'Typing Speed', 'Click Pattern',
                                      'Time Spent', 'Scroll Behavior', 'CAPTCHA Success', 
                                      'Form Fill Time']
                        importances = rf_model.feature_importances_
                        fig, ax = plt.subplots(figsize=(10, 5))
                        y_pos = np.arange(len(feature_names))
                        ax.barh(y_pos, importances, align='center')
                        ax.set_yticks(y_pos)
                        ax.set_yticklabels(feature_names)
                        ax.invert_yaxis()
                        ax.set_xlabel('Importance')
                        ax.set_title('Feature Importance')
                        st.pyplot(fig)
                except Exception as e:
                    st.error(f"Error analyzing session: {str(e)}")
    except Exception as e:
        st.error(f"Error in Single Session Analysis tab: {e}")

# Add information about the Chrome extension
st.sidebar.title("Grinch Bot Detector")
st.sidebar.image("grinch-bot-extension/images/icon128.png", width=100)
st.sidebar.markdown("""
## How to Use
1. Install the Chrome extension
2. Browse an e-commerce website
3. Click "Start Monitoring Session" in the extension
4. Complete a purchase flow (add to cart → checkout → purchase)
5. View results here in real-time

## Features Monitored
- Mouse movement patterns
- Typing speed and rhythm
- Click patterns
- Time spent on page
- Scrolling behavior
- Form filling speed
- CAPTCHA success rate
""")

# Add model information
st.sidebar.markdown("---")
st.sidebar.subheader("Model Information")
st.sidebar.markdown(f"Model Type: Random Forest")
st.sidebar.markdown("Feature Importance")
st.sidebar.image("feature_importance.png", width=300)
