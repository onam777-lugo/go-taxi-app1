import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración visual
st.set_page_config(page_title="GO TAXI", page_icon="🚖")
st.markdown("<h1 style='text-align: center;'>🚖 GO TAXI - Píritu</h1>", unsafe_allow_html=True)
st.write("### Tu transporte seguro en Portuguesa")

# 1. Conexión a tu Excel
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# 2. Ordenar por Estatus (Disponible arriba)
# Usamos los nombres exactos de tu captura: NOMBRE, TELEFONO, ESTATUS
orden_prioridad = {'Disponible': 1, 'Ocupado': 2, 'No Laborando': 3}
df['Orden'] = df['ESTATUS'].map(orden_prioridad).fillna(4)
df = df.sort_values('Orden')

# 3. Colores
colores = {'Disponible': '#28a745', 'Ocupado': '#dc3545', 'No Laborando': '#6c757d'}

# 4. Crear las tarjetas
for _, fila in df.iterrows():
    color = colores.get(fila['ESTATUS'], '#000000')
    
    st.markdown(f"""
        <div style="border-left: 10px solid {color}; padding: 15px; margin-bottom: 15px; border-radius: 10px; background-color: #f0f2f6;">
            <h3 style="margin:0;">👤 Chófer: {fila['NOMBRE']}</h3>
            <p style="color: {color}; font-weight: bold; font-size: 1.2rem; margin: 5px 0;">📍 Estatus: {fila['ESTATUS']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Botón de llamada
    st.link_button(f"📞 LLAMAR AHORA", f"tel:{fila['TELEFONO']}", use_container_width=True)
