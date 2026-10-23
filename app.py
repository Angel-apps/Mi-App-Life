import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración de página
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
        # Asegurar columnas necesarias
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

# ----------------------------
# CSS
# ----------------------------
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    h1, h2, h3 { color: #1e1e24; font-family: 'Inter', sans-serif; font-weight: 600; }
    .stButton>button { background-color: #1e1e24; color: white; border-radius: 6px; border: none; padding: 0.5rem 1rem; }
    .card { background: white; padding: 20px; border-radius: 8px; border: 1px solid #f0f0f0; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# SIDEBAR Y ACCESO
# ----------------------------
with st.sidebar:
    st.markdown("### 🔐 Acceso al Sistema")
    codigo_ingresado = st.text_input("Introduce tu código:", type="password")

    if codigo_ingresado == CODIGO_ADMIN:
        rol = "Administrador"
        st.success("Acceso: Administrador 👑")
    elif codigo_ingresado == CODIGO_EMPLEADO:
        rol = "Empleado"
        st.success("Acceso: Empleado 🛠️")
    else:
        rol = None
        if codigo_ingresado != "":
            st.error("Código incorrecto")

    st.markdown("---")

    if rol == "Administrador":
        opciones_menu = ["📈 Dashboard General", "📦 Almacén Materia Prima", "🔨 Taller de Fabricación", "💰 Registrar Venta", "📚 Videos de Capacitación"]
    elif rol == "Empleado":
        opciones_menu = ["🔨 Taller de Fabricación", "📚 Videos de Capacitación"]
    else:
        opciones_menu = []

    if rol:
        menu = st.radio("Navegación:", opciones_menu)

    st.markdown("<small>Circuito Local Automatizado v2.5</small>", unsafe_allow_html=True)

# ----------------------------
# PANTALLAS
# ----------------------------
if not rol:
    st.title("🏭 Control de Producción Local")
    st.info("Coloca tu código en la barra lateral para desbloquear tus herramientas de trabajo.")
else:
    # 1. DASHBOARD GENERAL (Administrador)
    if menu == "📈 Dashboard General":
        st.title("Análisis de Inversión y Ventas")
        total_ventas = st.session_state.ventas["Total Venta ($)"].sum()
        total_inversion = st.session_state.materia_prima["Inversión Total ($)"].sum()

        col1, col2 = st.columns(2)
        with col1: st.metric("Ventas Totales Registradas", f"${total_ventas:,.2f}")
        with col2: st.metric("Costo Total Invertido en Materia Prima", f"${total_inversion:,.2f}")

        st.markdown("### 📊 Gráfico Analítico: Ventas Totales por Producto")
        fig = px.bar(st.session_state.ventas, x="Producto", y="Total Venta ($)", text="Total Venta ($)", color="Producto", color_discrete_sequence=["#1e1e24", "#5c5c6d"])
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", showlegend=False)
        fig.update_traces(texttemplate='$%{text:,.2f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # 2. ALMACÉN MATERIA PRIMA (Administrador)
    elif menu == "📦 Almacén Materia Prima":
        st.title("Inventario de Materia Prima e Inversión")
        with st.form("form_mp"):
            mat = st.text_input("Nombre del Material:")
            cant = st.number_input("Cantidad que ingresa:", min_value=0.0, step=1.0)
            costo = st.number_input("Costo Unitario ($):", min_value=0.0)

            if st.form_submit_button("Registrar Entrada") and mat:
                df = st.session_state.materia_prima
                existente = df["Material"] == mat

                if existente.any():
                    idx = df.index[existente]
                    df.at[idx, "Cantidad"] += cant
                    df.at[idx, "Costo Unitario ($)"] = costo if costo > 0 else df.at[idx, "Costo Unitario ($)"]
                else:
                    nueva = pd.DataFrame([{"Material": mat, "Cantidad": cant, "Costo Unitario ($)": costo, "Inversión Total ($)": 0.0}])
                    st.session_state.materia_prima = pd.concat([df, nueva], ignore_index=True)

                guardar_datos()
                st.success("¡Ingreso exitoso! Almacén actualizado.")
                st.rerun()
        st.dataframe(st.session_state.materia_prima, use_container_width=True, hide_index=True)

    # 3. TALLER DE FABRICACIÓN (Ambos)
    elif menu == "🔨 Taller de Fabricación":
        st.title("Reportar Producción Terminada")
        productos = st.session_state.productos_fabricados["Producto"].tolist()

        with st.form("form_fab"):
            prod = st.selectbox("¿Qué producto se fabricó?", productos)
            cant_fab = st.number_input("Cantidad de piezas terminadas:", min_value=1, step=1)

            if st.form_submit_button("Confirmar y Descontar Inventario"):
                receta = FORMULAS.get(prod)
                if not receta:
                    st.error(f"❌ No existe la fórmula de fabricación para '{prod}'.")
                else:
                    materiales_faltantes = []
                    ok = True

                    for material, cantidad_por_pieza in receta.items():
                        total_necesario = cantidad_por_pieza * cant_fab
                        fila = st.session_state.materia_prima[st.session_state.materia_prima["Material"] == material]

                        if fila.empty:
                            ok = False
                            materiales_faltantes.append(f"{material} (no existe en almacén)")
                            continue
                        
                        if fila.iloc[0]["Cantidad"] < total_necesario:
                            ok = False
