import streamlit as st
import pandas as pd
import os
import io
import zipfile
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Border, Side
from xhtml2pdf import pisa
from io import BytesIO
import base64

st.set_page_config(layout="wide")
st.title("Conselho de Classe IFNMG Almenara")

# Parâmetros iniciais
pasta_boletins = "boletim_saida"
arquivos_disponiveis = {
    "Agropecuária - 1º ano": "agro1_boletim.csv",
    "Agropecuária - 2º ano": "agro2_boletim.csv",
    "Agropecuária - 3º ano": "agro3_boletim.csv",
    "Informática - 1º ano": "info1_boletim.csv",
    "Informática - 2º ano": "info2_boletim.csv",
    "Informática - 3º ano": "info3_boletim.csv",
    "Administração - 1º ano": "adm1_boletim.csv",
    "Administração - 2º ano": "adm2_boletim.csv",
    "Administração - 3º ano": "adm3_boletim.csv",
    "Zootecnia - 1º ano": "zoo1_boletim.csv",
    "Zootecnia - 2º ano": "zoo2_boletim.csv",
    "Zootecnia - 3º ano": "zoo3_boletim.csv",
    "Alternância - 1º ano": "alt1_boletim.csv",
    "Alternância - 2º ano": "alt2_boletim.csv",
    "Alternância - 3º ano": "alt3_boletim.csv"
}

# Filtros na barra lateral
st.sidebar.header("⚙️ Configurações")
turma_escolhida = st.sidebar.selectbox("Selecione a turma:", list(arquivos_disponiveis.keys()))
nota_corte = st.sidebar.number_input("Nota de corte", min_value=0, max_value=100, value=30)
num_letras = st.sidebar.number_input("Letras para abreviação de disciplina", min_value=1, max_value=10, value=3)
#zi

def gerar_excel(df_final, nota_corte, disciplinas_zeradas):
    output = io.BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = 'Desempenho'

    border = Border(left=Side(style="thin"), right=Side(style="thin"), top=Side(style="thin"), bottom=Side(style="thin"))
    red_fill = PatternFill(start_color="F8D7DA", end_color="F8D7DA", fill_type="solid")
    green_fill = PatternFill(start_color="D4EDDA", end_color="D4EDDA", fill_type="solid")
    yellow_fill = PatternFill(start_color="FFF3CD", end_color="FFF3CD", fill_type="solid")

    headers = ['Nome'] + list(df_final.columns)
    for col_num, col_name in enumerate(headers, 1):
        ws.cell(row=1, column=col_num, value=col_name)

    for row_num, (index, row) in enumerate(df_final.iterrows(), 2):
        ws.cell(row=row_num, column=1, value=index)
        for col_num, value in enumerate(row, 2):
            try:
                val = float(value)
            except:
                val = value
            cell = ws.cell(row=row_num, column=col_num, value=val)
            if isinstance(val, float):
                if headers[col_num - 1] == headers[-2]:
                    pass
                elif headers[col_num - 1] in disciplinas_zeradas:
                    cell.fill = yellow_fill
                elif val < nota_corte:
                    cell.fill = red_fill
                else:
                    cell.fill = green_fill
            cell.border = border

    wb.save(output)
    output.seek(0)
    return output

