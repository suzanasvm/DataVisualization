import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Análise de Desempenho por Curso")

arquivo = st.file_uploader("Envie o arquivo resumo_cursos.csv", type="csv")

if arquivo is not None:
    
    df = pd.read_csv(arquivo)
    
    st.subheader("Tabela de Dados")
    st.dataframe(df)

    opcoes = st.multiselect(
        "Selecione quais gráficos deseja visualizar:",
        ["Geral", "Matemática", "Português"],
        default=["Geral", "Matemática", "Português"]
    )

    st.subheader("Avaliação Diagnóstica")

    cores = {
        "adm": "#1f77b4",
        "info": "#ff7f0e",
        "agro": "#2ca02c",
        "zoo": "#d62728",
        "alt": "#9467bd"
    }

    # Legenda única
    legenda_html = ""
    for curso, cor in cores.items():
        if curso in df["Curso"].values:
            legenda_html += f"""
            <span style='display:inline-block;margin-right:20px;'>
                <span style='display:inline-block;width:12px;height:12px;
                background-color:{cor};margin-right:5px;'></span>
                {curso}
            </span>
            """

    st.markdown(legenda_html, unsafe_allow_html=True)

    def gerar_grafico(coluna, titulo):
        
        df_ordenado = df.sort_values(by=coluna, ascending=False)
        media_geral = df_ordenado[coluna].mean()

        fig = px.bar(
            df_ordenado,
            x="Curso",
            y=coluna,
            color="Curso",
            text=coluna,
            title=titulo,
            color_discrete_map=cores,
            category_orders={"Curso": df_ordenado["Curso"].tolist()}
        )
        nota_esperada = 12
        fig.add_hline(
            y=nota_esperada,
            line_dash="dash",
            annotation_text=f"Nota Esperada",
            annotation_position="top left"
        )

        fig.update_traces(textposition="outside")

        fig.update_layout(
            yaxis_title="Média de Notas",
            xaxis_title="Curso",
            showlegend=False
        )

        return fig

    if len(opcoes) > 0:
        colunas = st.columns(len(opcoes))

        for i, opcao in enumerate(opcoes):
            with colunas[i]:

                if opcao == "Geral":
                    fig = gerar_grafico("Media_Notas_Geral", "Média Geral")

                elif opcao == "Matemática":
                    fig = gerar_grafico("Media_Notas_Matematica", "Média em Matemática")

                elif opcao == "Português":
                    fig = gerar_grafico("Media_Notas_Portugues", "Média em Português")

                st.plotly_chart(fig, use_container_width=True)