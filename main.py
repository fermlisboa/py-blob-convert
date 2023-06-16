import pandas as pd
import base64, os, mysql.connector

def get_file_extension(file_name):
    return file_name.split('.')[-1]

def execute_query(query):
    # Connect to database
    connection = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )

    try:
        # Create a cursos to database connection
        cursor = connection.cursor()

        # Execute query
        cursor.execute(query)

        # get the results
        results = cursor.fetchall()

        return results

    except Exception as e:
        # Exception for error
        print(f"Ocorreu um erro na execução da consulta: {str(e)}")

    finally:
        # Close database connection
        connection.close()

file_path = os.getenv('FILE_PATH')

# SQL Query
query = "SELECT * FROM arquivo_upload_binario"

# Execute the query
result1 = execute_query(query)

# Show the result
for res in result1:
    query2 = f"SELECT arquivo_upload_binario INTO DUMPFILE '{file_path}{res['arquivo_upload_nome']}.bin' FROM arquivo_upload WHERE arquivo_upload_id = {res['arquivo_upload_id']};"

    result2 = execute_query(query2)
    
    with open(f'{file_path}{res['arquivo_upload_nome']}.bin', 'rb') as file:
    binary_data = file.read()

    # bin to base64
    base64_data = base64.b64encode(binary_data).decode('utf-8')

    file_extension = get_file_extension(f'{file_path}{res['arquivo_upload_nome']}.bin')
    # OR
    # file_extension = result2['arquivo_upload_extensao']

    # Create dataframe from binary
    if file_extension == 'html':
        df = pd.DataFrame({'arquivo_html': [f'<iframe src="data:text/html;base64,{base64_data}"></iframe>']})
    elif file_extension == 'doc':
        df = pd.DataFrame({'arquivo_html': [f'<iframe src="data:application/msword;base64,{base64_data}"></iframe>']})
    elif file_extension == 'png':
        df = pd.DataFrame({'arquivo_html': [f'<img src="data:image/png;base64,{base64_data}">']})
    elif file_extension == 'jpg' or file_extension == 'jpeg':
        df = pd.DataFrame({'arquivo_html': [f'<img src="data:image/jpeg;base64,{base64_data}">']})
    elif file_extension == 'pdf':
        df = pd.DataFrame({'arquivo_html': [f'<embed src="data:application/pdf;base64,{base64_data}" type="application/pdf" width="100%" height="600px">']})
    else:
        raise ValueError('Formato de arquivo não suportado.')

    output_file = f'{file_path}{res['arquivo_upload_nome']}.{file_extension}'
    df.to_html(output_file, index=False)

    # .html to .file_extension
    new_output_file = f'{file_path}{res['arquivo_upload_nome']}.{file_extension}'
    os.rename(output_file, new_output_file)
