#importar librerias
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import ast
from typing import List, Optional

app = FastAPI()

#modelos para estructurar las respuestas de las rutas
class MovieDetail(BaseModel):
    titulo: str
    fecha_lanzamiento: Optional[str]
    retorno_individual: Optional[float]
    costo: Optional[float]
    ganancia: Optional[float]

class DirectorResponse(BaseModel):
    director: str
    peliculas: List[MovieDetail]
    retorno_total: float

class PopularMoviesResponse(BaseModel):
    top_n: int
    peliculas: List[str]

class MoviesByLanguageResponse(BaseModel):
    idioma: str
    peliculas: List[str]

class MoviesByReviewResponse(BaseModel):
    review: str
    peliculas: List[str]

class RecommendationResponse(BaseModel):
    recommendations: list

class MovieByGenreResponse(BaseModel):
    genero: str
    peliculas: List[str]

class ActorRequest(BaseModel):
    nombre_actor: str

#cargar datos, filtrados y limpios (limpieza.py)
try:
    movies_metadata = pd.read_parquet("datasets/movies_dataset.parquet")
    credits = pd.read_parquet("datasets/credits.parquet")

except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
    raise RuntimeError(f"Error al cargar los archivos parquet: {e}")

#procesar datos
def extract_genres(genre_field):
    try:
        genres = ast.literal_eval(genre_field)
        return [genre['name'] for genre in genres]
    except (ValueError, SyntaxError, TypeError):
        return []

movies_metadata['genres_list'] = movies_metadata['genres'].apply(extract_genres)

#SISTEMA DE RECOMENDACION
@app.get("/recomendacion/{titulo}", response_model=RecommendationResponse)
def recommend(titulo: str):
    '''Se introduce el un valor como un nombre de pelicula para relacionarlo y recomendar similares'''
    titulo = titulo.lower()
    filtered_movies = movies_metadata[movies_metadata['title'].str.lower().str.contains(titulo.lower(), na=False)]
    if filtered_movies.empty:
        return {"error": "Película no encontrada"}
    recommended_movies = filtered_movies['title'].head(5).tolist()
    return {"recommendations": recommended_movies}

#CANTIDAD DE FILMACIONES POR MES
@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    '''Se introduce un mes en español'''
    meses = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
             "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12}
    mes_num = meses.get(mes.lower())
    if mes_num is None:
        return {"error": "Mes no válido"}
    movies_metadata['release_date'] = pd.to_datetime(movies_metadata['release_date'], errors='coerce')
    count = movies_metadata[movies_metadata['release_date'].dt.month == mes_num].shape[0]
    return {"cantidad": count}

