import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Gestion de Manufactura", page_icon="🏭", layout="wide")

DB_MATERIA = "db_materia_prima.csv"
DB_PRODUCTOS = "db_productos.csv"
DB_VENTAS = "db_ventas.csv"

CODIGO_ADMIN = "1234"
CODIGO_EMPLEADO = "5678"

FORMULAS = {
    "Mesa de Centro Minimalista": {
        "Madera de Pino": 1,
        "Barniz Ecologico": 0.5
    },
    "Silla Nordica": {
        "Madera de Pino": 0.5,
        "Barniz Ecologico": 0.2
    }
}

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
        df["Inversion Total ($)"] = df["Cantidad"] * df["Costo Unitario ($)"]
    return df

def guardar_datos():
    st.session_state.materia_prima = normalizar_numericos(
        st.session_state.materia_prima,
        ["Cantidad", "Costo Unitario ($)", "Inversion Total ($)"]
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

if "materia_prima" not in st.session_state:
    st.session_state.materia_prima = cargar_datos(DB_MATERIA, [
        {"Material": "Madera de Pino", "Cantidad": 150.0, "Costo Unitario ($)": 45.0, "Inversion Total ($)": 6750.0},
        {"Material": "Barniz Ecologico", "Cantidad": 20.0, "Costo Unitario ($)": 120.0, "Inversion Total ($)": 2400.0}
    ])
    st.session_state.materia_prima = normalizar_numericos(st.session_state.materia_prima, ["Cantidad", "Costo Unitario ($)", "Inversion Total ($)"])
    st.session_state.materia_prima = recalcular_inversion_material(st.session_state.materia_prima)

if "productos_fabricados" not in st.session_state:
    st.session_state.productos_fabricados = cargar_datos(DB_PRODUCTOS, [
        {"Producto": "Mesa de Centro Minimalista", "Stock Disponible": 12},
        {"Producto": "Silla Nordica", "Stock Disponible": 34}
    ])
    st.session_state.productos_fabricados = normalizar_numericos(st.session_state.productos_fabricados, ["Stock Disponible"])

if "ventas" not in st.session_state:
    st.session_state.ventas = cargar_datos(DB_VENTAS, [
        {"Producto": "Mesa de Centro Minimalista", "Unidades Vendidas": 25, "Total Venta ($)": 48750.0},
        {"Producto": "Silla Nordica", "Unidades Vendidas": 80, "Total Venta ($)": 63200.0}
    ])
    st.session_state.ventas = normalizar_numericos(st.session_state.ventas, ["Unidades Vendidas", "Total Venta ($)"])

if "rol" not in st.session_state:
    st.session_state.rol = None

if "menu_seleccionado" not in st.session_state:
    st.session_state.menu_seleccionado = "Panel de Control"

st.markdown('''
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
    h1, h2, h3, p, span, label, .stMetric div {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: space-around !important;
        align-items: center !important;
        width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        width: 100% !important;
        min-width: 0 !important;
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
    </style>
''', unsafe_allow_html=True)

if not st.session_state.rol:
    st.markdown('''
        <style>
        .login-box { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-top: 18vh; margin-bottom: 25px; }
        .avatar { width: 100px; height: 100px; border: 4px solid #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
        .avatar::before { content: "👤"; font-size: 50px; color: #ffffff; }
        div[data-testid="stTextInput"] {
            max-width: 280px !important;
            margin: 0 auto !important;
        }
        div[data-testid="stTextInput"] > div { 
            background-color: #111111 !important; 
            border: 1px solid #333333 !important; 
            border-radius: 20px !important; 
        }
        div[data-testid="stTextInput"] input { 
            color: #ffffff !important; 
            text-align: center !important; 
            font-size: 16px !important; 
        }
        div[data-testid="stTextInput"] label { display: none !important; }
        </style>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="login-box"><div class="avatar"></div></div>', unsafe_allow_html=True)
    codigo_ingresado = st.text_input("Ingreso", type="password", placeholder="🔒 Digite el codigo...")

    if codigo_ingresado:
        if codigo_ingresado == CODIGO_ADMIN:
            st.session_state.rol = "Administrador"
            st.session_state.menu_seleccionado = "Panel de Control"
            st.rerun()
        elif codigo_ingresado == CODIGO_EMPLEADO:
            st.session_state.rol = "Empleado"
            st.session_state.menu_seleccionado = "Taller de Fabricacion"
            st.rerun()
        else:
            st.markdown("<p style='text-align:center; color:#ff4b4b; font-size:14px; margin-top:15px;'>Codigo incorrecto</p>", unsafe_allow_html=True)

else:
    if st.session_state.rol == "Administrador":
        opciones = [
            {"name": "Panel de Control", "icon": "📊", "label": "Panel"},
            {"name": "Almacen", "icon": "📦", "label": "Almacen"},
            {"name": "Taller de Fabricacion", "icon": "🔨", "label": "Taller"},
            {"name": "Ventas", "icon": "💰", "label": "Ventas"},
            {"name": "Capacitacion", "icon": "▶️", "label": "Videos"}
        ]
    else:
        opciones = [
            {"name": "Taller de Fabricacion", "icon": "🔨", "label": "Taller"},
            {"name": "Capacitacion", "icon": "▶️", "label": "Videos"}
        ]

    cols_nav = st.columns(len(opciones))
    
    for idx, opt in enumerate(opciones):
        with cols_nav[idx]:
            es_act = st.session_state.menu_seleccionado == opt["name"]
            opacidad = "opacity: 1.0; font-weight: bold; color: #ffffff;" if es_act else "opacity: 0.3; color: #888888;"
            
            st.markdown(f"""
                <div style='text-align: center; margin-bottom: -5px; {opacidad}'>
                    <span style='font-size: 24px;'>{opt["icon"]}</span><br>
                    <span style='font-size: 9px; font-family: sans-serif; white-space: nowrap;'>{opt["label"]}</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown('''
                <style>
                div[data-testid="stHorizontalBlock"] button {
                    background-color: transparent !important;
                    border: none !important;
                    color: transparent !important;
                    height: 40px !important;
                    margin-top: -45px !important;
                    position: relative !important;
                    z-index: 10 !important;
                }
                div[data-testid="stHorizontalBlock"] button:hover {
                    background-color: transparent !important;
                    border: none !important;
                }
                </style>
            ''', unsafe_allow_html=True)
            
            if st.button("", key=f"nav_{opt['name']}"):
                st.session_state.menu_seleccionado = opt["name"]
                st.rerun()

    st.markdown("<hr style='border: 1px solid #111111; margin-top: 15px; margin-bottom: 20px;'>", unsafe_allow_html=True)

    if st.session_state.menu_seleccionado == "Panel de Control" and st.session_state.rol == "Administrador":
        st.subheader("Panel de Control")
