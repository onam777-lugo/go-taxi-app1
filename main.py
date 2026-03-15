import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración de la aplicación
st.set_page_config(page_title="GO TAXI", page_icon="🚖")
st.markdown("<h1 style='text-align: center;'>🚖 GO TAXI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Tu transporte seguro en Portuguesa</h3>", unsafe_allow_html=True)

# 1. Conexión a la hoja de Google (Asegúrate de configurar los Secrets en Streamlit)
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# 2. Ordenar por Estatus (Disponible primero)
# Usamos los nombres exactos de tu Excel: NOMBRE, TELEFONO, ESTATUS
orden_prioridad = {'Disponible': 1, 'Ocupado': 2, 'No Laborando': 3}
df['Orden'] = df['ESTATUS'].map(orden_prioridad).fillna(4)
df = df.sort_values('Orden')

# 3. Colores por Estatus
colores = {
    'Disponible': '#28a745',    # Verde
    'Ocupado': '#dc3545',       # Rojo
    'No Laborando': '#6c757d'    # Gris
}

# 4. Mostrar las tarjetas
for _, fila in df.iterrows():
    color = colores.get(fila['ESTATUS'], '#000000')
    
    st.markdown(f"""
        <div style="border-left: 10px solid {color}; padding: 15px; margin-bottom: 10px; border-radius: 10px; background-color: #f8f9fa; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            <h3 style="margin:0; color: #333;">👤 {fila['NOMBRE']}</h3>
            <p style="color: {color}; font-weight: bold; font-size: 1.1rem; margin: 5px 0;">● {fila['ESTATUS']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Botón para llamar
    st.link_button(f"📞 LLAMAR AHORA", f"tel:{fila['TELEFONO']}", use_container_width=True)
    st.markdown("---")

