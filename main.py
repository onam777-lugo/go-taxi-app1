import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
import pytz

# 1. CONFIGURACIÓN DE LA APP
st.set_page_config(
    page_title="GO TAXI", 
    page_icon="logo.jpg", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. DISEÑO DE INTERFAZ PREMIUM
st.markdown("""
    <style>
    header, [data-testid="stHeader"], .stAppHeader {
        display: none !important;
        visibility: hidden !important;
    }
    
    .stApp {
        background-color: #FF8C00;
        margin-top: -30px !important;
    }

    #MainMenu, footer { visibility: hidden; }
    
    .block-container { 
        padding-top: 1rem !important; 
        max-width: 450px !important; 
    }

    .brand-title { 
        text-align: center; 
        color: white !important; 
        text-shadow: 2px 2px 5px rgba(0,0,0,0.4); 
        margin-bottom: -10px; 
        font-size: 42px; 
        font-weight: 900; 
        padding-top: 80px;
    }
    .brand-subtitle { 
        text-align: center; 
        color: black !important; 
        font-weight: 800; 
        font-size: 14px; 
        letter-spacing: 2px; 
        margin-bottom: 25px; 
    }

    .tarifa-container {
        background-color: rgba(0, 0, 0, 0.5); 
        color: white; 
        padding: 8px 12px; 
        border-radius: 12px; 
        text-align: center; 
        margin-bottom: 25px; 
        border: 1px solid rgba(255,255,255,0.1);
        width: 50%; 
        margin-left: auto; 
        margin-right: auto;
    }

    /* ESTILO DE TARJETAS CON BARRA DINÁMICA */
    .driver-card {
        background: linear-gradient(145deg, #FEE0C0, #f7d4b0);
        padding: 0px !important; 
        border-radius: 15px; 
        margin-bottom: 15px; 
        box-shadow: 4px 4px 10px rgba(0,0,0,0.15);
        display: flex;
        overflow: hidden;
        border: none !important;
        position: relative;
        z-index: 2; /* Para que esté por encima del expander */
    }
    
    .status-bar {
        width: 14px; 
        min-height: 100%;
    }

    .card-info {
        padding: 15px;
        flex-grow: 1;
    }
    
    .name-text { font-weight: 800; font-size: 20px; color: #1a1a1a !important; display: block; }
    .code-tag { background-color: black; color: #FF8C00 !important; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: bold; margin-left: 5px; }
    
    /* CORRECCIÓN DE LAS ESQUINAS DEL BOTÓN DE DESPLIEGUE */
    .stExpander { 
        background-color: #FEE0C0 !important; 
        border: none !important; 
        border-radius: 0 0 15px 15px !important; 
        margin-top: -25px; /* Sube para pegarse a la tarjeta */
        margin-bottom: 20px; 
        margin-left: 5px; /* Reduce ancho para que no sobresalga */
        margin-right: 5px;
        z-index: 1;
    }
    
    .stExpander details { border: none !important; }
    .stExpander p { color: #FF8C00 !important; font-weight: 800 !important; text-transform: uppercase; }
    .stExpander svg { fill: #FF8C00 !important; }
    .stButton>button { border-radius: 12px !important; height: 50px !important; font-weight: 700 !important; text-transform: uppercase; }
    
    .install-box {
        background-color: rgba(255,255,255,0.2
        
