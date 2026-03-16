import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN Y LIMPIEZA
st.set_page_config(page_title="GO TAXI", page_icon="🚖", layout="centered")

# Estilos CSS
st.markdown("""
    <style>
    .stApp { background-color: #FF8C00; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }

    .brand-title { text-align: center; color: white !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); margin-bottom: 0px; }
    .brand-subtitle { text-align: center; color: black !important; font-weight: bold; font-size: 12px; margin-bottom: 20px; }

    /* Tarjeta Blanca */
    .driver-info {
        background-color: white;
        padding: 12px;
        border-radius: 12px 12px 0 0;
        border-left: 12px solid var(--status-color);
        margin-bottom: -5px;
    }
    .name-bold { font-weight: bold; font-size: 18px; color: black !important; }
    .code-badge { background-color: #eee; padding: 2px 6px; border-radius: 5px; font-size: 12px; color: #555 !important; margin-left: 5px; vertical-align: middle; }
    .phone-small { font-weight: normal; font-size: 13px; color: #666 !important; display: block; margin-top: 2px; }

    /* Expander */
    .stExpander {
        background-color: white !important;
        border: none !important;
        border-radius: 0 0 12px 12px !important;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    }
    .stButton>button { border-radius: 10px !important; height: 45px !important; font-weight: bold !important; }
    .stMarkdown p, .stMarkdown b { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="brand-title">GO TAXI</h1><p class="brand-subtitle">PÍRITU - PORTUGUESA</p>', unsafe_allow_html=True)

try:
    # 2. CONEXIÓN CON LIMPIEZA DE CACHÉ (Para que el orden se actualice al instante)
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # ttl=0 obliga a la app a buscar datos nuevos del Excel cada vez que se refresca
    url = "https://docs.google.com/spreadsheets/d/1ClVwjiaV44TOWysCtqtyjkfAs6TbRMToMT6b7mQWTRc/edit?usp=sharing"
    df = conn.read(spreadsheet=url, ttl=0) 
    
    df.columns = df.columns.str.strip().str.upper()

    # Buscador
    busqueda = st.text_input("", placeholder="🔍 Buscar chofer...")
    if busqueda:
        df = df[df['NOMBRE'].str.contains(busqueda, case=False, na=False)]

    # 3. SECCIONES (El orden de esta lista define qué aparece primero)
    secciones = [
        {"label": "🟢 DISPONIBLES", "key": "Disponible", "color": "#28a745"},
        {"label": "🟡 OCUPADOS", "key": "Ocupado", "color": "#f1c40f"},
        {"label": "🔴 NO LABORANDO", "key": "No Laborando", "color": "#dc3545"}
    ]

    for sec in secciones:
        # Filtramos los choferes que pertenecen a esta sección actual
        grupo = df[df['ESTATUS'] == sec['key']]
        
        if not grupo.empty:
            st.markdown(f"<b style='color: white !important; text-shadow: 1px 1px 2px black;'>{sec['label']}</b>", unsafe_allow_html=True)
            
            for _, fila in grupo.iterrows():
                telf_raw = str(fila['TELEFONO']).split('.')[0]
                telf_fmt = f"+58 {telf_raw[0:3]} {telf_raw[3:6]} {telf_raw[6:]}"
                pago = str(fila['DATOSPAGO']) if pd.notna(fila['DATOSPAGO']) else "Sin datos."
                
                # Obtener el código si existe la columna, si no poner "S/C"
                codigo = str(fila['CODIGO']).split('.')[0] if 'CODIGO' in df.columns else "---"

                # FICHA CON NOMBRE Y CÓDIGO
                st.markdown(f"""
                    <div class="driver-info" style="--status-color: {sec['color']};">
                        <span class="name-bold">{fila['NOMBRE']}</span>
                        <span class="code-badge">#{codigo}</span>
                        <span class="phone-small">{telf_fmt}</span>
                    </div>
                """, unsafe_allow_html=True)

                with st.expander(" "):
                    st.markdown(f"**💳 PAGO MÓVIL:**\n\n{pago}")
                    c1, c2 = st.columns(2)
                    with c1: st.link_button("📞 LLAMAR", f"tel:{telf_raw}", use_container_width=True)
                    with c2: st.link_button("WHATSAPP", f"https://wa.me/58{telf_raw}", use_container_width=True)

    # Botón manual de refrescar por si acaso
    if st.button("🔄 Actualizar Lista"):
        st.rerun()

except Exception as e:
    st.error("Sincronizando...")
