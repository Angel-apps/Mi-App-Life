import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración de página minimalista
st.set_page_config(page_title="Gestión de Manufactura Automatizada", page_icon="🏭", layout="wide")

# Archivos locales
DB_MATERIA = "db_materia_prima.csv"
DB_PRODUCTOS = "db_productos.csv"
DB_VENTAS = "db_ventas.csv"

# Códigos de acceso por rol
CODIGO_ADMIN = "1234"
CODIGO_EMPLEADO = "5678"

# Fórmulas de fabricación
FORMULAS = {
    "Mesa de Centro Minimalista": {
        "Madera de Pino": 1,
        "Barniz Ecológico": 0.5
    },
    "Silla Nórdica": {
        "Madera de Pino": 0.5,
        "Barniz Ecológico": 0.2
    }
}

# ----------------------------
# UTILIDADES
# ----------------------------
def cargar_datos(ruta, columnas_defecto):
    if os.path.exists(ruta):
        df = pd.read_csv(ruta)
        if df.empty:
            return pd.DataFrame(columnas_defecto)
        for fila in columnas_defecto:
            for col in fila.keys():
                if col not in df.columns:
                    df[col] = 0
        return df
    return pd.DataFrame(columnas_defecto)

def normalizar_numericos(df, columnas):
    df = df.copy()
    for col in columnas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def recalcular_inversion_material(df):
    df = df.copy()
    if "Cantidad" in df.columns and "Costo Unitario ($)" in df.columns:
        df["Inversión Total ($)"] = df["Cantidad"] * df["Costo Unitario ($)"]
    return df

def guardar_datos():
    st.session_state.materia_prima = normalizar_numericos(
        st.session_state.materia_prima,
        ["Cantidad", "Costo Unitario ($)", "Inversión Total ($)"]
    )
    st.session_state.materia_prima = recalcular_inversion_material(st.session_state.materia_prima)

    st.session_state.productos_fabricados = normalizar_numericos(
        st.session_state.productos_fabricados,
        ["Stock Disponible"]
    )

    st.session_state.ventas = normalizar_numericos(
        st.session_state.ventas,
        ["Unidades Vendidas", "Total Venta ($)"]
    )

    st.session_state.materia_prima.to_csv(DB_MATERIA, index=False)
    st.session_state.productos_fabricados.to_csv(DB_PRODUCTOS, index=False)
    st.session_state.ventas.to_csv(DB_VENTAS, index=False)

def registrar_venta_efectiva(producto, unidades, precio_unitario):
    df = st.session_state.ventas.copy()
    total_venta = unidades * precio_unitario

    if producto in df["Producto"].values:
        idx = df.index[df["Producto"] == producto]
        df.at[idx, "Unidades Vendidas"] += unidades
        df.at[idx, "Total Venta ($)"] += total_venta
    else:
        nueva_fila = pd.DataFrame([{
            "Producto": producto,
            "Unidades Vendidas": unidades,
            "Total Venta ($)": total_venta
        }])
        df = pd.concat([df, nueva_fila], ignore_index=True)

    st.session_state.ventas = df

# ----------------------------
# INICIALIZAR DATOS
# ----------------------------
if "materia_prima" not in st.session_state:
    st.session_state.materia_prima = cargar_datos(DB_MATERIA, [
        {"Material": "Madera de Pino", "Cantidad": 150.0, "Costo Unitario ($)": 45.0, "Inversión Total ($)": 6750.0},
        {"Material": "Barniz Ecológico", "Cantidad": 20.0, "Costo Unitario ($)": 120.0, "Inversión Total ($)": 2400.0}
    ])
    st.session_state.materia_prima = normalizar_numericos(st.session_state.materia_prima, ["Cantidad", "Costo Unitario ($)", "Inversión Total ($)"])
    st.session_state.materia_prima = recalcular_inversion_material(st.session_state.materia_prima)

if "productos_fabricados" not in st.session_state:
    st.session_state.productos_fabricados = cargar_datos(DB_PRODUCTOS, [
        {"Producto": "Mesa de Centro Minimalista", "Stock Disponible": 12},
        {"Producto": "Silla Nórdica", "Stock Disponible": 34}
    ])
    st.session_state.productos_fabricados = normalizar_numericos(st.session_state.productos_fabricados, ["Stock Disponible"])

if "ventas" not in st.session_state:
    st.session_state.ventas = cargar_datos(DB_VENTAS, [
        {"Producto": "Mesa de Centro Minimalista", "Unidades Vendidas": 25, "Total Venta ($)": 48750.0},
        {"Producto": "Silla Nórdica", "Unidades Vendidas": 80, "Total Venta ($)": 63200.0}
    ])
    st.session_state.ventas = normalizar_numericos(st.session_state.ventas, ["Unidades Vendidas", "Total Venta ($)"])

