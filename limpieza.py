#SCRIPT PARA LIMIAR LOS DATOS DEL DATASET, CONVIRTIENDO TIPOS DE DATOS, MANEJANDO ERRORES Y ELIMINANDO COLUMNAS NO UTILIZADAS
import pandas as pd
import ast
import os

#definir ubicaciones de los csv a limpiar
csv_movies = 'datasets/movies_dataset.csv'
csv_credits = 'datasets/credits.csv'

#verificar si los csv existen
if os.path.exists(csv_movies):
    df_movies = pd.read_csv(csv_movies)
else:
    print(f"El archivo {csv_movies} no existe. LIMPIEZA CANCELADA")
    exit()

if os.path.exists(csv_credits):
    df_credits = pd.read_csv(csv_credits)
else:
    print(f"El archivo {csv_credits} no existe. LIMPIEZA CANCELADA")
    exit()

#MOVIES_DATASET
#convertir columnas a tipos numericos
df_movies['budget'] = pd.to_numeric(df_movies['budget'], errors='coerce')
df_movies['popularity'] = pd.to_numeric(df_movies['popularity'], errors='coerce')
df_movies['revenue'] = pd.to_numeric(df_movies['revenue'], errors='coerce')
df_movies['runtime'] = pd.to_numeric(df_movies['runtime'], errors='coerce')

#manejar fechas
df_movies['release_date'] = pd.to_datetime(df_movies['release_date'], errors='coerce')

#rellenar nulos con 0
df_movies['budget'].fillna(0, inplace=True)
df_movies['popularity'].fillna(0, inplace=True)
df_movies['revenue'].fillna(0, inplace=True)
df_movies['runtime'].fillna(0, inplace=True)

#borrar filas con valores nulos
df_movies.dropna(subset=['release_date'], inplace=True)

#eliminar release_date y crear columna release_year
df_movies['release_date'] = df_movies['release_date'].dt.strftime('%Y-%m-%d')
df_movies['release_year'] = pd.to_datetime(df_movies['release_date']).dt.year

#hacer columna return como ratio de revenue sobre budget
df_movies['return'] = df_movies.apply(lambda row: row['revenue'] / row['budget'] if row['budget'] > 0 else 0, axis=1)

#borrar columnas que no se usarán
columns_to_drop = ['video', 'imdb_id', 'adult', 'original_title', 'poster_path', 'homepage']
df_movies.drop(columns=columns_to_drop, inplace=True)

#procesar columnas anidadas
def parse_nested_column(value):
    try:
        return ast.literal_eval(value) if pd.notnull(value) else []
    except (ValueError, SyntaxError):
        return []

#desanidar
list_columns = ['production_companies', 'production_countries', 'spoken_languages']
for column in list_columns:
    df_movies[column] = df_movies[column].apply(parse_nested_column)
print("df movies finalizado")


#CREDITS DATASET
#extraer el nombre y el personaje del elenco
def extract_cast(cast_str):
    try:
        cast_list = ast.literal_eval(cast_str)
        return [{'name': cast_member['name'], 'character': cast_member['character']} for cast_member in cast_list]
    except (ValueError, SyntaxError):
        return []

#extraer el nombre, trabajo y departamento
def extract_crew(crew_str):
    try:
        crew_list = ast.literal_eval(crew_str)
        return [{'name': crew_member['name'], 'job': crew_member['job'], 'department': crew_member['department']} for crew_member in crew_list]
    except (ValueError, SyntaxError):
        return []

#aplicar las funciones a las columnas
df_credits['cast'] = df_credits['cast'].apply(extract_cast)
df_credits['crew'] = df_credits['crew'].apply(extract_crew)
print("df credits finalizado")



#save
df_movies.to_parquet("datasets/movies_dataset.parquet", index=False)
df_credits.to_parquet("datasets/credits.parquet", index=False)
print("limpieza realizada")

#ELIMINAR ARCHIVOS ANTIGUIS
# Verificar si el archivo existe y eliminarlo
if os.path.exists(csv_movies):
    os.remove(csv_movies)
    print(f"Archivo {csv_movies} eliminado.")
else:
    print(f"El archivo {csv_movies} no existe.")
if os.path.exists(csv_credits):
    os.remove(csv_credits)
    print(f"Archivo {csv_credits} eliminado.")
else:
    print(f"El archivo {csv_credits} no existe.")
print("codigo finalizado")