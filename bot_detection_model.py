import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('bot_human_behavior.csv')

# Preprocess the data
# Convert scroll_behavior to numerical values
le = LabelEncoder()
df['scroll_behavior_encoded'] = le.fit_transform(df['scroll_behavior'])

# Prepare features and target
features = ['mouse_movement_units', 'typing_speed_cpm', 'click_pattern_score', 
           'time_spent_on_page_sec', 'scroll_behavior_encoded', 'captcha_success', 
           'form_fill_time_sec']
X = df[features]
y = df['is_bot']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# Make predictions
y_pred = rf_model.predict(X_test)

# Print model performance
print("\nModel Performance Report:")
print("------------------------")
print(classification_report(y_test, y_pred))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': features,
    'importance': rf_model.feature_importances_
})
feature_importance = feature_importance.sort_values('importance', ascending=False)

# Plot feature importance
plt.figure(figsize=(10, 6))
sns.barplot(x='importance', y='feature', data=feature_importance)
plt.title('Feature Importance in Bot Detection')
plt.savefig('feature_importance.png')
plt.close()

# Create a function for real-time prediction
def predict_bot_probability(mouse_movement, typing_speed, click_pattern, 
                          time_spent, scroll_behavior, captcha_success, form_fill_time):
    # Convert scroll_behavior to encoded value
    scroll_encoded = le.transform([scroll_behavior])[0]
    
    # Create feature array
    features_dict = {
        'mouse_movement_units': [mouse_movement],
        'typing_speed_cpm': [typing_speed],
        'click_pattern_score': [click_pattern],
        'time_spent_on_page_sec': [time_spent],
        'scroll_behavior_encoded': [scroll_encoded],
        'captcha_success': [captcha_success],
        'form_fill_time_sec': [form_fill_time]
    }
    features_df = pd.DataFrame(features_dict)
    
    # Get probability of being a bot
    return rf_model.predict_proba(features_df)[0][1]

# Example usage
print("\nExample Prediction:")
print("------------------")
example = predict_bot_probability(
    mouse_movement=5.0,    # Low mouse movement
    typing_speed=1000.0,   # High typing speed
    click_pattern=0.1,     # Low click pattern score
    time_spent=2.0,        # Short time spent
    scroll_behavior='none', # No scrolling
    captcha_success=0,     # Failed captcha
    form_fill_time=2.0     # Quick form fill
)
print(f"Probability of being a bot: {example:.2%}") 


import joblib
joblib.dump(rf_model, "rf_bot_model.pkl")
joblib.dump(le, "scroll_behavior_encoder.pkl")
print("✅ Model and encoder saved successfully!")
