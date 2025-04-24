import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Mapeamento dos níveis
mapa_niveis = {
    '00. Nao esperado': 0,
    '01. Aprendiz': 1,
    '02. Iniciante': 2,
    '03. Profissional': 3,
    '04. Expert': 4,
    '05. Professor': 5
}
cores_niveis = {
    '00. Nao esperado': '#ffffff',
    '01. Aprendiz': '#cce5ff',
    '02. Iniciante': '#99ccff',
    '03. Profissional': '#66b2ff',
    '04. Expert': '#3399ff',
    '05. Professor': '#0066cc'
}

def carregar_dados(pasta):
    dfs = []
    for arquivo in os.listdir(pasta):
        if arquivo.endswith('.xlsx'):
            try:
                caminho = os.path.join(pasta, arquivo)
                df = pd.read_excel(caminho)
                print(f"Lendo arquivo: {arquivo}")
                df = df.dropna(subset=["Habilidade", "Nível"])
                df["Nivel_num"] = df["Nível"].map(mapa_niveis)
                dfs.append(df[["Habilidade", "Nivel_num"]])
            except Exception as e:
                st.warning(f"Erro ao processar {arquivo}: {e}")
    if dfs:
        try:
            return pd.concat(dfs, ignore_index=True)
        except Exception as e:
            st.error(f"Erro ao concatenar os dados: {e}")
            return pd.DataFrame(columns=["Habilidade", "Nivel_num"])
    else:
        st.warning("Nenhum dado válido foi encontrado.")
        return pd.DataFrame(columns=["Habilidade", "Nivel_num"])

def gerar_dashboard(df):
    try:
        st.title("Habilidades dos Alunos IFNMG Banco de Dados 2  - 2025")

        st.subheader("Habilidades com maior dificuldade geral")
        df_dificuldade = df[df["Nivel_num"] <= 2]
        dificuldade_por_habilidade = df_dificuldade.groupby("Habilidade").size().sort_values(ascending=False)
        st.dataframe(dificuldade_por_habilidade.rename("Qtd alunos com dificuldade"))

        st.subheader("Percentual de dificuldade por habilidade")
        total_por_habilidade = df.groupby("Habilidade").size()
        percentual_dificuldade = (dificuldade_por_habilidade / total_por_habilidade * 100).fillna(0)
        percentual_dificuldade = percentual_dificuldade.sort_values(ascending=False)
        st.dataframe(percentual_dificuldade.rename("% com dificuldade").round(2))

        # Top 10 habilidades com maior percentual de dificuldade
        top_10_habilidades = percentual_dificuldade.head(10).index.tolist()

        st.subheader("Distribuição dos Níveis nas 10 Habilidades com maior dificuldade (horizontal)")

        # Filtrar e preparar os dados
        df_top10 = df[df["Habilidade"].isin(top_10_habilidades)]
        df_top10["Habilidade"] = pd.Categorical(df_top10["Habilidade"], categories=top_10_habilidades[::-1], ordered=True)

        # Contar a quantidade por nível e habilidade
        contagem = df_top10.groupby(["Habilidade", "Nivel_num"]).size().reset_index(name="Quantidade")
        contagem["Nivel_nome"] = contagem["Nivel_num"].map({v: k for k, v in mapa_niveis.items()})

        # Gráfico interativo com cores customizadas (branco a azul escuro)
        fig = px.bar(
            contagem,
            x="Quantidade",
            y="Habilidade",
            color="Nivel_nome",
            orientation="h",
            title="Distribuição dos Níveis nas 10 Habilidades com maior dificuldade",
            color_discrete_map=cores_niveis
        )
        fig.update_layout(
            barmode='stack',
            yaxis_title="Habilidade",
            xaxis_title="Quantidade de Alunos",
            legend_title="Nível de Conhecimento"
        )
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Ocorreu um erro ao gerar o dashboard: {e}")

if __name__ == "__main__":
    st.sidebar.title("Configuração")
    pasta = st.sidebar.text_input("📂 Caminho da pasta com arquivos XLSX", value="./planilhas")
    if os.path.exists(pasta):
        try:
            dados = carregar_dados(pasta)
            if not dados.empty:
                gerar_dashboard(dados)
            else:
                st.warning("Nenhum dado carregado para exibir no dashboard.")
        except Exception as e:
            st.error(f"Erro durante o processamento: {e}")
    else:
        st.error("Pasta não encontrada. Verifique o caminho.")
