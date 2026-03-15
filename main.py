import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(page_title="GO TAXI", page_icon="🚖")

st.title("🚖 GO TAXI - Píritu")
st.markdown("---")

# 1. Conexión a los datos
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read()

# 2. Lógica de Ordenamiento (Esto es lo que pediste)
orden_prioridad = {'Disponible': 1, 'Ocupado': 2, 'No Laborando': 3}
df['Orden'] = df['ESTATUS'].map(orden_prioridad).fillna(4)
df = df.sort_values('Orden')

# 3. Colores por Estatus
colores = {
    'Disponible': '#28a745',    # Verde
    'Ocupado': '#dc3545',       # Rojo
    'No Laborando': '#6c757d'    # Gris
}

# 4. Crear las tarjetas visuales
for _, fila in df.iterrows():
    color = colores.get(fila['ESTATUS'], '#000000')
    
    with st.container():
        # Tarjeta con color dinámico
        st.markdown(f"""
            <div style="border-left: 8px solid {color}; padding: 15px; margin-bottom: 10px; border-radius: 10px; background-color: #f8f9fa; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                <h3 style="margin:0; color: #333;">{fila['NOMBRE']}</h3>
                <p style="color: {color}; font-weight: bold; font-size: 1.2rem; margin: 5px 0;">● {fila['ESTATUS']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón de llamada
        st.link_button(f"📞 LLAMAR A {fila['NOMBRE']}", f"tel:{fila['TELEFONO']}", use_container_width=True)
        st.markdown("---")
