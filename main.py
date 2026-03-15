import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(page_title="GO TAXI", page_icon="🚖")

st.markdown("<h1 style='text-align: center; color: #f1c40f;'>🚖 GO TAXI - Píritu</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Selecciona un conductor disponible</p>", unsafe_allow_html=True)

# 1. Conexión a los datos
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()

    # 2. Ordenar por Estatus (Disponible primero)
    orden_prioridad = {'Disponible': 1, 'Ocupado': 2, 'No Laborando': 3}
    df['Orden'] = df['ESTATUS'].map(orden_prioridad).fillna(4)
    df = df.sort_values('Orden')

    # 3. Colores por Estatus
    colores = {
        'Disponible': '#28a745',    # Verde
        'Ocupado': '#dc3545',       # Rojo
        'No Laborando': '#6c757d'    # Gris
    }

    # 4. Mostrar las tarjetas de conductores
    for _, fila in df.iterrows():
        color = colores.get(fila['ESTATUS'], '#000000')
        telf = str(fila['TELEFONO']).replace(".0", "") # Limpiar el número si viene de Excel
        
        # Tarjeta visual
        st.markdown(f"""
            <div style="border-left: 10px solid {color}; padding: 15px; margin-bottom: 5px; border-radius: 10px; background-color: #f8f9fa; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                <h3 style="margin:0; color: #333;">{fila['NOMBRE']}</h3>
                <p style="color: {color}; font-weight: bold; margin: 5px 0;">● {fila['ESTATUS']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Botones de contacto en dos columnas
        col1, col2 = st.columns(2)
        with col1:
            st.link_button(f"📞 LLAMAR", f"tel:{telf}", use_container_width=True)
        with col2:
            # Enlace de WhatsApp con mensaje predeterminado
            st.link_button(f"💬 WHATSAPP", f"https://wa.me/{telf}?text=Hola,%20necesito%20un%20servicio%20de%20GO%20TAXI", use_container_width=True)
        
        st.markdown("---")

except Exception as e:
    st.error("Conectando con la base de datos... Por favor espera o verifica la configuración.")
