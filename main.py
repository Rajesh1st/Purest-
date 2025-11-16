# main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from imdb import IMDb
from typing import List, Optional
import os

app = FastAPI(title="Simple IMDb Info API")

ia = IMDb()  # imdbpy instance (uses web scraping / imdb unofficial)

class MovieInfo(BaseModel):
    TITLE: str
    YEAR: Optional[int] = None
    RATING: Optional[float] = None
    DURATION: Optional[str] = None
    GENRE: List[str] = []
    LANGUAGE: List[str] = []
    ACTORS: List[str] = []
    STORY_LINE: Optional[str] = None
    POSTER: Optional[str] = None
    IMDB_ID: Optional[str] = None

def first_or_none(lst):
    return lst[0] if lst else None

@app.get("/movie", response_model=MovieInfo)
def get_movie(q: str = Query(..., min_length=1, description="Movie name to search")):
    """
    Search IMDb for a movie by name and return metadata (title, year, rating, runtime, genres, languages, actors, storyline, poster).
    """
    try:
        # Search movies (returns list of results)
        results = ia.search_movie(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IMDb search failed: {e}")

    if not results:
        raise HTTPException(status_code=404, detail="No movie found matching the query.")

    # Pick the top result
    top = results[0]
    movie_id = top.movieID

    try:
        # fetch detailed info
        movie = ia.get_movie(movie_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch movie details: {e}")

    # Title & Year
    title = movie.get('title') or top.get('title') or q
    year = movie.get('year')

    # Rating
    rating = movie.get('rating')

    # Duration/runtime
    runtimes = movie.get('runtimes') or movie.get('runtime') or []
    duration = None
    if isinstance(runtimes, list):
        duration = ":".join(runtimes) if runtimes else None
    elif isinstance(runtimes, str):
        duration = runtimes

    # Genres
    genres = movie.get('genres') or []

    # Languages
    languages = movie.get('languages') or []

    # Actors (top 10)
    cast = movie.get('cast') or []
    actors = [str(person) for person in cast[:10]]

    # Plot/storyline
    plot_list = movie.get('plot') or movie.get('plot outline') or []
    storyline = None
    if isinstance(plot_list, list) and plot_list:
        storyline = plot_list[0].split("::")[0].strip()
    elif isinstance(plot_list, str):
        storyline = plot_list

    # Poster URL
    poster = movie.get('cover url') or movie.get('full-size cover url') or movie.get('cover url')

    imdb_id = f"tt{movie_id}" if movie_id else None

    data = MovieInfo(
        TITLE=title,
        YEAR=year,
        RATING=rating,
        DURATION=duration,
        GENRE=genres,
        LANGUAGE=languages,
        ACTORS=actors,
        STORY_LINE=storyline,
        POSTER=poster,
        IMDB_ID=imdb_id
    )

    return data
