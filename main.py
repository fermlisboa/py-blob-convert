from pathlib import Path
from PIL import Image
from fpdf import FPDF
from docx import Document
import pandas as pd
import base64
import os
import mysql.connector
import uuid
import io

def get_file_extension(file_name):
    return file_name.split('.')[-1]

class CustomPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        pass

def execute_query(query, fetch_results=True):
    # Conectar ao banco de dados
    connection = mysql.connector.connect(
        host='10.0.0.32',
        user='root',
        password='53nh@.15',
        database='otimizar_clear_spi'
    )

    try:
        # Criar um cursor para a conexão com o banco de dados
        cursor = connection.cursor()

        # Executar a consulta
        cursor.execute(query)

        if fetch_results:
            # Obter os nomes das colunas do cursor
            column_names = cursor.column_names

            # Obter os resultados da consulta
            results = cursor.fetchall()

            return column_names, results

    except Exception as e:
        # Tratar exceções e imprimir o erro
        print(f"Ocorreu um erro na execução da consulta: {str(e)}")

    finally:
        # Fechar a conexão com o banco de dados
        connection.close()

# Caminho do diretório de arquivos
file_path = Path(os.path.abspath('upload/'))
file_path = file_path.as_posix()

# Criar o diretório se ele não existir
if not os.path.exists(file_path):
    os.makedirs(file_path)

# Consulta SQL
query = "SELECT * FROM arquivo_upload"

# Executar a consulta e obter os nomes das colunas e resultados
column_names, result1 = execute_query(query)

# Mostrar os resultados
for res in result1:
    # Converter a tupla em um dicionário
    res_dict = dict(zip(column_names, res))

    # Acessar os valores pelo nome da coluna
    if 'arquivo_upload_nome' in res_dict:
        arquivo_upload_nome = res_dict['arquivo_upload_nome']
        arquivo_nome = arquivo_upload_nome.replace(" ", "")
    else:
        arquivo_upload_nome = str(uuid.uuid4())
    arquivo_upload_id = res_dict['arquivo_upload_id']
    arquivo_upload_extensao = res_dict['arquivo_upload_extensao']

    query2 = f"SELECT arquivo_upload_binario FROM arquivo_upload WHERE arquivo_upload_id = {arquivo_upload_id}"
    column_names, result2 = execute_query(query2)

    if result2:
        binary_data = result2[0][0]

        # Converter binário para base64
        base64_data = base64.b64encode(binary_data).decode('utf-8')

        file_extension = arquivo_upload_extensao

        output_file = f'{file_path}/{arquivo_nome}.{file_extension}'

        # Criar DataFrame a partir dos dados binários
        if file_extension == 'html':
            df = pd.DataFrame({'arquivo_html': [f'<iframe src="data:text/html;base64,{base64_data}"></iframe>']})
            df.to_html(output_file, index=False)
        elif file_extension == 'doc':
            doc = Document(binary_data)

            doc.save(output_file)
        elif file_extension == 'png':
            image = Image.open(io.BytesIO(binary_data))

            image.save(output_file)
        elif file_extension == 'jpg' or file_extension == 'jpeg':
            image = Image.open(io.BytesIO(binary_data))

            image.save(output_file)
        elif file_extension == 'pdf':
            pdf = CustomPDF()

            pdf.add_page()

            pdf.set_font('Arial', size=12)

            text = binary_data.decode('utf-8')

            pdf.cell(0, 10, text)

            pdf.output(output_file)
        elif file_extension == 'ttf':
            with open(output_file, 'wb') as file:
                file.write(binary_data)
        else:
            print(file_extension)
            raise ValueError('Formato de arquivo não suportado.')

        new_output_file = f'{file_path}/{arquivo_nome}.{file_extension}'
        os.rename(output_file, new_output_file)