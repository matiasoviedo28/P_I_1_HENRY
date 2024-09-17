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

#cargar datos, filtrados y limpios (limpieza.py)
try:
    movies_metadata = pd.read_parquet("datasets/movies_dataset.parquet")
    credits = pd.read_parquet("datasets/credits.parquet")

except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
    raise RuntimeError(f"Error al cargar los archivos CSV: {e}")

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
    titulo = titulo.lower()
    filtered_movies = movies_metadata[movies_metadata['title'].str.lower().str.contains(titulo.lower(), na=False)]
    if filtered_movies.empty:
        return {"error": "Película no encontrada"}
    recommended_movies = filtered_movies['title'].tolist()
    return {"recommendations": recommended_movies}

#CANTIDAD DE FILMACIONES POR MES
@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
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
    nombre_actor = nombre_actor.lower()
    try:
        actor_movies = credits[credits['cast'].str.contains(nombre_actor, na=False)]
        if actor_movies.empty:
            return {"error": "Actor no encontrado"}
        total_ret = 0
        for index, row in actor_movies.iterrows():
            movie = movies_metadata[movies_metadata['id'] == row['id']]
            total_ret += movie['revenue'].sum() / (movie['budget'].sum() + 1e-9)
        promedio_ret = total_ret / actor_movies.shape[0]
        return {"actor": nombre_actor, "cantidad_peliculas": actor_movies.shape[0], "retorno_total": total_ret, "promedio_retorno": promedio_ret}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


@app.get("/get_director/{nombre_director}", response_model=DirectorResponse)
def get_director(nombre_director: str):
    nombre_director = nombre_director.lower()
    director_movies = credits[credits['crew'].str.contains(nombre_director, na=False, case=False)]
    if director_movies.empty:
        return {"error": "Director no encontrado"}
    total_ret = 0
    peliculas = []
    for _, row in director_movies.iterrows():
        movie = movies_metadata[movies_metadata['id'] == row['id']].copy()
        if movie.empty:
            continue
        movie['revenue'] = pd.to_numeric(movie['revenue'], errors='coerce').fillna(0)
        movie['budget'] = pd.to_numeric(movie['budget'], errors='coerce').fillna(0)
        budget = movie['budget'].sum()
        revenue = movie['revenue'].sum()
        retorno_individual = revenue / budget if budget > 0 else 0
        total_ret += retorno_individual
        peliculas.append(MovieDetail(
            titulo=movie['title'].values[0],
            fecha_lanzamiento=movie['release_date'].values[0] if 'release_date' in movie else None,
            retorno_individual=retorno_individual,
            costo=budget,
            ganancia=revenue
        ))
    return DirectorResponse(director=nombre_director, peliculas=peliculas, retorno_total=total_ret)

#TOP POPULARIDAD
@app.get("/popular_movies/{top_n}", response_model=PopularMoviesResponse)
def popular_movies(top_n: int):
    top_movies = movies_metadata[['title', 'popularity']].sort_values(by='popularity', ascending=False).head(top_n)
    return {"top_n": top_n, "peliculas": top_movies['title'].tolist()}

#VER POR LENGUAJE
@app.get("/movies_by_language/{idioma}", response_model=MoviesByLanguageResponse) 
def movies_by_language(idioma: str):
    movies_by_language = movies_metadata[movies_metadata['original_language'].str.lower() == idioma.lower()]
    return {"idioma": idioma, "peliculas": movies_by_language['title'].tolist()}

#PELICULAS POR PALABRAS CLAVE EN REVIEW
@app.get("/movies_by_review/{review}", response_model=MoviesByReviewResponse) 
def movies_by_review(review: str):
    movies_by_review = movies_metadata[movies_metadata['overview'].str.contains(review, case=False, na=False)]
    return {"review": review, "peliculas": movies_by_review['title'].tolist()}

#PELICULAS POR GENERO
@app.get("/movies_by_genre/{genero}", response_model=MovieByGenreResponse)
def movies_by_genre(genero: str):
    movies_by_genre = movies_metadata[movies_metadata['genres_list'].apply(lambda x: genero.lower() in [g.lower() for g in x])]
    return {"genero": genero, "peliculas": movies_by_genre['title'].tolist()}

#VALORACIONES
@app.get("/votos_titulo/{titulo}") 
def votos_titulo(titulo: str):
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
