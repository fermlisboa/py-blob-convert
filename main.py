import pandas as pd
import base64, os, mysql.connector

def get_file_extension(file_name):
    return file_name.split('.')[-1]

def execute_query(query):
    # Connect to database
    connection = mysql.connector.connect(
        host='MYSQL_HOST',
        user='MYSQL_USER',
        password='MYSQL_PASSWORD',
        database='MYSQL_DATABASE'
    )

    try:
        # Create a cursos to database connection
        cursor = connection.cursor()

        # Execute query
        cursor.execute(query)

        # Get the column names from the cursor object
        column_names = cursor.column_names

        # get the results
        results = cursor.fetchall()

        return column_names, results

    except Exception as e:
        # Exception for error
        print(f"Ocorreu um erro na execução da consulta: {str(e)}")

    finally:
        # Close database connection
        connection.close()

file_path = 'FILE_PATH'
# Create directory if it doesn't exist
if not os.path.exists(file_path):
    os.makedirs(file_path)

# SQL Query
query = "SELECT * FROM arquivo_upload"

# Execute the query and get column names and results
column_names, result1 = execute_query(query)

# Show the result
for res in result1:
    # Convert the tuple to a dictionary
    res_dict = dict(zip(column_names, res))

    # Access the values by column name
    arquivo_upload_nome = res_dict['arquivo_upload_nome']
    arquivo_nome = arquivo_upload_nome.replace(" ", "")
    arquivo_upload_id = res_dict['arquivo_upload_id']


    query2 = f"SELECT arquivo_upload_binario INTO DUMPFILE '{file_path}/{arquivo_nome}.bin' FROM arquivo_upload WHERE arquivo_upload_id = {arquivo_upload_id};"

    result2 = execute_query(query2)

    print(result2)
    
    with open(f'{file_path}/{arquivo_nome}.bin', 'rb') as file:
        binary_data = file.read()

    # bin to base64
    base64_data = base64.b64encode(binary_data).decode('utf-8')

    file_extension = get_file_extension(f'{file_path}{arquivo_nome}.bin')
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

    output_file = f'{file_path}{arquivo_nome}.{file_extension}'
    df.to_html(output_file, index=False)

    # .html to .file_extension
    new_output_file = f'{file_path}{arquivo_nome}.{file_extension}'
    os.rename(output_file, new_output_file)