#CANTIDAD DE FILMACIONES POR DIA
@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    '''Se introduce un día de la semana en español'''
    dias = {"lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3, "viernes": 4, "sábado": 5, "domingo": 6}
    dia_num = dias.get(dia.lower())
    if dia_num is None:
        return {"error": "Día no válido"}
    movies_metadata['release_date'] = pd.to_datetime(movies_metadata['release_date'], errors='coerce')
    count = movies_metadata[movies_metadata['release_date'].dt.weekday == dia_num].shape[0]
    return {"cantidad": count}

#VER TITULOS
@app.get("/score_titulo/{titulo}")
def score_titulo(titulo: str):
    '''Se introduce el nombre de una pelicula y retorna su año de estreno y su score'''
    try:
        # Verificar si las columnas existen
        if 'title' not in movies_metadata.columns or 'popularity' not in movies_metadata.columns or 'release_year' not in movies_metadata.columns:
            return {"error": "Datos faltantes en el dataset"}
        
        # Filtrar la película
        movie = movies_metadata[movies_metadata['title'].str.lower() == titulo.lower()]
        
        if movie.empty:
            return {"error": "Película no encontrada"}
        
        score = float(movie['popularity'].values[0])  
        year = int(movie['release_year'].values[0])  
        
        return {"titulo": titulo, "año": year, "score": score}
    
    except KeyError as e:
        return {"error": f"Columna faltante en el dataset: {e}"}
    except Exception as e:
        return {"error": f"Ha ocurrido un error: {str(e)}"}

#VER ACTOR
@app.get("/get_actor/{nombre_actor}")
def get_actor(nombre_actor: str):
    '''Se introduce el nombre de un actor y retorna la cantidad de peliculas y retorno total y promedio'''
    nombre_actor = nombre_actor.lower()
    
    #filtrar
    actor_movies = credits[credits['cast'].apply(
        lambda cast_list: any(nombre_actor in actor['name'].lower() for actor in cast_list)
    )]
    
    if actor_movies.empty:
        return {"error": "Actor no encontrado"}

    #crear una lista de actores
    actores_encontrados = {}
    for _, row in actor_movies.iterrows():
        for actor in row['cast']:
            nombre = actor['name'].lower()
            if nombre_actor in nombre:
                if nombre not in actores_encontrados:
                    actores_encontrados[nombre] = {
                        "cantidad_peliculas": 0,
                        "retorno_total": 0
                    }
                actores_encontrados[nombre]["cantidad_peliculas"] += 1
                movie = movies_metadata[movies_metadata['id'] == row['id']]
                if not movie.empty:
                    actores_encontrados[nombre]["retorno_total"] += movie['revenue'].sum() / (movie['budget'].sum() + 1e-9)
    
    #ordenar los actores por la cantidad de pelis
    actor_relevante = max(actores_encontrados, key=lambda x: actores_encontrados[x]["cantidad_peliculas"])

    #calcular el promedio de retorno
    retorno_total = actores_encontrados[actor_relevante]["retorno_total"]
    cantidad_peliculas = actores_encontrados[actor_relevante]["cantidad_peliculas"]
    promedio_retorno = retorno_total / cantidad_peliculas if cantidad_peliculas > 0 else 0

    return {
        "Actor/Actriz": actor_relevante.title(),
        "Cantidad de películas": cantidad_peliculas,
        "Retorno Total": retorno_total,
        "Retorno Promedio": promedio_retorno
    }


#VER DIRECTOR
@app.get("/director/{nombre_director}")
def get_director(nombre_director: str):
    '''Se introduce un director y retorna sus peliculas con sus numeros'''
    nombre_director = nombre_director.lower()

    # Filtrar el dataframe credits para encontrar directores
    director_credits = credits[credits['crew'].apply(
        lambda crew: any(
            crew_member['job'] == 'Director' and crew_member['name'].lower() == nombre_director
            for crew_member in crew
        )
    )]

    if director_credits.empty:
        return {"Director": nombre_director, "Retorno Total": 0, "Películas": []}

    # Obtener la lista de IDs de películas en las que el director ha trabajado
    movie_ids = director_credits['id'].tolist()

    # Filtrar las películas del dataframe movies_metadata
    director_movies = movies_metadata[movies_metadata['id'].astype(str).isin(map(str, movie_ids))]

    # Calcular el retorno total y obtener detalles de las películas
    total_retorno = 0
    peliculas = []

    for _, row in director_movies.iterrows():
        movie_id = row['id']
        title = row['title']
        release_date = row['release_date']
        retorno = row['return']
        budget = row['budget']
        revenue = row['revenue']

        if budget > 0:
            total_retorno += retorno

        peliculas.append({
            "Título": title,
            "Fecha de Lanzamiento": release_date,
            "Retorno Individual": retorno,
            "Costo": budget,
            "Ganancia": revenue
        })

    return {
        "Director": nombre_director,
        "Retorno Total": total_retorno,
        "Películas": peliculas
    }

#TOP POPULARIDAD
@app.get("/popular_movies/{top_n}", response_model=PopularMoviesResponse)
def popular_movies(top_n: int):
    '''Se introduce un numero y retorna el una lista con el top peliculas'''
    top_movies = movies_metadata[['title', 'popularity']].sort_values(by='popularity', ascending=False).head(top_n)
    return {"top_n": top_n, "peliculas": top_movies['title'].tolist()}

#VER POR LENGUAJE
@app.get("/movies_by_language/{idioma}", response_model=MoviesByLanguageResponse) 
def movies_by_language(idioma: str):
    '''Se introduce un lenguaje y retorna la cantidad de peliculas'''
    movies_by_language = movies_metadata[movies_metadata['original_language'].str.lower() == idioma.lower()]
    return {"idioma": idioma, "peliculas": movies_by_language['title'].tolist()}

#PELICULAS POR PALABRAS CLAVE EN REVIEW
@app.get("/movies_by_review/{review}", response_model=MoviesByReviewResponse) 
def movies_by_review(review: str):
    '''Cantidad de peliculas por palabra clave de review'''
    movies_by_review = movies_metadata[movies_metadata['overview'].str.contains(review, case=False, na=False)]
    return {"review": review, "peliculas": movies_by_review['title'].tolist()}

#PELICULAS POR GENERO
@app.get("/movies_by_genre/{genero}", response_model=MovieByGenreResponse)
def movies_by_genre(genero: str):
    '''Cantidad de peliculas por genero'''
    movies_by_genre = movies_metadata[movies_metadata['genres_list'].apply(lambda x: genero.lower() in [g.lower() for g in x])]
    return {"genero": genero, "peliculas": movies_by_genre['title'].tolist()}

#VALORACIONES
@app.get("/votos_titulo/{titulo}") 
def votos_titulo(titulo: str):
    '''se introduce un titulo y retorna sus valoraciones'''
    try:
        movie = movies_metadata[movies_metadata['title'].str.lower() == titulo.lower()]
        if movie.empty:
            return {"error": "Película no encontrada"}
        if movie['vote_count'].values[0] < 2000:
            return {"error": "La película no tiene suficientes valoraciones"}
        votes = movie['vote_count'].values[0]
        average_vote = movie['vote_average'].values[0]
        return {"titulo": titulo, "cantidad_votos": votes, "promedio_votacion": average_vote}
    except KeyError as e:
        return {"error": f"Missing column in dataset: {e}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
