import json

def movies_json(_,info):
    with open('{}/databases/movies.json'.format("."), "r") as file:
        movies = json.load(file)["movies"]
        return movies

def movie_with_id(_, info, id):
    with open('./databases/movies.json') as file:
        movies = json.load(file)["movies"]
    for movie in movies:
        if movie["id"] == id:
            return movie
    raise Exception("Movie not found with id: " + id)


def movie_with_title(_,info,title):
    with open('{}/databases/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if str(movie["title"]) == title:
                return movie
        raise Exception("Movie not found with title : " + title)

def add_movie(_, info, id, title, rating, director):
    with open('{}/databases/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        
    for movie in movies["movies"]:
        if str(movie["id"]) == id:
            raise Exception("Movie ID already exists : " + id)
    
    newmovie = {
        "id": id,
        "title" : title,
        "rating" : rating,
        "director" : director
    }
    movies["movies"].append(newmovie)
    newmovies = movies
    with open('{}/databases/movies.json'.format("."), "w") as wfile:
        json.dump(newmovies, wfile)
    return newmovie

def update_movie_rate(_,info,id,rating):
    newmovie = None
    with open('{}/databases/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        
        for movie in movies['movies']:
            if movie['id'] == id:
                movie['rating'] = rating
                newmovie = movie
        
        if newmovie is None:
            raise Exception("Movie not found with id: " + id)
    
    with open('{}/databases/movies.json'.format("."), "w") as wfile:
        json.dump(movies, wfile)
    return newmovie

def remove_movie_with_id(_, info, id):
    with open('{}/databases/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
    removed_movie = None
        
    for movie in movies["movies"]:
        if str(movie["id"]) == id:
            movies["movies"].remove(movie)
            removed_movie = movie
        
    if removed_movie is None:
        raise Exception("Movie not found with id: " + id)

    with open('{}/databases/movies.json'.format("."), "w") as wfile:
        json.dump(movies, wfile)
    return movie