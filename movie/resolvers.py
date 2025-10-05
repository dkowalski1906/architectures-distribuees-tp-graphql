import json
from graphql import GraphQLError
import requests

USER_URL  = "http://localhost:3201" # microservice User

with open('{}/databases/movies.json'.format("."), "r") as jsf:
    movies = json.load(jsf)["movies"]
    
def write(movies_data):
    with open('{}/databases/movies.json'.format("."), 'w') as f:
        full = {}
        full['movies'] = movies_data
        json.dump(full, f)

def movies_json(_,info):
        return movies

def movie_with_id(_, info, id):
    for movie in movies:
        if movie["id"] == id:
            return movie
    raise GraphQLError("Movie not found with id: " + id)


def movie_with_title(_,info,title):
    for movie in movies:
        if str(movie["title"]) == title:
            return movie
    raise GraphQLError("Movie not found with title : " + title)

def add_movie(_, info, id, title, rating, director):
    for movie in movies:
        if str(movie["id"]) == id:
            raise GraphQLError("Movie ID already exists : " + id)
    newmovie = {
        "id": id,
        "title" : title,
        "rating" : rating,
        "director" : director
    }
    movies.append(newmovie)
    write(movies)
    return newmovie

def update_movie_rate(_,info,id,rating):
    newmovie = None
    for movie in movies:
        if movie['id'] == id:
            movie['rating'] = rating
            newmovie = movie
        
    if newmovie is None:
        raise GraphQLError("Movie not found with id: " + id)
    
    write(movies)
    return newmovie

def remove_movie_with_id(_, info, id):
    removed_movie = None
        
    for movie in movies:
        if str(movie["id"]) == id:
            movies.remove(movie)
            removed_movie = movie
        
    if removed_movie is None:
        raise GraphQLError("Movie not found with id: " + id)

    write(movies)
    return movie