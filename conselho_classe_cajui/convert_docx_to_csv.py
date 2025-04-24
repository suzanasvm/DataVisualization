import os
from docx import Document
import csv

# Pastas de entrada e saída
pasta_entrada = 'boletim_entrada'
pasta_saida = 'boletim_saida'

# Cria a pasta de saída se não existir
os.makedirs(pasta_saida, exist_ok=True)

# Lista todos os arquivos .docx da pasta de entrada
arquivos_docx = [f for f in os.listdir(pasta_entrada) if f.endswith('.docx')]

for arquivo in arquivos_docx:
    caminho_entrada = os.path.join(pasta_entrada, arquivo)
    doc = Document(caminho_entrada)
    tables = doc.tables

    # Validações
    if len(tables) < 2 or len(tables) % 2 != 0:
        print(f"⚠️ Arquivo '{arquivo}' ignorado: número inválido de tabelas.")
        continue

    # Lista final com os dados do boletim
    boletins_filtrados = []
    cabecalho = []

    for i in range(0, len(tables), 2):
        tabela_dados = tables[i]
        tabela_boletim = tables[i + 1]

        nome_aluno = "Desconhecido"
        matricula_aluno = "Desconhecida"
        dados_aluno = {}

        # Extração dos dados pessoais
        for row in tabela_dados.rows:
            cell_text = row.cells[0].text.strip()
            if ':' in cell_text:
                key, value = cell_text.split(':', 1)
                key = key.strip()
                value = value.strip()
                dados_aluno[key] = value
                if key.lower() == 'nome':
                    nome_aluno = value
                if key.lower() == 'matricula':
                    matricula_aluno = value
            elif len(row.cells) >= 2:
                key = row.cells[0].text.strip().replace(':', '')
                value = row.cells[1].text.strip()
                dados_aluno[key] = value
                if 'nome' in key.lower():
                    nome_aluno = value
                if 'matricula' in key.lower():
                    matricula_aluno = value

        # Extração do boletim com filtragem por Estado
        for j, row in enumerate(tabela_boletim.rows):
            linha = [cell.text.strip() for cell in row.cells]

            if j == 0:
                # Guarda o cabeçalho e encontra o índice da coluna "Estado"
                cabecalho = ['Nome', 'Matrícula'] + linha
                try:
                    idx_estado = linha.index('Estado')
                except ValueError:
                    print(f"❌ Campo 'Estado' não encontrado na tabela do arquivo '{arquivo}'.")
                    break
                continue  # Pula o cabeçalho

            if linha and len(linha) > idx_estado:
                estado = linha[idx_estado].upper()
                if estado == 'MATRICULADO':
                    boletins_filtrados.append([nome_aluno, matricula_aluno] + linha)

    # Salva CSV se houver dados válidos
    if boletins_filtrados:
        boletins_filtrados.insert(0, cabecalho)  # Adiciona o cabeçalho no topo
        nome_base = os.path.splitext(arquivo)[0]
        caminho_csv_boletim = os.path.join(pasta_saida, f'{nome_base}_boletim.csv')
        with open(caminho_csv_boletim, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(boletins_filtrados)
        print(f"✅ Arquivo '{arquivo}' processado e salvo como CSV em '{pasta_saida}'")
    else:
        print(f"⚠️ Nenhum aluno 'MATRICULADO' encontrado em '{arquivo}'")
