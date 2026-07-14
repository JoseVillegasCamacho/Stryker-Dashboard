import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Quiniela R7", layout="wide")

# Estilos CSS con el color exacto solicitado
st.markdown("""
    <style>
    .winner-box {
        background-color: #FFB81C;
        padding: 25px;
        border-radius: 15px;
        color: #000000;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        margin-bottom: 25px;
        border: 2px solid #e6a500;
    }
    .tie-box {
        background-color: #FFB81C;
        padding: 25px;
        border-radius: 15px;
        color: #000000;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        margin-bottom: 25px;
        border: 2px solid #e6a500;
    }
    h2, h3 { color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def cargar_y_procesar():
    df = pd.read_excel('datos_reales.xlsx', dtype=str)
    col_fecha = df.columns[6]
    col_equipo = df.columns[7]
    df = df[df[col_equipo].isin(['Credit Risk', 'Invoice Delivery'])]
    
    ganadores_por_fecha = {
        "7": {"Invoice Delivery": "Raquel Sandí", "Credit Risk": "Leo Alvarado"},
        "8": {"Invoice Delivery": "Deykell Wilson", "Credit Risk": "Wendys Flores"},
        "9": {"Invoice Delivery": "Deykell Wilson", "Credit Risk": "Wendys Flores"}
    }
    mapeo_dia = {"6": "7", "7": "8", "8": "9"}
    
    def evaluar_acierto(row):
        fecha_voto_raw = str(row[col_fecha])
        equipo = str(row[col_equipo]).strip()
        dia_voto = fecha_voto_raw.split('-')[2].split(' ')[0].lstrip('0')
        dia_evento = mapeo_dia.get(dia_voto)
        
        if dia_evento and equipo in ganadores_por_fecha.get(dia_evento, {}):
            col_voto = next((c for c in df.columns if equipo in c), None)
            voto = str(row.get(col_voto, "")).strip()
            ganador_real = ganadores_por_fecha[dia_evento][equipo]
            return 1 if ganador_real.lower() in voto.lower() else 0
        return 0

    df["Aciertos"] = df.apply(evaluar_acierto, axis=1)
    return df

try:
    df = cargar_y_procesar()
    leaderboard = df.groupby("Name")["Aciertos"].sum().reset_index().sort_values(by="Aciertos", ascending=False)
    
    st.title("Stryker")
    st.subheader("🏆 LEADERBOARD SEMANAL: R7 DRESS TO DEPLOY")
    
    # UI ESTÉTICA
    if not leaderboard.empty:
        max_aciertos = leaderboard['Aciertos'].max()
        lideres = leaderboard[leaderboard['Aciertos'] == max_aciertos]
        
        if len(lideres) > 1:
            st.markdown(f"""
            <div class="tie-box">
                <h2>🔥 ¡EMPATE! 🔥</h2>
                <p style="font-size: 20px;">Con <b>{int(max_aciertos)} aciertos</b>, nuestros campeones actuales son:</p>
                <h3>✨ {' & '.join(lideres['Name'].tolist())} ✨</h3>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="winner-box">
                <h2>👑 ¡LÍDER ABSOLUTO! 👑</h2>
                <p style="font-size: 24px;"><b>{lideres.iloc[0]['Name']}</b></p>
                <p style="font-size: 18px;">Dominando con <b>{int(max_aciertos)} aciertos</b></p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Líderes por Equipo (Más juntos)
    st.subheader("🎯 Líderes por Equipo")
    _, c_cr, c_id, _ = st.columns([1, 2, 2, 1])
    
    equipos = {'Credit Risk': c_cr, 'Invoice Delivery': c_id}
    for equipo, col in equipos.items():
        df_equipo = df[df[df.columns[7]] == equipo]
        lb_equipo = df_equipo.groupby("Name")["Aciertos"].sum().reset_index().sort_values(by="Aciertos", ascending=False)
        
        if not lb_equipo.empty:
            max_eq = lb_equipo['Aciertos'].max()
            lideres_eq = lb_equipo[lb_equipo['Aciertos'] == max_eq]
            col.metric(f"{equipo}", f"{int(max_eq)} aciertos", f"{', '.join(lideres_eq['Name'].tolist())}")

    st.markdown("---")
    
    # Clasificación y Gráfico
    c_tabla, c_grafico = st.columns([1, 1])
    with c_tabla:
        st.markdown("### 📋 Clasificación Completa")
        st.dataframe(leaderboard, hide_index=True, use_container_width=True)
    with c_grafico:
        st.markdown("### 📊 Rendimiento por Equipo")
        # Gráfico con color corporativo
        fig = px.bar(df.groupby(df.columns[7])["Aciertos"].sum().reset_index(), 
                     x=df.columns[7], y="Aciertos", color_discrete_sequence=['#FFB81C'])
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error técnico: {e}")
