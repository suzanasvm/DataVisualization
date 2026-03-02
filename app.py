import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(layout="wide")

st.title("Análise de Desempenho por Curso")

menu = st.sidebar.selectbox(
    "Selecione o Menu:",
    ["Notas Gerais", "Habilidades"]
)

arquivo = st.file_uploader("Envie o arquivo dados_completos.csv", type="csv")

if arquivo is not None:
    
    df_detalhado = pd.read_csv(arquivo)

    # Converter todas as questões para número
    colunas_questoes = [
        col for col in df_detalhado.columns
        if col.lower().startswith("q")
    ]

    for col in colunas_questoes:
        df_detalhado[col] = pd.to_numeric(df_detalhado[col], errors="coerce")

    cores = {
        "adm": "#1f77b4",
        "info": "#ff7f0e",
        "agro": "#2ca02c",
        "zoo": "#d62728",
        "alt": "#9467bd"
    }

    # ===============================
    # MENU 1 - NOTAS GERAIS
    # ===============================
    if menu == "Notas Gerais":

        # Separar matemática e português dinamicamente
        questoes_matematica = []
        questoes_portugues = []

        for col in colunas_questoes:
            numero = int(re.findall(r'\d+', col)[0])
            if numero <= 20:
                questoes_matematica.append(col)
            else:
                questoes_portugues.append(col)

        df = df_detalhado.groupby("Curso").mean(numeric_only=True).reset_index()

        if questoes_matematica:
            df["Media_Notas_Matematica"] = df[questoes_matematica].mean(axis=1)
        else:
            df["Media_Notas_Matematica"] = 0

        if questoes_portugues:
            df["Media_Notas_Portugues"] = df[questoes_portugues].mean(axis=1)
        else:
            df["Media_Notas_Portugues"] = 0

        # Média geral considera todas as questões
        if colunas_questoes:
            df["Media_Notas_Geral"] = df[colunas_questoes].mean(axis=1)
            df["Mediana_Notas_Geral"] = df[colunas_questoes].median(axis=1)
        else:
            df["Media_Notas_Geral"] = 0
            df["Mediana_Notas_Geral"] = 0

        df = df[[
            "Curso",
            "Media_Notas_Geral",
            "Mediana_Notas_Geral",
            "Media_Notas_Matematica",
            "Media_Notas_Portugues"
        ]]

        df = df.round(2)

        st.subheader("Tabela de Dados")
        st.dataframe(df)

        opcoes = st.multiselect(
            "Selecione quais gráficos deseja visualizar:",
            ["Geral", "Matemática", "Português"],
            default=["Geral", "Matemática", "Português"]
        )

        def gerar_grafico(coluna, titulo):
            
            df_ordenado = df.sort_values(by=coluna, ascending=False).copy()
            df_ordenado["Percentual"] = (df_ordenado[coluna] / 1) * 100

            df_ordenado["Curso_Formatado"] = df_ordenado["Curso"].apply(
                lambda x: f"<b>{x}</b>"
            )

            fig = px.bar(
                df_ordenado,
                x="Curso_Formatado",
                y="Percentual",
                color="Curso",
                text=df_ordenado["Percentual"].map(lambda x: f"{x:.1f}%"),
                title=titulo,
                color_discrete_map=cores,
                category_orders={"Curso_Formatado": df_ordenado["Curso_Formatado"].tolist()}
            )

            fig.update_traces(textposition="outside")

            fig.update_layout(
                yaxis_title="Desempenho (%)",
                xaxis_title="Curso",
                yaxis=dict(range=[0, 100]),
                showlegend=False
            )

            return fig

        if opcoes:
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

    # ===============================
    # MENU 2 - HABILIDADES
    # ===============================
    elif menu == "Habilidades":

        st.subheader("Análise Diagnóstica por Habilidades")

        questoes_detalhes = {
            "Q.1": "Compreender, comparar e ordenar frações associadas às ideias de partes de inteiros e resultado de divisão, identificando frações equivalentes.",
            "Q.2": "Compreender, comparar e ordenar frações associadas às ideias de partes de inteiros e resultado de divisão, identificando frações equivalentes.",
            "Q.3": "Associar pares ordenados de números a pontos do plano cartesiano do 1º quadrante.",
            "Q.4": "Associar pares ordenados de números a pontos do plano cartesiano do 1º quadrante.",
            "Q.5": "Resolver problemas envolvendo grandezas como comprimento, massa, tempo, temperatura, área e volume.",
            "Q.6": "Resolver problemas envolvendo grandezas como comprimento, massa, tempo, temperatura, área e volume.",
            "Q.7": "Interpretar dados apresentados em tabelas sobre temas como sustentabilidade e consumo.",
            "Q.8": "Interpretar dados apresentados em tabelas sobre temas como sustentabilidade e consumo.",
            "Q.9": "Resolver problemas com operações com números racionais.",
            "Q.10": "Resolver problemas com operações com números racionais.",
            "Q.11": "Resolver problemas com grandezas diretamente ou inversamente proporcionais.",
            "Q.12": "Resolver problemas com grandezas diretamente ou inversamente proporcionais.",
            "Q.13": "Calcular área de figuras geométricas como quadriláteros, triângulos e círculos.",
            "Q.14": "Calcular área de figuras geométricas como quadriláteros, triângulos e círculos.",
            "Q.15": "Resolver equações polinomiais de 1º grau na forma ax + b = c.",
            "Q.16": "Resolver equações polinomiais de 1º grau na forma ax + b = c.",
            "Q.17": "Resolver problemas envolvendo cálculo de porcentagens.",
            "Q.18": "Resolver problemas envolvendo cálculo de porcentagens.",
            "Q.19": "Calcular média, moda e mediana e interpretar dispersão.",
            "Q.20": "Calcular média, moda e mediana e interpretar dispersão."
        }

        colunas_questoes = [
            col for col in df_detalhado.columns
            if col in questoes_detalhes.keys()
        ]

        if colunas_questoes:

            top_x = st.number_input(
                "Quantidade de questões mais difíceis (Top X):",
                min_value=1,
                max_value=len(colunas_questoes),
                value=5,
                step=1
            )

            tipo_visao = st.radio(
                "Selecione a visão:",
                ["Visão Geral", "Comparar Cursos"],
                horizontal=True
            )

            # ============================
            # VISÃO GERAL
            # ============================
            if tipo_visao == "Visão Geral":

                medias = df_detalhado[colunas_questoes].mean().reset_index()
                medias.columns = ["Questao", "Media"]
                medias["Percentual"] = medias["Media"] * 100
                medias["Habilidade"] = medias["Questao"].map(questoes_detalhes)

                medias = medias.sort_values(by="Percentual").head(top_x)

                fig = px.bar(
                    medias,
                    x="Percentual",
                    y="Questao",
                    orientation="h",
                    text=medias["Percentual"].map(lambda x: f"{x:.1f}%"),
                    title=f"Top {top_x} Questões Mais Difíceis - Visão Geral",
                    color="Percentual",
                    color_continuous_scale="RdYlGn"
                )

                fig.update_traces(textposition="outside")

                fig.update_layout(
                    xaxis_title="Percentual Médio de Acertos",
                    yaxis_title="Questão",
                    height=500
                )

                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Habilidades Relacionadas")
                st.dataframe(medias[["Questao", "Habilidade", "Percentual"]])

            # ============================
            # COMPARAR CURSOS
            # ============================
            else:

                lista_cursos = sorted(df_detalhado["Curso"].unique())

                cursos_selecionados = st.multiselect(
                    "Selecione os cursos para comparar:",
                    lista_cursos,
                    default=lista_cursos
                )

                if cursos_selecionados:

                    colunas_layout = st.columns(len(cursos_selecionados))

                    for i, curso in enumerate(cursos_selecionados):

                        df_curso = df_detalhado[df_detalhado["Curso"] == curso]

                        medias = df_curso[colunas_questoes].mean().reset_index()
                        medias.columns = ["Questao", "Media"]
                        medias["Percentual"] = medias["Media"] * 100
                        medias["Habilidade"] = medias["Questao"].map(questoes_detalhes)

                        medias = medias.sort_values(by="Percentual").head(top_x)

                        with colunas_layout[i]:

                            fig = px.bar(
                                medias,
                                x="Percentual",
                                y="Questao",
                                orientation="h",
                                text=medias["Percentual"].map(lambda x: f"{x:.1f}%"),
                                title=f"{curso} - Top {top_x}",
                                color="Percentual",
                                color_continuous_scale="RdYlGn"
                            )

                            fig.update_traces(textposition="outside")

                            fig.update_layout(
                                xaxis_title="%",
                                yaxis_title="Questão",
                                height=500
                            )

                            st.plotly_chart(fig, use_container_width=True)

                    st.subheader("Legenda das Habilidades")

                    legenda = pd.DataFrame({
                        "Questao": list(questoes_detalhes.keys()),
                        "Habilidade": list(questoes_detalhes.values())
                    })

                    st.dataframe(legenda)

                else:
                    st.info("Selecione pelo menos um curso para comparar.")

        else:
            st.warning("Nenhuma questão correspondente encontrada.")