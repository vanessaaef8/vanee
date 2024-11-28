import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import requests
import yfinance as yf
import plotly.express as px


# Configuración inicial de la página
st.set_page_config(
    page_title="Planv",
    page_icon="🏡",
    layout="wide"
)

# Configuración de Banxico API
BANXICO_API_TOKEN = "c12f3a32914576b3029870226615defce1527efcc49967ebea0a9d6ed14a7c78"
BANXICO_URL = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/{series_id}/datos/oportuno"

def obtener_tasa_cetes(plazo):
    series_id = {
        28: "SF43936",
        91: "SF43937",
        182: "SF43938",
        364: "SF43939"
    }.get(plazo, "SF43939")

    headers = {"Bmx-Token": BANXICO_API_TOKEN}
    response = requests.get(BANXICO_URL.format(series_id=series_id), headers=headers)
    data = response.json()

    try:
        tasa_cetes_str = data["bmx"]["series"][0]["datos"][0]["dato"]
        return float(tasa_cetes_str.replace(",", "")) / 100
    except (KeyError, IndexError):
        st.error("Error al obtener tasas de Banxico.")
        return 0.05  # Predeterminado

def obtener_rendimiento_fondo(ticker, años=1):
    try:
        data = yf.download(ticker, period=f"{años}y", interval="1d")
        precio_inicial = data['Adj Close'].iloc[0]
        precio_final = data['Adj Close'].iloc[-1]
        rendimiento_total = (precio_final / precio_inicial) - 1
        return (1 + rendimiento_total) ** (1 / años) - 1
    except Exception as e:
        st.error(f"Error al obtener datos de {ticker}: {e}")
        return 0.10  # Predeterminado

def obtener_rendimiento_cripto(cripto_id, días=365):
    url = f"https://api.coingecko.com/api/v3/coins/{cripto_id}/market_chart"
    params = {"vs_currency": "usd", "days": días}
    response = requests.get(url, params=params)
    data = response.json()

    try:
        precios = data["prices"]
        precio_inicial = precios[0][1]
        precio_final = precios[-1][1]
        return (precio_final / precio_inicial) - 1
    except KeyError:
        st.error(f"Error al obtener datos de {cripto_id}.")
        return 0.15  # Predeterminado

# Función para mostrar la página de inicio
def mostrar_inicio():
    st.header("Jubilife🎓")
    st.write("¡Bienvenido a nuestra aplicación de planificación financiera!")
    
    # Solicitar nombre y teléfono
    nombre = st.text_input("Ingresa tu nombre", placeholder="Tu nombre aquí")
    telefono = st.text_input("Ingresa tu teléfono", placeholder="Tu número aquí")
    
    if nombre and telefono.isdigit():
        st.success(f"¡Hola {nombre}! Nos alegra que estés aquí. ¡Estás un paso más cerca de cumplir tus objetivos!")
        st.image("https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExbmQ0bG03NHpqcjV2cmZmNWM2cDRud2Jyc29scWNlbXllZHExam04dCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/YRuFixSNWFVcXaxpmX/giphy.gif", width=300)
        st.write("¡Vamos a planificar tu futuro financiero!🎅🏼🤶🏼")
    else:
        st.warning("Por favor, ingresa tu nombre y un teléfono válido para continuar.")

# Función para configurar metas
def configurar_metas():
    st.header("💰 Configurar Metas Financieras")
    monto_casa = st.number_input("Monto deseado (en pesos):", min_value=100_000.0, step=10_000.0)
    plazo_casa = st.slider("Plazo para alcanzar esta meta (en años):", min_value=1, max_value=30, step=1)
    
    # Botón para calcular
    if st.button("Calcular Metas"):
        # Calcular monto mensual necesario
        plazo_meses = plazo_casa * 12
        monto_mensual = monto_casa / plazo_meses
        
        # Mostrar el mensaje con el resultado
        st.success(f"¡Tu meta ha sido configurada!")
        
