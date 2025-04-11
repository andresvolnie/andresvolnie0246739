# ✅ Configuración inicial
import streamlit as st
st.set_page_config(page_title="FinanceCompare Pro", layout="wide", page_icon="📊")

# 📦 Librerías
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator

# 🎨 Estilo profesional con tema claro
st.markdown("""
    <style>
        :root {
            --primary: #1f77b4;
            --secondary: #ff7f0e;
            --background: #ffffff;
            --card: #f8f9fa;
            --text: #333333;
            --border: #e1e4e8;
        }
        
        .main {
            background-color: var(--background);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--text) !important;
            font-family: 'Inter', sans-serif;
        }
        
        .stApp {
            background-color: var(--background);
            font-family: 'Inter', sans-serif;
            color: var(--text);
        }
        
        .stSidebar {
            background-color: var(--card) !important;
            border-right: 1px solid var(--border);
        }
        
        .stTextInput>div>div>input {
            background-color: white !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
        }
        
        .metric-card {
            background-color: var(--card);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border);
        }
        
        .comparison-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 8px;
        }
        
        .positive {
            background-color: #e6f7ee;
            color: #14532d;
            border: 1px solid #a7f3d0;
        }
        
        .negative {
            background-color: #fee2e2;
            color: #7f1d1d;
            border: 1px solid #fca5a5;
        }
        
        .neutral {
            background-color: #dbeafe;
            color: #1e40af;
            border: 1px solid #93c5fd;
        }
        
        .ticker-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        
        .ticker-color-1 {
            color: #1f77b4;
        }
        
        .ticker-color-2 {
            color: #ff7f0e;
        }
        
        .formula-box {
            background-color: #f0f5ff;
            border-left: 4px solid #1f77b4;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 0 5px 5px 0;
            font-family: 'Courier New', monospace;
        }
    </style>
""", unsafe_allow_html=True)

# 📌 Título con logo profesional
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2472/2472054.png", width=60)
with col2:
    st.title("FinanceCompare Pro")
st.markdown("**Plataforma profesional de análisis y comparación de activos financieros**")

# 🔎 Función para obtener info de empresa mejorada
def get_company_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        company_name = info.get("shortName", info.get("longName", symbol))
        sector = info.get("sector", "Sector no disponible")
        industry = info.get("industry", "Industria no disponible")
        country = info.get("country", "País no disponible")
        description = info.get("longBusinessSummary", "Descripción no disponible.")
        
        # Traducción al español
        try:
            description = GoogleTranslator(source='auto', target='es').translate(description[:2000])
        except:
            pass
            
        # Datos adicionales
        market_cap = info.get("marketCap", "N/A")
        if isinstance(market_cap, (int, float)):
            if market_cap >= 1e12:
                market_cap = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                market_cap = f"${market_cap/1e6:.2f}M"
        
        return {
            "symbol": symbol,
            "name": company_name,
            "sector": sector,
            "industry": industry,
            "country": country,
            "description": description,
            "market_cap": market_cap,
            "currency": info.get("currency", "N/A")
        }
    except Exception as e:
        return {"error": f"Error al obtener datos: {str(e)}"}

# 📉 Función para obtener precios históricos mejorada
def get_historical_prices(symbol, years):
    try:
        end_date = datetime.today() + timedelta(days=1)  # Incluir día actual
        start_date = end_date - timedelta(days=years * 365)
        
        # Primero intentar con yf.download
        try:
            hist = yf.download(symbol, start=start_date, end=end_date, progress=False)
            if not hist.empty:
                return hist[['Close']]
        except:
            pass
        
        # Si falla, intentar con yf.Ticker
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            return hist[['Close']]
        except Exception as e:
            st.error(f"Error obteniendo datos para {symbol}: {str(e)}")
            return None
            
    except Exception as e:
        st.error(f"Error crítico obteniendo datos para {symbol}: {str(e)}")
        return None

# 📈 Funciones de cálculo de métricas
def calculate_cagr(prices, years):
    if prices is None or prices.empty:
        return None
    start_price = prices.iloc[0][0]
    end_price = prices.iloc[-1][0]
    cagr = ((end_price / start_price) ** (1 / years) - 1) * 100
    return round(cagr, 2)

def calculate_volatility(prices):
    if prices is None or prices.empty:
        return None
    returns = prices.iloc[:, 0].pct_change().dropna()
    volatility = np.std(returns) * np.sqrt(252) * 100
    return round(volatility, 2)

