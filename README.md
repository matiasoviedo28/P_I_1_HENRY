# Machine Learning Operations
## Proyecto individual N°1 de Data Science, Soy Henry

## Sistema de Recomendaciones de Películas 🎬
### Descripción del Proyecto
Este proyecto consiste en la creación de una API MVP para un sistema de recomendación de películas. En este README, se detalla el proceso completo, desde la obtención y preparación de los datos crudos hasta la implementación y consultas a la API desplegada en Render.
___

### Estructura del Proyecto ⚙️
* ETL (Extract, Transform, Load): Proceso de extracción y limpieza de datos a partir de varios datasets de películas.
* EDA (Exploratory Data Analysis): Análisis estadístico y visualización de los datos para entender las características más relevantes.
* API (FastAPI): Interfaz REST que expone los endpoints para obtener recomendaciones de películas y otros datos sobre las mismas.
* Despliegue en Render.com: El sistema está desplegado en la nube para que otros puedan acceder fácilment

___

### Estructura de Archivos⚙️
```python
P_I_1_HENRY/
│
├── main.py                 #archivo principal que corre FastAPI
├── ETL.py                  #script que ejecuta el ETL
├── EDA.ipynb               #notebook con el análisis exploratorio de datos
├── requirements.txt        #dependencias del proyecto
├── README.md               #este archivo
├── datasets/               #directorio con los archivos de entrada (datasets)
├── images/                 #directorio con imagenes para el readme
└── Graficos/               #directorio donde se exportarán graficos del EDA
```

___

### Requisitos del Sistema ⚙️
* Python 3.12.0
* Dependencias de Python que se instalan a través de requirements.txt
* Conexión a internet para acceder a la API en Render.com

___

### Limpieza 🧹​
* La limpieza se realiza mediante un proceso ETL (Extracción, Transformación y Carga), limpia y optimiza un conjunto de datos. El flujo incluye la corrección de valores nulos, el análisis y eliminación de duplicados, el ajuste de formatos incorrectos, y la eliminación de datos irrelevantes. Finalmente, los archivos originales en formato CSV se convierten a Parquet, logrando reducir significativamente el tamaño del dataset, de 230 MB a 30 MB.

![dataset](/images/dataset.png)
___
### Endpoints 💬​
![endpoints](/images/endpoints.png)
Ejemplo de uso de la API:

* GET /recomendacion: Al ingresar un nombre etorna una lista de 5 recomendaciones de películas basada en los datos procesados.

* GET /cantidad_filmaciones_mes: Se ingresa un mes en idioma Español. Debe devolver la cantidad de películas que fueron estrenadas en el mes consultado en la totalidad del dataset.

* GET /cantidad_filmaciones_dia: Se ingresa un día en idioma Español. Debe devolver la cantidad de películas que fueron estrenadas en día consultado en la totalidad del dataset.

* GET /score_titulo: Se ingresa el título de una filmación esperando como respuesta el título, el año de estreno y el score.

* GET /get_actor: Se ingresa el nombre de un actor que se encuentre dentro de un dataset debiendo devolver el éxito del mismo medido a través del retorno. Además, la cantidad de películas que en las que ha participado y el promedio de retorno. La definición no deberá considerar directores.

* GET /get_director: Se ingresa el nombre de un director que se encuentre dentro de un dataset debiendo devolver el éxito del mismo medido a través del retorno. Además, deberá devolver el nombre de cada película con la fecha de lanzamiento, retorno individual, costo y ganancia de la misma.

* GET/popular_movies: Se ingresa un numero para obtener el top de peliculas en el dataset, al combinarlo con otras funciones se puede usar como un filtro.

* GET/movies_by_lenguaje: Se ingresa un idioma por nombre o siglas y retorna las peliculas con esa caracteristica.

* GET/movies_by_review: Se ingresa una palabra o texto y la funcion retorna cuantas peliculas inclluyen el valor en su review.

* GET/movies_by_genero: Se ingresa una categoría tipo genero y retorna las peliculas con esa caracteristica.

* GET /votos_titulo: Se ingresa el título de una filmación esperando como respuesta el título, la cantidad de votos y el valor promedio de las votaciones. La misma variable deberá de contar con al menos 2000 valoraciones, caso contrario, debemos contar con un mensaje avisando que no cumple esta condición y que por ende, no se devuelve ningun valor.

___

### Exploración de Datos (EDA) 🔍​
Se realizó un análisis exploratorio de los datos con el objetivo de comprender mejor la distribución y características principales del dataset. Algunos de los análisis realizados incluyen:

* Cantidad de extrenos por año
* Duración de peliculas
* Extrenos por mes
* Extrenos por día
* Nube de palabras en reviews
* Peliculas por idioma
* Popularidad por año
* Presupuesto contra ingresos
* Puntuaciones
* Top recaudaciones

Los gráficos y análisis generados durante el EDA están disponibles en el archivo EDA.ipynb

### Despliegue en Render.com ⚙️

* La API está disponible en [Render](https://p-i-1-henry.onrender.com/docs), vinculada al repositorio en [GITHUB](https://github.com/matiasoviedo28/P_I_1_HENRY)

![fastapi](/images/fastapi.png)


___
### Instalación y Configuración ⚙️

* Clona el repositorio:
```bash
git clone https://github.com/matiasoviedo28/P_I_1_HENRY.git
cd P_I_1_HENRY #posicionarse en la carpeta clonada
```

* Instalar requerimientos:
```bash
pip install -r requirements.txt #instalar versiones de librerías funcionales
```

* Ejecución de la API web
    La API está disponible en [Render](https://p-i-1-henry.onrender.com/docs)

    Una vez está abierta la API, ya se pueden ejecutar las consultas desde los distintos endpoints

* Para ejecutar la API localmente:
```python 
#hay que estar posicionado con cd en P_I_1_HENRY
uvicorn main:app --reload #por defecto se usa el puerto 8000
```
    Luego en el navegador abrir este enlace:
    http://127.0.0.1:8000/docs 
[Link para local. ](http://127.0.0.1:8000/docs)
    Desde ahí puedes probar los diferentes endpoints en local

___

### Proyecto realizado por Matias Oviedo
