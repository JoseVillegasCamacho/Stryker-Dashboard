import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

def app():
    # Leer archivo
    df = pd.read_excel('datos_reales.xlsx')
    
    # Filtrado inicial para asegurar que solo incluya los equipos correctos
    df = df[df.iloc[:, 7].isin(['Credit Risk', 'Invoice Delivery'])]
    
    # Mapeo actualizado de ganadores
    ganadores = {
        '2026-07-07': {'Invoice Delivery': ['Raquel Sandí'], 'Credit Risk': ['Leo Alvarado']},
        '2026-07-08': {'Invoice Delivery': ['Deykell Wilson'], 'Credit Risk': ['Wendys Flores']},
        '2026-07-09': {'Invoice Delivery': ['Deykell Wilson'], 'Credit Risk': ['Wendys Flores']},
        '2026-07-14': {'Invoice Delivery': ['Deykell Wilson'], 'Credit Risk': ['Guiselle Melendez']},
        '2026-07-15': {'Invoice Delivery': ['Susana Mora'], 'Credit Risk': ['Guiselle Melendez']},
        '2026-07-16': {'Invoice Delivery': ['Jessica Esquivel'], 'Credit Risk': ['Wendys Flores']},
        '2026-07-21': {'Invoice Delivery': ['Kattia Soto', 'Michael Perez'], 'Credit Risk': ['Guiselle Melendez']},
        '2026-07-22': {'Invoice Delivery': ['Ericka Fernandez'], 'Credit Risk': ['Guiselle Melendez']},
        '2026-07-23': {'Invoice Delivery': ['Maria Jose Paniagua'], 'Credit Risk': ['Guiselle Melendez']}
    }

    def calcular_punto(row):
        fecha_val = pd.to_datetime(row.iloc[6]).strftime('%Y-%m-%d')
        equipo = str(row.iloc[7]).strip()
        if fecha_val in ganadores and equipo in ganadores[fecha_val]:
            objetivos = ganadores[fecha_val][equipo]
            # Buscamos en las columnas de votos (del índice 8 al 11) si votó por cualquiera de los ganadores del día
            for i in range(8, 12):
                voto = str(row.iloc[i]).strip()
                if voto in objetivos:
                    return 1
        return 0

    df['Aciertos'] = df.apply(calcular_punto, axis=1)
    
    # --- UI ESTÉTICA ---
    st.title("Stryker")
    st.subheader("🏆 LEADERBOARD SEMANAL: R7 DRESS TO DEPLOY")

    # Banner de Campeones
    res = df.groupby(df.columns[4])['Aciertos'].sum().reset_index()
    max_aciertos = res['Aciertos'].max()
    campeones = res[res['Aciertos'] == max_aciertos]['Name'].tolist()
    
    msg = "¡EMPATE!" if len(campeones) > 1 else "¡CAMPEÓN!"
    st.markdown(f"""
    <div style="background-color: #FFB81C; padding: 20px; border-radius: 10px; text-align: center; color: black;">
        <h3>🔥 {msg} 🔥</h3>
        <p>Con {max_aciertos} aciertos, nuestros campeones actuales son:</p>
        <p><b>✨ {' & '.join(campeones)}</b></p>
    </div>
    """, unsafe_allow_html=True)

    # Líderes por Equipo
    st.markdown("### 🎯 Líderes por Equipo")
    c1, c2 = st.columns(2)
    for i, equipo in enumerate(['Credit Risk', 'Invoice Delivery']):
        subset = df[df.iloc[:, 7] == equipo].groupby(df.columns[4])['Aciertos'].sum()
        sub = subset.idxmax()
        val = subset.max()
        with (c1 if i == 0 else c2):
            st.metric(equipo, f"{val} aciertos", sub)

    # Clasificación y Rendimiento
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("### 📋 Clasificación Completa")
        st.dataframe(res.sort_values(by='Aciertos', ascending=False), use_container_width=True, hide_index=True)
    with c4:
        st.markdown("### 📊 Rendimiento por Equipo")
        fig = px.bar(df.groupby(df.columns[7])['Aciertos'].sum().reset_index(), 
                     x=df.columns[7], y='Aciertos', color_discrete_sequence=['#FFB81C'])
        fig.update_yaxes(dtick=1)
        fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)

app()