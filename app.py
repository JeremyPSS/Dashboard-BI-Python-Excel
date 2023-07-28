import pickle
from pathlib import Path

import pandas as pd 
import plotly.express as px
import streamlit as st 
import streamlit_authenticator as stauth  

st.set_page_config(page_title="Dashboard productos Agricolas", page_icon=":bar_chart:", layout="wide")


# --- USER AUTHENTICATION ---
names = ["Jeremy Prieto", "Oscar Cuenca"]
usernames = ["jeremyp01", "oscarc01"]

# load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "bi_dashboard", "abcdef", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Usuario/contraseña es incorrecta")

if authentication_status == None:
    st.warning("Porfavor digita tu usuario y contraseña")

if authentication_status:
    

    # ---- READING productos
    @st.cache_data or st.cache_resource
    def get_pro_from_excel():
        df = pd.read_excel(
            io="Expor_Produc_Cons_Precio.xlsx",
            engine="openpyxl",
            sheet_name="th_produccion_v",
            usecols="A:E",
            nrows=1000,
        )
        return df
    df = get_pro_from_excel()
    # ---- READING precio
    @st.cache_data or st.cache_resource
    def get_precio_from_excel():
        df1 = pd.read_excel(
            io="Expor_Produc_Cons_Precio.xlsx",
            engine="openpyxl",
            sheet_name="th_precio_v",
            usecols="A:D",
            nrows=1000,
        )
        return df1
    df1 = get_precio_from_excel()

    # ---- SIDEBAR USING STREAMLIT ----
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Bienvenido {name}")
    st.sidebar.header("Filtra datos aqui:")
    Pais = st.sidebar.multiselect(
        "Selecciona el pais:",
        options=df["pais"].unique(),
        default= "Ecuador"
    )

    Anio = st.sidebar.multiselect(
        "Selecciona el año:",
        options=df["anio"].unique(),
        default= 2016
    )

    Producto = st.sidebar.multiselect(
        "Selecciona el producto del top:",
        options=df["producto"].unique(),
        default=df["producto"].unique()
    )

    # ---- PUTTING FILTERS FOR EACH DATA MART
    df_selection = df.query(
        "pais == @Pais & anio ==@Anio & producto == @Producto"
    )
    #Anio1 = st.selectbox('selecciona el año', df1["anio"].unique())
    df1_selection = df1.query(
        "pais == @Pais & anio ==@Anio & producto == @Producto"
    )

    # ---- MAINPAGE ----
    st.title(":bar_chart: Dashboard de Analisis de productos agricolas en el mercado mundial ")
    st.markdown("##")

    # TOP KPI's
    total_production = int(df_selection["cantidad_kg"].sum()) #total cantidad de produccion por pais, año y produccion
    #type_production = df_selection["tipo_producto"] 
    price_production = round(df1_selection["precio"].sum(),2)#Precio promedio de los productos exportados por pais en un determinado año


    left_column, middle_column = st.columns(2)
    with left_column:
        st.subheader("Total Produccion:")
        st.subheader(f"{total_production:,} kg")
    with middle_column:
        st.subheader("Precio promedio:")
        st.subheader(f"$ {price_production}")

    st.markdown("""---""")

    # SALES BY PRODUCT LINE [BAR CHART]
    cant_by_product_line = (
        df_selection.groupby('producto')['cantidad_kg'].sum()
    )
    fig_product_cant = px.bar(
        cant_by_product_line,
        x="cantidad_kg",
        y=cant_by_product_line.index,
        orientation="h",
        title="<b>Cantidad de kg x Producto</b>",
        color_discrete_sequence=["#0083B8"] * len(cant_by_product_line),
        template="plotly_dark",
    )
    fig_product_cant.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
    fig_product_cant_pie = px.pie(
        cant_by_product_line,
        values="cantidad_kg",
        names=cant_by_product_line.index,
        title="<b>Cantidad de kg x Producto</b>",
        template="plotly_dark"
    )

    precio_by_line = (
        df1_selection.groupby('producto')['precio'].sum()
    )
    fig_precio = px.line(
        precio_by_line,
        x = precio_by_line.index ,
        y = 'precio',
        title="<b>Precios</b>",
    )


    #right_column = st.columns(2)
    #right_column[0].plotly_chart(fig_product_cant, use_container_width=True)
    st.plotly_chart(fig_product_cant, use_container_width=True)
    st.plotly_chart(fig_product_cant_pie, use_container_width=True)
    st.plotly_chart(fig_precio, use_container_width=True)

    # ---- HIDE STREAMLIT STYLE ----
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)
