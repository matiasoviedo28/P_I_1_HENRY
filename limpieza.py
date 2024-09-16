#SCRIPT PARA LIMIAR LOS DATOS DEL DATASET, CONVIRTIENDO TIPOS DE DATOS, MANEJANDO ERRORES Y ELIMINANDO COLUMNAS NO UTILIZADAS
import pandas as pd
import ast

df_movies = pd.read_csv('movies_dataset.csv') 
df_credits = pd.read_csv('credits.csv')

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

#save
df_movies.to_parquet("movies_dataset.parquet", index=False)
df_credits.to_parquet("credits.parquet", index=False)