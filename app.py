import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

st.set_page_config(layout="wide")

st.title("Avaliação Diagnóstica - IFNMG - 1°anos")

menu = st.sidebar.selectbox(
    "Selecione o Menu:",
    ["Notas Gerais - Matemática", "Habilidades - Matemática", "Habilidades Língua Portuguesa"]
)

cores = {
    "adm": "#1f77b4",
    "info": "#ff7f0e",
    "agro": "#2ca02c",
    "zoo": "#d62728",
    "alt": "#9467bd"
}

# ===============================
# MENU 1 e 2 - arquivo original
# ===============================
if menu in ["Notas Gerais - Matemática", "Habilidades - Matemática"]:

    arquivo = st.file_uploader("Envie o arquivo dados_completos.csv", type="csv")

    if arquivo is not None:

        df_detalhado = pd.read_csv(arquivo)

        colunas_questoes = [
            col for col in df_detalhado.columns
            if col.lower().startswith("q")
        ]

        for col in colunas_questoes:
            df_detalhado[col] = pd.to_numeric(df_detalhado[col], errors="coerce")

        # ===============================
        # MENU 1 - Notas Gerais - Matemática
        # ===============================
        if menu == "Notas Gerais - Matemática":

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
                default=["Matemática"]
            )

            espessura_barra = st.number_input(
                "Espessura das barras (0.1 a 1.0):",
                min_value=0.1,
                max_value=1.0,
                value=0.8,
                step=0.1
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

                fig.update_traces(
                    textposition="outside",
                    width=espessura_barra
                )

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
        elif menu == "Habilidades - Matemática":

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

                if tipo_visao == "Visão Geral":

                    medias = df_detalhado[colunas_questoes].mean().reset_index()
                    medias.columns = ["Questao", "Media"]
                    medias["Percentual"] = medias["Media"] * 100
                    medias["Habilidade"] = medias["Questao"].map(questoes_detalhes)

                    medias = medias.sort_values(by="Percentual", ascending=True).head(top_x)

                    fig = px.bar(
                        medias,
                        x="Percentual",
                        y="Questao",
                        orientation="h",
                        text=medias["Percentual"].map(lambda x: f"{x:.1f}%"),
                        title=f"Top {top_x} Questões Mais Difíceis - Visão Geral",
                        color="Percentual",
                        color_continuous_scale="RdYlGn",
                        range_color=[0, 100],
                        category_orders={"Questao": medias["Questao"].tolist()}
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

                            medias = medias.sort_values(by="Percentual", ascending=True).head(top_x)

                            with colunas_layout[i]:

                                fig = px.bar(
                                    medias,
                                    x="Percentual",
                                    y="Questao",
                                    orientation="h",
                                    text=medias["Percentual"].map(lambda x: f"{x:.1f}%"),
                                    title=f"{curso} - Top {top_x}",
                                    color="Percentual",
                                    color_continuous_scale="RdYlGn",
                                    range_color=[0, 100],
                                    category_orders={"Questao": medias["Questao"].tolist()}
                                )

                                fig.update_traces(textposition="outside")

                                fig.update_layout(
                                    xaxis_title="Percentual Médio",
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

# ===============================
# MENU 3 - HABILIDADES LÍNGUA PORTUGUESA
# ===============================
elif menu == "Habilidades Língua Portuguesa":

    st.subheader("Análise de Habilidades em Língua Portuguesa")

    arquivo_lp = st.file_uploader("Envie o arquivo CSV de Língua Portuguesa", type="csv")

    if arquivo_lp is not None:

        df_lp = pd.read_csv(arquivo_lp)

        # Definição das categorias de demanda
        demandas_urgentes = [
            "ESCRITA EM BLOCO",
            "PARAGRAFAÇÃO",
            "CALIGRAFIA",
            "ORTOGRAFIA",
            "SEPARAÇÃO SILÁBICA",
            "ACENTUAÇÃO",
            "PONTUAÇÃO",
        ]

        demandas_secundarias = [
            "REGÊNCIA",
            "CONCORDÂNCIA",
            "TRUNCAMENTOS",
            "JUSTAPOSIÇÕES",
        ]

        # Identificar colunas presentes no CSV
        colunas_urgentes = [col for col in demandas_urgentes if col in df_lp.columns]
        colunas_secundarias = [col for col in demandas_secundarias if col in df_lp.columns]

        if not colunas_urgentes and not colunas_secundarias:
            st.error("Nenhuma coluna de habilidades reconhecida foi encontrada no arquivo.")
            st.info(f"Colunas esperadas: {demandas_urgentes + demandas_secundarias}")
            st.info(f"Colunas encontradas: {list(df_lp.columns)}")
        else:

            # Converter colunas para numérico
            for col in colunas_urgentes + colunas_secundarias:
                df_lp[col] = pd.to_numeric(df_lp[col], errors="coerce").fillna(0)

            col_curso = "Curso" if "Curso" in df_lp.columns else None

            if col_curso is None:
                st.error("Coluna 'Curso' não encontrada no arquivo.")
            else:

                lista_cursos = sorted(df_lp[col_curso].unique())

                # Calcular % de alunos com valor 1 por curso e por item
                resumo_por_curso = []

                for curso in lista_cursos:
                    df_curso = df_lp[df_lp[col_curso] == curso]
                    total = len(df_curso)

                    row = {"Curso": curso, "Total Alunos": total}

                    for col in colunas_urgentes + colunas_secundarias:
                        pct = (df_curso[col] == 1).sum() / total * 100 if total > 0 else 0
                        row[col] = round(pct, 1)

                    # Percentual médio por categoria
                    if colunas_urgentes:
                        vals = [(df_curso[c] == 1).sum() / total * 100 for c in colunas_urgentes]
                        row["Media_Urgentes"] = round(sum(vals) / len(vals), 1)
                    else:
                        row["Media_Urgentes"] = 0

                    if colunas_secundarias:
                        vals = [(df_curso[c] == 1).sum() / total * 100 for c in colunas_secundarias]
                        row["Media_Secundarias"] = round(sum(vals) / len(vals), 1)
                    else:
                        row["Media_Secundarias"] = 0

                    resumo_por_curso.append(row)

                df_resumo = pd.DataFrame(resumo_por_curso)

                # ============================
                # VISÃO COMPARATIVA ENTRE CURSOS
                # ============================
                st.markdown("### Comparativo Geral por Curso")
                st.caption("Percentual médio de alunos com ocorrência (valor = 1) por categoria de demanda")

                fig_comp = go.Figure()

                fig_comp.add_trace(go.Bar(
                    name="Demandas Urgentes",
                    x=df_resumo["Curso"],
                    y=df_resumo["Media_Urgentes"],
                    marker_color="#d62728",
                    text=df_resumo["Media_Urgentes"].map(lambda x: f"{x:.1f}%"),
                    textposition="outside"
                ))

                fig_comp.add_trace(go.Bar(
                    name="Demandas Secundárias",
                    x=df_resumo["Curso"],
                    y=df_resumo["Media_Secundarias"],
                    marker_color="#ff7f0e",
                    text=df_resumo["Media_Secundarias"].map(lambda x: f"{x:.1f}%"),
                    textposition="outside"
                ))

                fig_comp.update_layout(
                    barmode="group",
                    yaxis=dict(range=[0, 110], title="% de Alunos com Ocorrência"),
                    xaxis_title="Curso",
                    legend_title="Categoria",
                    height=450
                )

                st.plotly_chart(fig_comp, use_container_width=True)

                # ============================
                # GRÁFICO POR CURSO - DETALHADO
                # ============================
                st.markdown("### Detalhamento por Curso e Item")
                st.caption("Selecione os cursos para visualizar o detalhamento por habilidade")

                cursos_selecionados = st.multiselect(
                    "Selecione os cursos:",
                    lista_cursos,
                    default=lista_cursos
                )

                if cursos_selecionados:

                    col_grossura, col_quebra = st.columns([1, 2])
                    with col_grossura:
                        grossura_barras = st.number_input(
                            "Grossura das barras (0.1 a 1.0):",
                            min_value=0.1,
                            max_value=1.0,
                            value=0.6,
                            step=0.05,
                            key="grossura_lp"
                        )
                    with col_quebra:
                        quebrar_linha = st.checkbox(
                            "Quebrar em linhas (máx. 3 por linha)",
                            value=False,
                            key="quebra_lp"
                        )

                    if quebrar_linha:
                        n_cols = min(len(cursos_selecionados), 3)
                        rows = [cursos_selecionados[i:i+n_cols] for i in range(0, len(cursos_selecionados), n_cols)]
                    else:
                        rows = [cursos_selecionados]

                    for row_cursos in rows:
                        colunas_layout = st.columns(len(row_cursos))

                        for i, curso in enumerate(row_cursos):

                            df_curso_row = df_resumo[df_resumo["Curso"] == curso].iloc[0]
                            total_alunos = int(df_curso_row["Total Alunos"])

                            itens = []
                            percentuais = []
                            categorias = []
                            cores_item = []

                            for col in colunas_urgentes:
                                itens.append(col)
                                percentuais.append(df_curso_row[col])
                                categorias.append("Demanda Urgente")
                                cores_item.append("#d62728")

                            for col in colunas_secundarias:
                                itens.append(col)
                                percentuais.append(df_curso_row[col])
                                categorias.append("Demanda Secundária")
                                cores_item.append("#ff7f0e")

                            df_plot = pd.DataFrame({
                                "Item": itens,
                                "Percentual": percentuais,
                                "Categoria": categorias,
                                "Cor": cores_item
                            })

                            # Ordenar: urgentes primeiro (desc percentual), depois secundárias (desc percentual)
                            df_plot["ordem_cat"] = df_plot["Categoria"].map({
                                "Demanda Urgente": 0,
                                "Demanda Secundária": 1
                            })
                            df_plot = df_plot.sort_values(
                                by=["ordem_cat", "Percentual"],
                                ascending=[True, False]
                            ).reset_index(drop=True)

                            # Inserir separador visual entre os grupos
                            SEPARADOR = "─────────────────"
                            if colunas_urgentes and colunas_secundarias:
                                idx_primeira_sec = df_plot[df_plot["Categoria"] == "Demanda Secundária"].index[0]
                                sep_row = pd.DataFrame([{
                                    "Item": SEPARADOR,
                                    "Percentual": 0,
                                    "Categoria": "Separador",
                                    "Cor": "rgba(0,0,0,0)",
                                    "ordem_cat": 0.5
                                }])
                                df_plot = pd.concat([
                                    df_plot.iloc[:idx_primeira_sec],
                                    sep_row,
                                    df_plot.iloc[idx_primeira_sec:]
                                ]).reset_index(drop=True)

                            # Ordem do eixo Y (de baixo para cima no gráfico horizontal)
                            ordem_y = df_plot["Item"].tolist()[::-1]
                            total_itens = len(df_plot)

                            with colunas_layout[i]:

                                fig = go.Figure()

                                for _, r in df_plot.iterrows():
                                    if r["Item"] == SEPARADOR:
                                        # Barra invisível só para ocupar espaço
                                        fig.add_trace(go.Bar(
                                            x=[0],
                                            y=[r["Item"]],
                                            orientation="h",
                                            marker_color="rgba(0,0,0,0)",
                                            showlegend=False,
                                            hoverinfo="skip"
                                        ))
                                    else:
                                        fig.add_trace(go.Bar(
                                            name=r["Categoria"],
                                            x=[r["Percentual"]],
                                            y=[r["Item"]],
                                            orientation="h",
                                            marker_color=r["Cor"],
                                            text=f"{r['Percentual']:.1f}%",
                                            textposition="outside",
                                            showlegend=False
                                        ))

                                fig.update_layout(
                                    title=f"<b>{curso}</b><br><sup>{total_alunos} alunos</sup>",
                                    xaxis=dict(range=[0, 130], title="% com Ocorrência"),
                                    yaxis=dict(
                                        title="",
                                        categoryorder="array",
                                        categoryarray=ordem_y,
                                        tickfont=dict(size=12),
                                        ticklabeloverflow="allow"
                                    ),
                                    height=120 + (total_itens * 55),
                                    margin=dict(l=15, r=40, t=90, b=50),
                                    barmode="overlay",
                                    bargap=round(1 - grossura_barras, 2),
                                )

                                # Anotações de legenda de categoria
                                if colunas_urgentes and colunas_secundarias:
                                    fig.add_annotation(
                                        text="🔴 Demandas Urgentes",
                                        xref="paper", yref="paper",
                                        x=0, y=1.09,
                                        showarrow=False,
                                        font=dict(color="#d62728", size=11)
                                    )
                                    fig.add_annotation(
                                        text="🟠 Demandas Secundárias",
                                        xref="paper", yref="paper",
                                        x=0, y=1.03,
                                        showarrow=False,
                                        font=dict(color="#ff7f0e", size=11)
                                    )

                                st.plotly_chart(fig, use_container_width=True)

                else:
                    st.info("Selecione pelo menos um curso.")

                # ============================
                # ANÁLISE: ALUNOS COM MAIS DE X DEMANDAS URGENTES
                # ============================
                st.markdown("---")
                st.markdown("### Alunos com Alto Número de Demandas Urgentes")
                st.caption("Percentual de alunos com mais de X itens urgentes marcados como 1")

                col_x, _ = st.columns([1, 3])
                with col_x:
                    limite_x = st.number_input(
                        "Mínimo de demandas urgentes (X):",
                        min_value=1,
                        max_value=len(colunas_urgentes) if colunas_urgentes else 7,
                        value=4,
                        step=1,
                        key="limite_urgentes"
                    )

                if colunas_urgentes:

                    df_lp["_total_urgentes"] = df_lp[colunas_urgentes].sum(axis=1)

                    dados_urgencia = []
                    for curso in lista_cursos:
                        df_c = df_lp[df_lp[col_curso] == curso]
                        total = len(df_c)
                        acima = df_c[df_c["_total_urgentes"] > limite_x]
                        pct = round(len(acima) / total * 100, 1) if total > 0 else 0
                        dados_urgencia.append({
                            "Curso": curso,
                            "Total Alunos": total,
                            f"Com mais de {limite_x} urgentes": len(acima),
                            "Percentual (%)": pct
                        })

                    df_urgencia = pd.DataFrame(dados_urgencia).sort_values("Percentual (%)", ascending=False)

                    fig_urg = px.bar(
                        df_urgencia,
                        x="Curso",
                        y="Percentual (%)",
                        color="Curso",
                        color_discrete_map=cores,
                        text=df_urgencia["Percentual (%)"].map(lambda v: f"{v:.1f}%"),
                        title=f"% de alunos com mais de {limite_x} demandas urgentes por curso - Língua Portuguesa",
                    )

                    fig_urg.update_traces(textposition="outside")
                    fig_urg.update_layout(
                        yaxis=dict(range=[0, 110], title="% de Alunos"),
                        xaxis_title="Curso",
                        height=400
                    )

                    st.plotly_chart(fig_urg, use_container_width=True)

                    st.dataframe(df_urgencia, use_container_width=True, hide_index=True)

                    with st.expander(f"📋 Ver lista de alunos com mais de {limite_x} demandas urgentes"):
                        col_nome = "NOME" if "NOME" in df_lp.columns else df_lp.columns[0]
                        for curso in lista_cursos:
                            df_c = df_lp[df_lp[col_curso] == curso]
                            alunos_acima = df_c[df_c["_total_urgentes"] > limite_x][[col_nome, "_total_urgentes"] + colunas_urgentes].copy()
                            alunos_acima = alunos_acima.rename(columns={"_total_urgentes": "Total Urgentes"})
                            alunos_acima = alunos_acima.sort_values("Total Urgentes", ascending=False)

                            if len(alunos_acima) > 0:
                                st.markdown(f"**{curso}** — {len(alunos_acima)} aluno(s)")
                                st.dataframe(alunos_acima, use_container_width=True, hide_index=True)
                            else:
                                st.markdown(f"**{curso}** — nenhum aluno acima do limite")

                # ============================
                # TABELA RESUMO
                # ============================
                st.markdown("---")
                st.markdown("### Tabela Resumo")

                colunas_exibir = ["Curso", "Total Alunos", "Media_Urgentes", "Media_Secundarias"] + colunas_urgentes + colunas_secundarias
                colunas_exibir = [c for c in colunas_exibir if c in df_resumo.columns]

                df_exibir = df_resumo[colunas_exibir].copy()
                df_exibir = df_exibir.rename(columns={
                    "Media_Urgentes": "Média Urgentes (%)",
                    "Media_Secundarias": "Média Secundárias (%)"
                })

                st.dataframe(df_exibir, use_container_width=True)

    else:
        st.info("📂 Envie o arquivo CSV com os dados de Língua Portuguesa para começar.")
        st.markdown("""
        **Formato esperado do arquivo:**
        - Coluna `NOME`: nome do aluno
        - Coluna `Curso`: curso do aluno (ex: agro, info, adm...)
        - Colunas de habilidades com valor `1` (presença) ou vazio/0 (ausência):
            - **Demandas Urgentes:** ESCRITA EM BLOCO, PARAGRAFAÇÃO, CALIGRAFIA, ORTOGRAFIA, SEPARAÇÃO SILÁBICA, ACENTUAÇÃO, PONTUAÇÃO
            - **Demandas Secundárias:** REGÊNCIA, CONCORDÂNCIA, TRUNCAMENTOS, JUSTAPOSIÇÕES
        """)
