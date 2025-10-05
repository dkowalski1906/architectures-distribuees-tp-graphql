import json
from graphql import GraphQLError
import requests

SCHEDULE_URL = "http://localhost:3202" # service Schedule
MOVIE_URL   = "http://localhost:3200" # service Movie
USER_URL  = "http://localhost:3201" # microservice User

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
    bookings = json.load(jsf)["bookings"]
    
def write(bookings_data):
    with open('{}/databases/bookings.json'.format("."), 'w') as f:
        full = {}
        full['bookings'] = bookings_data
        json.dump(full, f)

def resolve_booking_userid(booking, info):
    user_id = booking["userid"]
    with open('../user/databases/users.json') as file:
        users = json.load(file)["users"]
    for user in users:
        if user["id"] == user_id:
            return user
    raise GraphQLError("User not found: " + user_id)

def resolve_booking_dates(booking, info):
    dates_to_return = []
    for date in booking["dates"]:
        dates_to_return.append(date)
    return dates_to_return

def resolve_date_movies(date, info):
    movies_to_return = []
    for movieid in date["movies"]:
        query = f"""
        {{
            movie_with_id(id: "{movieid}") {{
                id
                title
                director
                rating
            }}
        }}
        """
        response = requests.post(f"{MOVIE_URL}/graphql",json={'query': query})
        data = response.json()
        movie_details = data["data"]["movie_with_id"]
        movies_to_return.append(movie_details)
    return movies_to_return

def bookings_json(_, info):
        return bookings

def booking_with_user_id(_, info, id):
    for booking in bookings:
        if booking["userid"] == id:
            return booking
    raise GraphQLError("Booking not found with userid: " + id)

def add_booking(_, info, userid, date, movieid):
    
    # vérifie auprès de Schedule que le film est dispo à cette date
    # TODO à faire avec requête gRCP
    
    # si l’utilisateur existe déjà
    for b in bookings:
        if b["userid"] == userid:
            for d in b["dates"]:
                if d["date"] == date:
                    if movieid in d["movies"]:
                        raise GraphQLError("Booking already exists")
                    d["movies"].append(movieid)
                    write(bookings)
                    return b
            # sinon nouvelle date pour l’utilisateur
            b["dates"].append({"date": date, "movies": [movieid]})
            write(bookings)
            return b
    
    # si l’utilisateur n’existe pas encore -> on le crée
    newbooking = {
        "userid": userid,
        "dates": [
            {
                "date": date, "movies": [movieid]
            }
        ]
    }
    bookings.append(newbooking)
    write(bookings)
    return newbooking

def remove_booking_with_movie_date_user(_, info, userid, date, movieid):
    for b in bookings:
        if b["userid"] == userid:
            for d in b["dates"]:
                if d["date"] == date:
                    if movieid in d["movies"]:
                        d["movies"].remove(movieid)
                        write(bookings)
                        return b
                    raise GraphQLError("Movie not found in this booking")
    raise GraphQLError("Booking not found")

def remove_bookings_with_user_id(_, info, userid):
    global bookings
    new_bookings = [b for b in bookings if b["userid"] != userid]
    if len(new_bookings) == len(bookings):
        raise GraphQLError("User not found")

    bookings = new_bookings
    write(bookings)
    return (f"All bookings removed for userid : {userid}")