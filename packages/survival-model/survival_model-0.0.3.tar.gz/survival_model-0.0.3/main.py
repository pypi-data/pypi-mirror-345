import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

import gradio as gr
import pickle
from typing import Union
import numpy as np
import pandas as pd
import os

from survival_model.config.core import TRAINED_MODEL_DIR, config
from survival_model import __version__ as _version

def load_model():
    save_file_name = f"{config.app_config_.pipeline_save_file}{_version}.pkl"
    model_path = TRAINED_MODEL_DIR / save_file_name
    if os.path.exists(model_path):
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        return model
    else:
        raise FileNotFoundError(f"Model file {model_path} not found")
    

# Load the model
try:
    model = load_model()
    model_loaded = True
except Exception as e:
    print(f"Error loading model: {e}")
    model_loaded = False
    model = None
    

def predict_death_event(age, anaemia, creatinine_phosphokinase, diabetes,
       ejection_fraction, high_blood_pressure, platelets,
       serum_creatinine, serum_sodium, sex, smoking, time) -> int:
    
    if not model_loaded:
        return "Model not loaded. Please check if the model file exists."
    
    
    """Make a prediction using a saved model """

    input_data = {
        'age': [age],
        'anaemia': [anaemia],
        'creatinine_phosphokinase': [creatinine_phosphokinase],
        'diabetes': [diabetes],
        'ejection_fraction': [ejection_fraction],
        'high_blood_pressure': [high_blood_pressure],
        'platelets': [platelets],
        'serum_creatinine': [serum_creatinine],
        'serum_sodium': [serum_sodium],
        'sex': [sex],
        'smoking': [smoking],
        'time': [time]
    }

    input_df = pd.DataFrame(input_data)
    
    try:
        # Make prediction
        prediction = model.predict(input_df)[0]
        print("Prediction:", prediction)
        return f"${prediction:,.2f}"
    except Exception as e:
        return f"Error making prediction: {str(e)}"


# Create the Gradio interface
with gr.Blocks(title="Patient Survival Prediction") as demo:
    gr.Markdown("# Patient Survival Prediction Model")
    gr.Markdown("Enter patient information to predict survival possiblity.")
    
    with gr.Row():
        with gr.Column():
            age = gr.Slider(minimum=10.0, maximum=100.0, step=1, value=65.0, label="Age")
            anaemia = gr.Radio(choices=[0, 1], label="Anaemia", value=0)
            creatinine_phosphokinase = gr.Slider(minimum=1, maximum=10000, step=1, value=160, label="Creatinine phosphokinase")
            diabetes = gr.Radio(choices=[0, 1], label="Diabetes", value=1)
            ejection_fraction = gr.Slider(minimum=0, maximum=100, step=1, value=20, label="Ejection fraction")
            high_blood_pressure = gr.Radio(choices=[0, 1], label="High blood pressure", value=0)
            platelets = gr.Number(label="Platelets", value=327000.00)
            serum_creatinine = gr.Slider(minimum=0, maximum=10, step=0.1, value=2.7, label="Serum Creatinine")
            serum_sodium = gr.Slider(minimum=100, maximum=200, step=1, value=116, label="Serum Sodium")
            sex = gr.Radio(choices=[0, 1], label="Sex", value=0)
            smoking = gr.Radio(choices=[0, 1], label="Smoking", value=0)
            time = gr.Slider(minimum=1, maximum=50, step=1, value=8, label="Follow-up period (days)")
            submit_btn = gr.Button("Predict Survival", variant="primary")
        
        with gr.Column():
            output = gr.Textbox(label="DEATH_EVENT", placeholder="Prediction result will be shown here.", interactive=False)
            
    # Set up the prediction on button click
    submit_btn.click(
        fn=predict_death_event,
        inputs=[age, anaemia, creatinine_phosphokinase, diabetes,
            ejection_fraction, high_blood_pressure, platelets,
            serum_creatinine, serum_sodium, sex, smoking, time],
        outputs=output
    )
    
# Launch the app
if __name__ == "__main__":
    demo.launch(share=True, debug=True, server_name="0.0.0.0")