# Función para obtener el precio de una criptomoneda desde Bitso
def obtener_precio_cripto(moneda_base="btc", moneda_mercado="mxn"):
    url = f"https://api.bitso.com/v3/ticker/?book={moneda_base}_{moneda_mercado}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return float(data['payload']['last'])
    else:
        st.error("Error al obtener datos de Bitso.")
        return None

# Función para sugerir criptomoneda basada en la política económica
def sugerir_cripto(politica_economica):
    if politica_economica == "Alta inflación":
        return "btc", "Bitcoin (BTC) es considerado una reserva de valor y puede actuar como refugio en tiempos de alta inflación."
    elif politica_economica == "Crecimiento económico":
        return "eth", "Ethereum (ETH) es una opción sólida en épocas de crecimiento debido a su ecosistema de aplicaciones descentralizadas."
    elif politica_economica == "Política restrictiva":
        return "xrp", "XRP puede beneficiarse en un entorno restrictivo por su enfoque en transacciones rápidas y costos bajos."
    else:
        return None, "Selecciona una política económica válida."

# Función para calcular la inversión final ajustada por inflación y con base en el perfil de riesgo
def calcular_inversion_final(monto_invertir, plazo, perfil_riesgo):
    # Asignación de la inversión según el perfil de riesgo
    asignacion = asignar_perfil_riesgo(perfil_riesgo)
    
    # Tasas de crecimiento (supuestas)
    tasa_cetes = 0.08  # 8% anual
    tasa_fondo = 0.12  # 12% anual
    tasa_cripto = 0.20  # 20% anual

    # Calcular el valor final de cada componente de la inversión
    monto_cetes = monto_invertir * asignacion['CETES'] * ((1 + tasa_cetes) ** plazo)
    monto_fondo = monto_invertir * asignacion['Fondo Indexado'] * ((1 + tasa_fondo) ** plazo)
    monto_cripto = monto_invertir * asignacion['Criptomonedas'] * ((1 + tasa_cripto) ** plazo)

    # Monto total después de inflación (ajustado)
    monto_final = monto_cetes + monto_fondo + monto_cripto
    
    # Inflación promedio (3% anual)
    inflacion = 0.03
    monto_final_ajustado = monto_final / ((1 + inflacion) ** plazo)
    
    return monto_final_ajustado

# Función para asignar las proporciones según el perfil de riesgo
def asignar_perfil_riesgo(perfil_riesgo):
    if perfil_riesgo == "Conservador":
        return {'CETES': 0.80, 'Fondo Indexado': 0.15, 'Criptomonedas': 0.05}
    elif perfil_riesgo == "Moderado":
        return {'CETES': 0.60, 'Fondo Indexado': 0.30, 'Criptomonedas': 0.10}
    elif perfil_riesgo == "Agresivo":
        return {'CETES': 0.20, 'Fondo Indexado': 0.30, 'Criptomonedas': 0.50}

# Función para mostrar lo que significa cada perfil de riesgo con colores
def mostrar_descripcion_perfil(perfil_riesgo):
    if perfil_riesgo == "Conservador":
        st.subheader("Perfil Conservador")
        st.markdown("<p style='color:green;'>🟢 Orientado a la seguridad y estabilidad. Prefiere instrumentos de bajo riesgo como CETES y fondos indexados conservadores.</p>", unsafe_allow_html=True)
    elif perfil_riesgo == "Moderado":
        st.subheader("Perfil Moderado")
        st.markdown("<p style='color:orange;'>🟠 Busca un equilibrio entre seguridad y crecimiento. Combina instrumentos de bajo riesgo con algunos más arriesgados como fondos indexados y criptomonedas.</p>", unsafe_allow_html=True)
    elif perfil_riesgo == "Agresivo":
        st.subheader("Perfil Agresivo")
        st.markdown("<p style='color:red;'>🔴 Maximiza el rendimiento a través de un alto riesgo, invirtiendo principalmente en criptomonedas y fondos indexados con mayor volatilidad.</p>", unsafe_allow_html=True)


