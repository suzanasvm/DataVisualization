import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

st.set_page_config(layout="centered")

st.title("Análise de Notas de Avaliações")

# Upload de arquivo CSV
uploaded_file = st.file_uploader("Envie um arquivo CSV com a coluna 'Avaliação'", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if 'Avaliação' not in df.columns:
        st.error("O arquivo CSV deve conter uma coluna chamada 'Avaliação'")
    else:
        notas = df['Avaliação'].dropna()

        # Controle de bins
        bins = st.slider("Selecione o número de bins para o histograma", min_value=10, max_value=100, value=30)

        st.subheader("1. Histograma com Curva Gaussiana")

        # Parâmetros para a curva gaussiana
        media = np.mean(notas)
        desvio = np.std(notas)
        x = np.linspace(min(notas), max(notas), 100)
        y = norm.pdf(x, media, desvio)

        # Histograma
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=notas, histnorm='probability density', name='Notas',
            opacity=0.6, marker_color='blue', nbinsx=bins
        ))

        # Curva Gaussiana
        fig_hist.add_trace(go.Scatter(
            x=x, y=y, mode='lines', name='Curva Gaussiana',
            line=dict(color='red', width=2)
        ))

        fig_hist.update_layout(
            xaxis_title='Nota',
            yaxis_title='Densidade (%)',
            bargap=0.1
        )

        # Exibir o gráfico com densidade em porcentagem
        fig_hist.update_yaxes(tickformat=".2%")
        st.plotly_chart(fig_hist, use_container_width=True)

        st.subheader("2. Boxplot das Notas")
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(
            y=notas, boxpoints="all", jitter=0.3, pointpos=-1.8,
            name="Notas", marker_color='purple'
        ))
        fig_box.update_layout(yaxis_title='Nota')
        st.plotly_chart(fig_box, use_container_width=True)

        st.subheader("3. Violin Plot")
        fig_violin = go.Figure()
        fig_violin.add_trace(go.Violin(
            y=notas, box_visible=True, meanline_visible=True,
            name='Notas', line_color='green'
        ))
        fig_violin.update_layout(yaxis_title='Nota')
        st.plotly_chart(fig_violin, use_container_width=True)
else:
    st.info("Faça o upload de um arquivo CSV com uma coluna chamada 'Avaliação'.")
