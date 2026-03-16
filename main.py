import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="GO TAXI PÍRITU", page_icon="logo.jpg", layout="centered")

# 2. CONEXIÓN AL EXCEL
url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. CARGA DE DATOS (Con valores de respaldo para evitar errores)
try:
    # Leemos choferes
    df = conn.read(spreadsheet=url, worksheet="Sheet1", ttl=0)
    # Leemos la tarifa de la hoja CONFIG
    df_config = conn.read(spreadsheet=url, worksheet="CONFIG", ttl=0)
    tarifa_val = str(df_config.iloc[0, 1])
except Exception:
    df = pd.DataFrame()
    tarifa_val = "Consultar"

# 4. DISEÑO VISUAL (Naranja y Negro)
st.markdown(f"""
    <style>
    .stApp {{ background-color: #FF8C00; }}
    .banner-tarifa {{
        background-color: black;
        color: #FF8C00;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        border: 2px solid white;
        margin-bottom: 20px;
    }}
    .driver-card {{
        background-color: #FEE0C0;
        padding: 15px;
        border-radius: 12px;
        border-left: 10px solid #28a745;
        margin-bottom: 10px;
        color: black;
    }}
    </style>
    """, unsafe_allow_html=True)

# Encabezado con Tarifa
st.markdown(f"""
    <div class="banner-tarifa">
        <h2 style="margin:0; color:white; font-size:16px;">GO TAXI PÍRITU</h2>
        <p style="margin:0; font-size:12px; color: #bbb;">TARIFA MÍNIMA HOY</p>
        <b style="font-size:28px;">Bs. {tarifa_val}</b>
    </div>
    """, unsafe_allow_html=True)

# 5. LISTADO DE CHOFERES
if not df.empty:
    # Limpiamos nombres de columnas por si acaso
    df.columns = df.columns.str.strip().str.upper()
    
    # Filtramos solo los que están "Disponible"
    if 'ESTATUS' in df.columns:
        disponibles = df[df['ESTATUS'].str.contains('Disponible', case=False, na=False)]
        
        if not disponibles.empty:
            st.markdown("<p style='color:white; font-weight:bold;'>🚖 Unidades en Línea:</p>", unsafe_allow_html=True)
            for _, fila in disponibles.iterrows():
                with st.container():
                    st.markdown(f"""
                        <div class="driver-card">
                            <b style="font-size:18px;">{fila['NOMBRE']}</b><br>
                            <span>📱 {fila['TELEFONO']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    with st.expander("VER OPCIONES DE PAGO Y LLAMAR"):
                        st.code(fila.get('DATOSPAGO', 'Consultar al chofer'), language=None)
                        st.link_button(f"Llamar a {fila['NOMBRE']}", f"tel:{fila['TELEFONO']}", use_container_width=True)
        else:
            st.warning("No hay unidades disponibles en este momento.")
else:
    st.info("Sincronizando con la central de choferes...")

st.markdown('<p style="text-align:center; color:white; font-size:10px; margin-top:30px;">Workflow Designer Onam</p>', unsafe_allow_html=True)