# Função para gerar arquivos Excel e PDF para todas as turmas
def gerar_zip_de_todas_as_turmas():
    # Inicializa o arquivo ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for turma, arquivo in arquivos_disponiveis.items():
            # Lê o CSV da turma
            arquivo_escolhido = os.path.join(pasta_boletins, arquivo)
            df = pd.read_csv(arquivo_escolhido)
            df.columns = [col.strip() for col in df.columns]
            if "Nota Final" in df.columns:
                df["Nota Final"] = pd.to_numeric(df["Nota Final"], errors="coerce").fillna(0)
            else:
                st.error(f"Coluna 'Nota Final' não encontrada no arquivo CSV para {turma}.")

            # Tabela pivot
            pivot = df.pivot_table(index="Nome", columns="Disciplina", values="Nota Final", aggfunc="first").fillna(0)
            disciplinas_zeradas = pivot.loc[:, (pivot == 0).all()].columns.tolist()
            disciplinas_para_analisar = pivot.drop(columns=disciplinas_zeradas)

            pivot['Disciplinas abaixo da média'] = (disciplinas_para_analisar < nota_corte).sum(axis=1)
            pivot['Média global'] = pivot.drop(columns=['Disciplinas abaixo da média']).mean(axis=1).round(2)
            pivot_sorted = pivot.sort_values(by=["Disciplinas abaixo da média", "Média global"], ascending=[False, True])

            # Gera o arquivo Excel
            excel_file = gerar_excel(pivot_sorted, nota_corte, disciplinas_zeradas)
            excel_name = f"{arquivo.replace('.csv','')}_completo.xlsx"
            zip_file.writestr(excel_name, excel_file.getvalue())

            # Gera o PDF
            pdf_bytes = gerar_pdf(pivot_sorted, turma, nota_corte, disciplinas_zeradas)
            pdf_name = f"{arquivo.replace('.csv','')}.pdf"
            zip_file.writestr(pdf_name, pdf_bytes.getvalue())

    # Retorna o arquivo ZIP
    zip_buffer.seek(0)
    return zip_buffer





# Lê o arquivo CSV da turma escolhida
arquivo_escolhido = os.path.join(pasta_boletins, arquivos_disponiveis[turma_escolhida])
df = pd.read_csv(arquivo_escolhido)
df.columns = [col.strip() for col in df.columns]

if "Nota Final" in df.columns:
    df["Nota Final"] = pd.to_numeric(df["Nota Final"], errors="coerce").fillna(0)
else:
    st.error("Coluna 'Nota Final' não encontrada no arquivo CSV.")

# Tabela pivot
pivot = df.pivot_table(index="Nome", columns="Disciplina", values="Nota Final", aggfunc="first").fillna(0)
disciplinas_zeradas = pivot.loc[:, (pivot == 0).all()].columns.tolist()
disciplinas_para_analisar = pivot.drop(columns=disciplinas_zeradas)

pivot['Disciplinas abaixo da média'] = (disciplinas_para_analisar < nota_corte).sum(axis=1)
pivot['Média global'] = pivot.drop(columns=['Disciplinas abaixo da média']).mean(axis=1).round(2)
pivot_sorted = pivot.sort_values(by=["Disciplinas abaixo da média", "Média global"], ascending=[False, True])

# Gerar PDF com xhtml2pdf
def gerar_pdf(df, titulo, nota_corte, disciplinas_zeradas):
    html = gerar_html_tabela(df, titulo, nota_corte, disciplinas_zeradas)
    pdf_file = BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=pdf_file)
    pdf_file.seek(0)
    return pdf_file


def highlight_cells(val, col_name, col_list):
    try:
        val = float(val)
        if col_name == col_list[-2]:
            return 'background-color: white; color: black'
        elif col_name in disciplinas_zeradas:
            return 'background-color: #fff3cd; color: #856404'
        elif val < nota_corte:
            return 'background-color: #f8d7da; color: red'
        else:
            return 'background-color: #d4edda; color: green'
    except:
        return ''

def formatar_notas(val):
    try:
        return f"{float(val):.2f}"
    except:
        return val

def abreviar_disciplinas(df_final, num_letras):
    new_columns = []
    for col in df_final.columns:
        abbreviated = ' '.join([word[:num_letras] for word in col.split()])
        new_columns.append(abbreviated)
    df_final.columns = new_columns
    return df_final

pivot_abreviado = abreviar_disciplinas(pivot_sorted.copy(), num_letras)
disciplinas_zeradas_abreviadas = pivot_abreviado.loc[:, (pivot_abreviado == 0).all()].columns.tolist()

pivot_sorted_fmt = pivot_sorted.round(2).applymap(formatar_notas)