# Función para sugerir criptomoneda y fondo según política económica
def sugerir_fondo_cripto(politica_economica):
    if politica_economica == "Alta inflación":
        fondo = "SCHP (Schwab TIPS ETF)"
        razon_fondo = "Este fondo está diseñado para protegerse contra la inflación."
        cripto = "BTC (Bitcoin)"
        razon_cripto = "Bitcoin tiende a subir en escenarios inflacionarios."
    elif politica_economica == "Crecimiento económico":
        fondo = "SPY (S&P 500 ETF)"
        razon_fondo = "Este fondo sigue al índice S&P 500."
        cripto = "ETH (Ethereum)"
        razon_cripto = "Ethereum es atractivo durante expansiones económicas."
    elif politica_economica == "Política restrictiva":
        fondo = "BND (Vanguard Total Bond Market ETF)"
        razon_fondo = "Este fondo es adecuado para políticas restrictivas."
        cripto = "XRP (Ripple)"
        razon_cripto = "Ripple puede ser una opción en mercados más volátiles."
    else:
        fondo = "Desconocido"
        razon_fondo = "No hay fondo recomendado."
        cripto = "Desconocida"
        razon_cripto = "No hay criptomoneda recomendada."
    
    return fondo, razon_fondo, cripto, razon_cripto

# Función para asignar la distribución según el perfil de riesgo
def asignar_perfil_riesgo(perfil_riesgo):
    if perfil_riesgo == "Conservador":
        return {"CETES": 0.80, "Fondo Indexado": 0.10, "Criptomonedas": 0.10}
    elif perfil_riesgo == "Moderado":
        return {"CETES": 0.60, "Fondo Indexado": 0.30, "Criptomonedas": 0.10}
    elif perfil_riesgo == "Agresivo":
        return {"CETES": 0.30, "Fondo Indexado": 0.40, "Criptomonedas": 0.30}
    else:
        return {"CETES": 0.0, "Fondo Indexado": 0.0, "Criptomonedas": 0.0}

# Función para calcular el valor final de la inversión
def calcular_inversion_final(monto_invertir, plazo, perfil_riesgo):
    # Este es un ejemplo sencillo, puedes ajustar las tasas de retorno según el perfil de riesgo.
    if perfil_riesgo == "Conservador":
        tasa_rendimiento = 0.05
    elif perfil_riesgo == "Moderado":
        tasa_rendimiento = 0.07
    elif perfil_riesgo == "Agresivo":
        tasa_rendimiento = 0.10
    else:
        tasa_rendimiento = 0.05
    
    valor_final = monto_invertir * (1 + tasa_rendimiento) ** plazo
    return valor_final

# Gráfico de crecimiento de los instrumentos, actualizado según el perfil de riesgo y política económica
def graficar_crecimiento(monto_invertir, plazo, perfil_riesgo):
    # Ajuste del crecimiento según el perfil de riesgo
    if perfil_riesgo == "Conservador":
        tasas_rendimiento = {
            "CETES": 0.04,  # 4% anual
            "Fondo Indexado": 0.06,  # 6% anual
            "Criptomonedas": 0.05   # 5% anual
        }
    elif perfil_riesgo == "Moderado":
        tasas_rendimiento = {
            "CETES": 0.05,  # 5% anual
            "Fondo Indexado": 0.08,  # 8% anual
            "Criptomonedas": 0.07   # 7% anual
        }
    elif perfil_riesgo == "Agresivo":
        tasas_rendimiento = {
            "CETES": 0.06,  # 6% anual
            "Fondo Indexado": 0.10,  # 10% anual
            "Criptomonedas": 0.12   # 12% anual
        }

    # Calcular el crecimiento de los instrumentos durante el plazo
    periodos = [1, 2, 3, 4, 5]
    crecimiento_cetes = [1 + tasas_rendimiento["CETES"] * i for i in periodos]
    crecimiento_fondo = [1 + tasas_rendimiento["Fondo Indexado"] * i for i in periodos]
    crecimiento_cripto = [1 + tasas_rendimiento["Criptomonedas"] * i for i in periodos]

    # Crear un DataFrame para el gráfico
    data = pd.DataFrame({
        "Periodo": periodos * 3,  # Repetimos los periodos para cada instrumento
        "Crecimiento": crecimiento_cetes + crecimiento_fondo + crecimiento_cripto,
        "Instrumento": ["CETES"] * 5 + ["Fondo Indexado"] * 5 + ["Criptomoneda"] * 5
    })

    # Crear gráfico 2D con Plotly Express
    fig = px.line(
        data,
        x="Periodo",
        y="Crecimiento",
        color="Instrumento",  # Diferencia los instrumentos por color
        title=f"Crecimiento de los Instrumentos Financieros ({perfil_riesgo} - Base 100)",
        labels={
            "Periodo": "Plazo (años)",
            "Crecimiento": "Crecimiento en Base 100",
            "Instrumento": "Instrumento Financiero"
        },
        markers=True  # Agrega puntos en las líneas para facilitar la lectura
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)