if "rol" not in st.session_state:
    st.session_state.rol = None

if "menu_seleccionado" not in st.session_state:
    st.session_state.menu_seleccionado = "Panel de Control"

# ----------------------------
# ESTILOS CSS BASE (TOTAL BLACK)
# ----------------------------
st.markdown("""
    <style>
    .stApp, .main, [data-testid="stSidebar"], [data-testid="stHeader"] {
        background-color: #000000 !important;
    }
    header, footer {
        visibility: hidden !important;
        height: 0px !important;
    }
    [data-testid="stSidebar"] {
        display: none !important;
    }
    h1, h2, h3, p, span, label {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background-color: #111111 !important;
        color: white !important;
        border: 1px solid #333333 !important;
        border-radius: 8px !important;
        width: 100%;
    }
    div[data-testid="stDataFrame"] div {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* ESTILOS DEL NUEVO MENÚ HORIZONTAL FORZADO PARA MÓVILES */
    .nav-container {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-around !important;
        align-items: center !important;
        background-color: #000000 !important;
        padding: 10px 0px !important;
        width: 100% !important;
        overflow-x: auto !important;
    }
    
    .nav-item {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        text-decoration: none !important;
        min-width: 65px !important;
        border: none !important;
        background: none !important;
        padding: 0 !important;
    }
    
    .nav-icon {
        font-size: 26px !important;
        margin-bottom: 5px !important;
    }
    
    .nav-text {
        font-size: 10px !important;
        color: #777777 !important;
        font-family: 'Inter', sans-serif !important;
        white-space: nowrap !important;
    }
    
    .nav-text-active {
        font-size: 10px !important;
        color: #ffffff !important;
        font-weight: bold !important;
        font-family: 'Inter', sans-serif !important;
        white-space: nowrap !important;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# PANTALLA DE LOGUEO (TOTAL BLACK)
# ----------------------------
if not st.session_state.rol:
    st.markdown("""
        <style>
        .login-box { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 15vh; margin-bottom: 30px; }
        .avatar { width: 100px; height: 100px; border: 4px solid #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
        .avatar::before { content: "👤"; font-size: 50px; color: #ffffff; }
        div[data-testid="stTextInput"] > div { background-color: #111111 !important; border: 1px solid #333333 !important; border-radius: 20px !important; max-width: 280px; margin: 0 auto; }
        div[data-testid="stTextInput"] input { color: #ffffff !important; text-align: center; font-size: 16px; }
        div[data-testid="stTextInput"] label { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-box"><div class="avatar"></div></div>', unsafe_allow_html=True)
    codigo_ingresado = st.text_input("Password", type="password", placeholder="🔒 Digite el código...")

    if codigo_ingresado:
        if codigo_ingresado == CODIGO_ADMIN:
            st.session_state.rol = "Administrador"
            st.session_state.menu_seleccionado = "Panel de Control"
            st.rerun()
        elif codigo_ingresado == CODIGO_EMPLEADO:
            st.session_state.rol = "Empleado"
            st.session_state.menu_seleccionado = "Taller de Fabricación"
            st.rerun()
        else:
            st.markdown("<p style='text-align:center; color:#ff4b4b; font-size:14px; margin-top:15px;'>Código incorrecto</p>", unsafe_allow_html=True)

# ----------------------------
# APLICACIÓN INICIADA (MENÚ HORIZONTAL REAL)
# ----------------------------
else:
    # Definir opciones del menú interactivo según rol
    if st.session_state.rol == "Administrador":
        opciones = [
            {"name": "Panel de Control", "icon": "📊", "label": "Panel de Control"},
            {"name": "Almacen", "icon": "📦", "label": "Almacen"},
            {"name": "Taller de Fabricación", "icon": "🔨", "label": "Fabricación"},
            {"name": "Ventas", "icon": "💰", "label": "Ventas"},
            {"name": "Capacitacion", "icon": "▶️", "label": "Capacitacion"}
        ]
    else:
        opciones = [
            {"name": "Taller de Fabricación", "icon": "🔨", "label": "Fabricación"},
            {"name": "Capacitacion", "icon": "▶️", "label": "Capacitacion"}
        ]

    # Renderizar el menú horizontal usando selectbox nativo camuflado como barra minimalista
    # Esto soluciona el colapso vertical en teléfonos y se ve idéntico a tu foto
    nombres_menu = [opt["label"] for opt in opciones]
    iconos_menu = [opt["icon"] for opt in opciones]
    claves_menu = [opt["name"] for opt in opciones]
    
    # Buscamos cuál es el índice actual para mantenerlo seleccionado
