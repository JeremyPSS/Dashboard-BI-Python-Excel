import pickle
from pathlib import Path

import pandas as pd 
import plotly.express as px
import streamlit as st 
import streamlit_authenticator as stauth  
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard clientes TEUNO", page_icon=":bar_chart:", layout="wide")


# --- USER AUTHENTICATION ---
names = ["Jeremy Prieto", "Oscar Cuenca"]
usernames = ["jeremyp01", "oscarc01"]
# load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,"bi_dashboard", "abcdef", cookie_expiry_days=30)
name, authentication_status, username = authenticator.login("Login", "main")
if authentication_status == False:
    st.error("Usuario/contraseña es incorrecta")
if authentication_status == None:
    st.warning("Porfavor digita tu usuario y contraseña")
    
if authentication_status:
    # ---- READING clientes------------------------------------------------------------------------------------------
    @st.cache_data or st.cache_resource
    def get_cli_from_excel():
        df = pd.read_excel(
            io="clientes_teuno.xlsx",
            engine="openpyxl",
            sheet_name="clientes",
            usecols="A:N",
            nrows=102,
        )
        return df
    df = get_cli_from_excel()

    #---- SIDEBAR USING STREAMLIT --------------------------------------------------------------------------------
    authenticator.logout("Logout", "sidebar")
    st.sidebar.title(f"Bienvenido {name}")
    st.sidebar.header("Filtra datos aqui:")
    UBI = st.sidebar.multiselect(
        "Selecciona la Ubicacion:",
        options=df["Ubicacion"].unique(),
        default=(df["Ubicacion"].unique()).tolist()
        # default= "Azuay"
    )
    # ---- PUTTING FILTERS FOR EACH DATA MART
    df_selection = df.query(
        "Ubicacion == @UBI"
    )



    # ---- MAINPAGE -----------------------------------------------------------------------------------------------------
    st.title(":bar_chart: Dashboard de Analisis de Clientes en TEUNO ")
    st.markdown("##")
    # TOP KPI's
    # Calcular Tasa de Renovación de Contratos
    num_contratos = len(df_selection)
    num_renovados = len(df_selection[df_selection['EstadoRenovacion'] == 'Renovado'])
    tasa_renovacion = (num_renovados / num_contratos) * 100
    tasa_renovacion = round(tasa_renovacion,2)
    # Calcular Tasa de Satisfacción del Cliente
    num_feedbacks = len(df_selection['Feedback'].dropna())
    num_feedbacks_positivos = len(df_selection[df_selection['Feedback'].str.contains('Satisfecho|Buen servicio')])
    tasa_satisfaccion = (num_feedbacks_positivos / num_feedbacks) * 100
    tasa_satisfaccion = round(tasa_satisfaccion,2)

    left_column, middle_column = st.columns(2)
    with left_column:
        st.subheader("Tasa de Renovación de Contratos:")
        st.subheader(f"{tasa_renovacion:,} %")
    with middle_column:
        st.subheader("Tasa de Satisfacción del Cliente:")
        st.subheader(f"{tasa_satisfaccion} %")

    st.markdown("""---""")

    # -----------------------------------------------------------------------------------------------------
    # Ejemplo de visualización: Tasa de renovación por tipo de servicio
    tasa_renovacion_servicio = df_selection.groupby('ServicioContratado')['EstadoRenovacion'].value_counts(normalize=True).unstack().fillna(0)
    fig = px.bar(tasa_renovacion_servicio, x=tasa_renovacion_servicio.index, y='Renovado', title='Tasa de Renovación por Tipo de Servicio', labels={'Renovado': 'Tasa de Renovación'})
    
    # Ejemplo de visualización: Distribución de clientes por tamaño de empresa
    fig2 = px.pie(df_selection, names='TamanioEmpresa', title='Distribución de Clientes por Tamaño de Empresa')

    # Ejemplo de visualización: Feedback de clientes
    feedback_renovacion = df_selection[df_selection['EstadoRenovacion'] == 'No Renovado']['Feedback'].value_counts()
    fig3 = go.Figure([go.Bar(x=feedback_renovacion.index, y=feedback_renovacion.values)])
    fig3.update_layout(title='Feedback de Clientes que No Renovaron', xaxis_title='Feedback', yaxis_title='Cantidad')


    # Gráfico de Ingreso Anual del Cliente
    fig4 = px.bar(df_selection, x='Ubicacion', y='IngresoAnualCliente', title='Ingreso Anual del Cliente por Provincia',
                        labels={'Ubicacion': 'Ubicacion', 'IngresoAnualCliente': 'Ingreso Anual (USD)'})

    # Gráfico de Duración del Contrato
    fig5 = px.bar(df_selection, x='Ubicacion', y='DuracionContrato', title='Duración del Contrato por Provincia',
                        labels={'Ubicacion': 'Ubicacion', 'DuracionContrato': 'Duración del Contrato (meses)'})

    st.plotly_chart(fig, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)
    st.plotly_chart(fig4, use_container_width=True)
    st.plotly_chart(fig5, use_container_width=True)

    # ---- HIDE STREAMLIT STYLE ----
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)