# Función para mostrar recomendaciones y cálculo
def mostrar_recomendaciones():
    st.title("Recomendación Según Política Económica")

    # Selección de política económica
    politica_economica = st.selectbox(
        "Selecciona el escenario de política económica:",
        ["Alta inflación", "Crecimiento económico", "Política restrictiva"]
    )

    # Texto explicativo dinámico basado en la opción seleccionada
    explicacion = {
        "Alta inflación": (
            "Este escenario ocurre cuando los precios de bienes y servicios suben significativamente. "
            "Se recomienda proteger tu inversión con instrumentos que ajusten su valor según la inflación, "
            "como CETES o fondos indexados ligados a bonos protegidos contra la inflación."
        ),
        "Crecimiento económico": (
            "En este escenario, la economía está en expansión, lo que puede generar mejores rendimientos en instrumentos "
            "como fondos de inversión y acciones. Sin embargo, también puede haber más volatilidad."
        ),
        "Política restrictiva": (
            "Un escenario de política restrictiva suele implicar aumentos en tasas de interés para controlar la inflación. "
            "Esto puede beneficiar a inversiones de renta fija como CETES, pero puede ser desfavorable para acciones o criptomonedas."
        ),
    }

    # Mostrar explicación bajo el selectbox
    st.write(explicacion[politica_economica])

    # Obtener recomendación de criptomoneda y fondo
    fondo, razon_fondo, cripto, razon_cripto = sugerir_fondo_cripto(politica_economica)

    # Mostrar recomendación de criptomoneda
    st.subheader(f"Recomendación: {cripto} (Criptomoneda)")
    st.write(razon_cripto)

    # Mostrar recomendación de fondo indexado
    st.subheader(f"Recomendación: {fondo} (Fondo Indexado)")
    st.write(razon_fondo)

    # Solicitar monto de inversión, perfil de riesgo y plazo
    monto_invertir = st.number_input("Monto a invertir (en pesos):", min_value=1_000.0, step=100.0)
    plazo = st.slider("Plazo de inversión (en años):", min_value=1, max_value=30, step=1)
    perfil_riesgo = st.selectbox("Selecciona tu perfil de riesgo:", ["Conservador", "Moderado", "Agresivo"])

    # Calcular la inversión final cuando el usuario haga clic en "Calcular Inversión"
    if st.button("Calcular Inversión"):
        # Calcular el valor final ajustado por inflación
        monto_final_ajustado = calcular_inversion_final(monto_invertir, plazo, perfil_riesgo)
        
        # Mostrar resultados de inversión final con estilo personalizado
        st.markdown(
            f"""
            <div style='
                background-color: #d4edda; 
                color: #155724; 
                border: 1px solid #c3e6cb; 
                border-radius: 5px; 
                padding: 10px;
                font-size: 18px;
            '>
                <b>¡Tu inversión de ${monto_invertir:,.2f} tiene un valor final estimado de ${monto_final_ajustado:,.2f} después de {plazo} años!</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        
        # Mostrar distribución de inversión según el perfil de riesgo
        distribucion = asignar_perfil_riesgo(perfil_riesgo)
        
        # Crear tabla con la distribución de inversión
        data = {
            "Instrumento": ["CETES", "Fondo Indexado", "Criptomonedas"],
            "Porcentaje Asignado": [
                f"{distribucion['CETES'] * 100:.2f}%",
                f"{distribucion['Fondo Indexado'] * 100:.2f}%",
                f"{distribucion['Criptomonedas'] * 100:.2f}%"
            ],
            "Monto Asignado": [
                monto_invertir * distribucion["CETES"],
                monto_invertir * distribucion["Fondo Indexado"],
                monto_invertir * distribucion["Criptomonedas"]
            ],
            "Instrumento Recomendado": [
                "CETES directo",
                fondo, 
                cripto
            ]
        }
        
        df = pd.DataFrame(data)
        
        # Mostrar tabla con los porcentajes y montos
        st.table(df)
        
        # Graficar el crecimiento de los instrumentos financieros
        graficar_crecimiento(monto_invertir, plazo, perfil_riesgo)

# Función para explicar cómo invertir
def invertir():
    st.header("📚 Cómo Invertir")
    st.subheader("1. Fondos Indexados")
    st.write("""
        Los fondos indexados son una excelente opción para diversificar tus inversiones y 
        seguir el rendimiento de un índice de mercado. Invertir en un fondo indexado te permite 
        tener una exposición a una variedad de activos sin la necesidad de seleccionar individualmente 
        cada acción o bono.
        
        ### Pasos para invertir en fondos indexados:
        1. **Selecciona un bróker**: Plataformas como **[GBM+](https://www.gbm.com.mx/)** o **[Bursanet](https://www.bursanet.mx/)** permiten invertir en estos fondos.
        2. **Abre una cuenta**: Regístrate y abre una cuenta en la plataforma seleccionada.
        3. **Busca el fondo**: Puedes invertir en fondos como **SPY**, **QQQ**, **EEM**, o **URTH**, que siguen índices como el S&P 500.
        4. **Deposita dinero**: Transfiere el monto que deseas invertir.
        5. **Compra el fondo**: Selecciona el fondo que más te convenga y realiza la compra.
    """)

    st.subheader("2. Criptomonedas")
    st.write("""
        Las criptomonedas son monedas digitales que funcionan sin un banco central. 
        Bitcoin, Ethereum y stablecoins como USDT son algunas de las opciones más populares.
        
        ### Pasos para invertir en criptomonedas:
        1. **Selecciona una plataforma**: Usa plataformas como **[Binance](https://www.binance.com/)**, **[Coinbase](https://www.coinbase.com/)**, o **[Bitso](https://bitso.com/)** para comprar criptomonedas.
        2. **Crea una cuenta**: Regístrate en la plataforma seleccionada.
        3. **Depósito**: Añade fondos a tu cuenta usando transferencia bancaria o tarjeta.
        4. **Compra criptomonedas**: Compra criptomonedas como **Bitcoin (BTC)** o **Ethereum (ETH)**.
        5. **Almacenamiento**: Guarda tus criptomonedas en una billetera digital.
    """)

    st.subheader("3. CETES")
    st.write("""
        Los CETES (Certificados de la Tesorería de la Federación) son instrumentos de deuda emitidos por el gobierno de México. 
        Son considerados de bajo riesgo y tienen plazos de inversión que varían entre 28 y 364 días.
        
        ### Pasos para invertir en CETES:
        1. **Regístrate en CETES Directo**: Ingresa a **[CETES Directo](https://www.cetesdirecto.com)** y abre una cuenta.
        2. **Selecciona un plazo**: Elige entre plazos de 28, 91, 182 o 364 días.
        3. **Realiza la inversión**: Decide cuánto dinero deseas invertir.
        4. **Compra los CETES**: Realiza la compra directamente desde la plataforma de CETES Directo.
        5. **Recibe los rendimientos**: Al final del plazo, recibirás los rendimientos generados.
    """)

# Navegación
menu = st.sidebar.radio("Navega por la app:", ["Inicio", "Configurar Metas", "Recomendaciones", "Para Invertir"])
if menu == "Inicio":
    mostrar_inicio()
elif menu == "Configurar Metas":
    configurar_metas()
elif menu == "Recomendaciones":
    mostrar_recomendaciones()
elif menu == "Para Invertir":
    invertir()