def aplicar_negrito(df):
    return df.style.applymap(lambda x: 'font-weight: bold', subset=pd.IndexSlice[:, :])

st.subheader(f"📋 {turma_escolhida}")
colunas_originais = list(pivot_sorted.columns)
st.dataframe(
    aplicar_negrito(pivot_sorted_fmt).apply(
        lambda col: col.apply(lambda val: highlight_cells(val, col.name, colunas_originais)), axis=0
    ),
    use_container_width=True
)

pivot_abreviado_fmt = pivot_abreviado.applymap(formatar_notas)
colunas_abreviadas = list(pivot_abreviado.columns)

def highlight_cells_abreviado(val, col_name, col_list):
    try:
        val = float(val)
        if col_name == col_list[-2]:
            return 'background-color: white; color: black'
        elif col_name in disciplinas_zeradas_abreviadas:
            return 'background-color: #fff3cd; color: #856404'
        elif val < nota_corte:
            return 'background-color: #f8d7da; color: red'
        else:
            return 'background-color: #d4edda; color: green'
    except:
        return ''

st.subheader(f"📋 Disciplinas abreviadas ({num_letras} letras)")
st.dataframe(
    aplicar_negrito(pivot_abreviado_fmt).apply(
        lambda col: col.apply(lambda val: highlight_cells_abreviado(val, col.name, colunas_abreviadas)), axis=0
    ),
    use_container_width=True
)

excel_completo = gerar_excel(pivot_sorted, nota_corte, disciplinas_zeradas)
excel_abreviado = gerar_excel(pivot_abreviado, nota_corte, disciplinas_zeradas_abreviadas)

st.download_button(
    label="📥 Baixar Excel completo",
    data=excel_completo,
    file_name=f"{arquivos_disponiveis[turma_escolhida].replace('.csv','')}_completo.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Função para gerar HTML
def gerar_html_tabela(df, titulo, nota_corte, disciplinas_zeradas):
    html = f"""
    <html>
    <head>
        <style>
            @page {{
                size: A4 landscape;
                margin: 2mm;
            }}
            body {{
                font-family: Arial, sans-serif;
                font-size: 6px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                border: 1px solid #000;
                padding: 1px;
                text-align: center;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            h2 {{
                text-align: center;
            }}
            .abaixo-da-media {{ background-color: #f8d7da; color: red; }}
            .acima-da-media {{ background-color: #d4edda; color: green; }}
            .disciplina-zerada {{ background-color: #fff3cd; color: #856404; }}
            .disciplina-neutra {{ background-color: #ffffff; color: black; }}
        </style>
    </head>
    <body>
        <h2>{titulo}</h2>
        <table>
            <thead>
                <tr>
                    <th>Nome</th>
                    {"".join(f"<th>{col}</th>" for col in df.columns)}
                </tr>
            </thead>
            <tbody>
    """

    for index, row in df.iterrows():
        html += f"<tr><td>{index}</td>"
        for col_name, value in row.items():
            classe = "disciplina-neutra"
            if col_name in disciplinas_zeradas:
                classe = "disciplina-zerada"
            elif col_name != 'Disciplinas abaixo da média' and isinstance(value, (int, float)):
                classe = "abaixo-da-media" if value < nota_corte else "acima-da-media"
            html += f'<td class="{classe}">{value}</td>'
        html += "</tr>"

    html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    return html

st.sidebar.download_button(
    label="📂 Baixar todos os arquivos",
    data=gerar_zip_de_todas_as_turmas(),
    file_name="boletins_conselho_de_classe.zip",
    mime="application/zip"
)
# Download do PDF
pdf_bytes = gerar_pdf(pivot_sorted, turma_escolhida, nota_corte, disciplinas_zeradas)
st.download_button(
    label="📄 Baixar PDF",
    data=pdf_bytes,
    file_name=f"{arquivos_disponiveis[turma_escolhida].replace('.csv','')}.pdf",
    mime="application/pdf"
)