def calculate_max_drawdown(prices):
    if prices is None or prices.empty:
        return None
    cumulative = prices.iloc[:, 0].pct_change().add(1).cumprod()
    peak = cumulative.expanding(min_periods=1).max()
    drawdown = (cumulative/peak - 1) * 100
    return round(drawdown.min(), 2)

# 📊 Visualización de volatilidad mejorada
def plot_volatility_comparison(prices1, prices2, name1, name2):
    if prices1 is None or prices2 is None or prices1.empty or prices2.empty:
        return None
    
    # Calcular volatilidad rolling (ventana de 3 meses)
    returns1 = prices1.iloc[:, 0].pct_change().dropna()
    rolling_vol1 = returns1.rolling(window=63).std() * np.sqrt(252) * 100
    
    returns2 = prices2.iloc[:, 0].pct_change().dropna()
    rolling_vol2 = returns2.rolling(window=63).std() * np.sqrt(252) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rolling_vol1.index,
        y=rolling_vol1,
        name=f"{name1}",
        line=dict(color='#1f77b4', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.1)'
    ))
    
    fig.add_trace(go.Scatter(
        x=rolling_vol2.index,
        y=rolling_vol2,
        name=f"{name2}",
        line=dict(color='#ff7f0e', width=2),
        fill='tozeroy',
        fillcolor='rgba(255, 127, 14, 0.1)'
    ))
    
    fig.update_layout(
        title="Comparación de Volatilidad (Rolling 3 meses)",
        xaxis_title="Fecha",
        yaxis_title="Volatilidad Anualizada (%)",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#333333'),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

# 🏆 Función para mostrar tarjeta de comparación
def display_comparison_metric(value1, value2, title, unit="%", reverse=False):
    if value1 is None or value2 is None:
        return
    
    diff = value1 - value2
    abs_diff = abs(diff)
    
    if diff > 0:
        badge_class = "positive" if not reverse else "negative"
        comparison_text = f"+{abs_diff:.2f}{unit}"
    elif diff < 0:
        badge_class = "negative" if not reverse else "positive"
        comparison_text = f"-{abs_diff:.2f}{unit}"
    else:
        badge_class = "neutral"
        comparison_text = f"0{unit}"
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"<div class='metric-card'><h5>{title}</h5><h3>{value1:.2f}{unit}</h3></div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<div class='metric-card'><h5>{title}</h5><h3>{value2:.2f}{unit}</h3></div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"<div class='metric-card'><h5>Diferencia</h5><h3><span class='comparison-badge {badge_class}'>{comparison_text}</span></h3></div>", unsafe_allow_html=True)

# 🧭 Sidebar para selección de tickers
st.sidebar.header("🔍 Configuración de Análisis")
ticker1 = st.sidebar.text_input("Símbolo 1 (Ej: AAPL)", "AAPL").upper()
ticker2 = st.sidebar.text_input("Símbolo 2 (Ej: MSFT)", "MSFT").upper()
years = st.sidebar.slider("Años históricos", 1, 10, 5)

# 📌 Obtención de datos
if ticker1 and ticker2:
    # Info de empresas
    company1 = get_company_info(ticker1)
    company2 = get_company_info(ticker2)
    
    # Precios históricos
    prices1 = get_historical_prices(ticker1, years)
    prices2 = get_historical_prices(ticker2, years)
    
    # Mostrar información de las empresas
    if "error" not in company1 and "error" not in company2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
                <div class='ticker-header'>
                    <h2 class='ticker-color-1'>📌 {company1['name']} ({ticker1})</h2>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div class='metric-card'>
                    <p><strong>Sector:</strong> {company1['sector']}</p>
                    <p><strong>Industria:</strong> {company1['industry']}</p>
                    <p><strong>País:</strong> {company1['country']}</p>
                    <p><strong>Capitalización:</strong> {company1['market_cap']} {company1['currency']}</p>
                </div>
                <div class='metric-card'>
                    <p>{company1['description']}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class='ticker-header'>
                    <h2 class='ticker-color-2'>📌 {company2['name']} ({ticker2})</h2>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
                <div class='metric-card'>
                    <p><strong>Sector:</strong> {company2['sector']}</p>
                    <p><strong>Industria:</strong> {company2['industry']}</p>
                    <p><strong>País:</strong> {company2['country']}</p>
                    <p><strong>Capitalización:</strong> {company2['market_cap']} {company2['currency']}</p>
                </div>
                <div class='metric-card'>
                    <p>{company2['description']}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # 📈 Gráfico de comparación de precios (CORREGIDO)
        st.subheader("📈 Comparación de Precios Históricos (Normalizados)")
        if prices1 is not None and prices2 is not None and not prices1.empty and not prices2.empty:
            # Normalizar precios para comparación
            norm_prices1 = prices1 / prices1.iloc[0] * 100
            norm_prices2 = prices2 / prices2.iloc[0] * 100
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=norm_prices1.index,
                y=norm_prices1['Close'],
                name=f"{ticker1}",
                line=dict(color='#1f77b4', width=2)
            ))
            
            fig.add_trace(go.Scatter(
                x=norm_prices2.index,
                y=norm_prices2['Close'],
                name=f"{ticker2}",
                line=dict(color='#ff7f0e', width=2)
            ))
            
            fig.update_layout(
                title=f"Comparación de Rendimiento ({years} años)",
                xaxis_title="Fecha",
                yaxis_title="Rendimiento Normalizado (%)",
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(color='#333333'),
                legend_title_text='',
                hovermode="x unified",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay suficientes datos para mostrar la comparación de precios")
        
        # 📊 Comparación de métricas
        st.subheader("📊 Comparación de Métricas Clave")
        
        # CAGR a diferentes plazos
        st.markdown("**Rendimiento Anualizado (CAGR)**")
        cagr1_1y = calculate_cagr(get_historical_prices(ticker1, 1), 1)
        cagr2_1y = calculate_cagr(get_historical_prices(ticker2, 1), 1)
        display_comparison_metric(cagr1_1y, cagr2_1y, "1 Año")
        
        cagr1_3y = calculate_cagr(get_historical_prices(ticker1, 3), 3)
        cagr2_3y = calculate_cagr(get_historical_prices(ticker2, 3), 3)
        display_comparison_metric(cagr1_3y, cagr2_3y, "3 Años")
        
        cagr1_5y = calculate_cagr(get_historical_prices(ticker1, 5), 5)
        cagr2_5y = calculate_cagr(get_historical_prices(ticker2, 5), 5)
        display_comparison_metric(cagr1_5y, cagr2_5y, "5 Años")
        
        # Fórmula del CAGR
        st.markdown("""
        <div class='formula-box'>
            <strong>Fórmula del CAGR:</strong><br>
            CAGR = [(Precio Final / Precio Inicial)<sup>(1/Número de Años)</sup> - 1] × 100<br>
            Donde:<br>
            - Precio Final = Último precio de cierre<br>
            - Precio Inicial = Primer precio de cierre<br>
            - Número de Años = Período de tiempo en años
        </div>
        """, unsafe_allow_html=True)
        
        # Volatilidad y drawdown
        st.markdown("**Riesgo**")
        vol1 = calculate_volatility(prices1) if prices1 is not None and not prices1.empty else None
        vol2 = calculate_volatility(prices2) if prices2 is not None and not prices2.empty else None
        display_comparison_metric(vol1, vol2, "Volatilidad Anualizada", reverse=True)
        
        max_dd1 = calculate_max_drawdown(prices1) if prices1 is not None and not prices1.empty else None
        max_dd2 = calculate_max_drawdown(prices2) if prices2 is not None and not prices2.empty else None
        display_comparison_metric(max_dd1, max_dd2, "Máximo Drawdown", reverse=True)
        
        # Fórmula de Volatilidad
        st.markdown("""
        <div class='formula-box'>
            <strong>Fórmula de Volatilidad Anualizada:</strong><br>
            σ = Desviación Estándar(Rendimientos Diarios) × √252 × 100<br>
            Donde:<br>
            - 252 = Número aproximado de días de trading en un año<br>
            - Rendimientos Diarios = (Precio<sub>t</sub> / Precio<sub>t-1</sub>) - 1
        </div>
        """, unsafe_allow_html=True)
        
        # Visualización avanzada de volatilidad
        st.subheader("📌 Comparación de Volatilidad")
        vol_fig = plot_volatility_comparison(prices1, prices2, ticker1, ticker2)
        if vol_fig:
            st.plotly_chart(vol_fig, use_container_width=True)
            st.markdown("""
                <div class='metric-card'>
                    <p>La volatilidad rolling muestra la variabilidad de los rendimientos en una ventana móvil de 3 meses. 
                    Una mayor volatilidad indica mayor riesgo. Esta visualización ayuda a identificar períodos de mayor 
                    incertidumbre en cada activo.</p>
                </div>
            """, unsafe_allow_html=True)
    
    else:
        if "error" in company1:
            st.error(f"Error con {ticker1}: {company1['error']}")
        if "error" in company2:
            st.error(f"Error con {ticker2}: {company2['error']}")
else:
    st.warning("Por favor ingrese dos símbolos válidos para comparar")




