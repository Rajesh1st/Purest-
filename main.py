from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# Primary source (try IMDbPY)
try:
    from imdb import IMDb
    ia_primary = IMDb()
except:
    ia_primary = None

# Backup source (Cinemagoer)
try:
    from cinemagoer import Cinemagoer
    ia_backup = Cinemagoer()
except:
    ia_backup = None


app = FastAPI(title="Hybrid IMDb Movie API (IMDbPY + Cinemagoer)")


class MovieInfo(BaseModel):
    TITLE: str
    YEAR: Optional[int]
    RATING: Optional[float]
    DURATION: Optional[str]
    GENRE: List[str]
    LANGUAGE: List[str]
    ACTORS: List[str]
    STORY_LINE: Optional[str]
    POSTER: Optional[str]
    IMDB_ID: Optional[str]


def extract_data(movie, fallback_query):
    """Extract clean movie metadata."""
    title = movie.get("title", fallback_query)
    year = movie.get("year")
    rating = movie.get("rating")

    runtime_list = movie.get("runtimes", [])
    duration = runtime_list[0] + " min" if runtime_list else None

    genres = movie.get("genres", [])
    langs = movie.get("languages", [])

    cast = movie.get("cast", [])
    actors = [str(a) for a in cast[:10]]

    plot_list = movie.get("plot", [])
    storyline = plot_list[0].split("::")[0] if plot_list else None

    poster = movie.get("cover url")
    imdb_id = "tt" + movie.movieID if hasattr(movie, "movieID") else None

    return MovieInfo(
        TITLE=title,
        YEAR=year,
        RATING=rating,
        DURATION=duration,
        GENRE=genres,
        LANGUAGE=langs,
        ACTORS=actors,
        STORY_LINE=storyline,
        POSTER=poster,
        IMDB_ID=imdb_id
    )


@app.get("/movie", response_model=MovieInfo)
def search_movie(q: str = Query(..., description="Movie name")):

    # -------------------------------------------
    # TRY 1: IMDbPY (Primary)
    # -------------------------------------------
    if ia_primary:
        try:
            results = ia_primary.search_movie(q)
            if results:
                movie = ia_primary.get_movie(results[0].movieID)
                return extract_data(movie, q)
        except:
            pass  # move to fallback

    # -------------------------------------------
    # TRY 2: Cinemagoer (Backup)
    # -------------------------------------------
    if ia_backup:
        try:
            results = ia_backup.search_movie(q)
            if results:
                movie_id = results[0].movieID
                movie = ia_backup.get_movie(movie_id)
                return extract_data(movie, q)
        except:
            pass

    raise HTTPException(status_code=404, detail="Movie not found via IMDbPY or Cinemagoer")
