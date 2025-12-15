import psycopg2
from math import ln
import basicsfunctions

weights = {"tracks": 0.3, "artists": 0.2, "albums": 0.2, "genres": 0.2, "languages": 0.1}
total_weight = sum(weights.values())

def connection_db():
    return psycopg2.connect(
        dbname="InTheEnd_DB",
        user="InTheEnd_User",
        password="InTheEnd_Password",
        host="localhost",
        port="25000"
    )

def note(listens, is_track_fav, is_artist_fav, is_album_fav, is_genre_fav, listen_language) :
    listen_score = (ln(listens) + 1)/10 if listens <= 8103 else 1
    return (
        listen_score + (
            is_track_fav * weights["tracks"] +
            is_artist_fav * weights["artists"] +
            is_album_fav * weights["albums"] +
            is_genre_fav * weights["genres"] +
            listen_language * weights["languages"]
            ) / total_weight
        ) / 2

def get_pred_for_user(user_id, track_id, sim=basicsfunctions.simCos) :
    prediction = 0
    deno = 0
    nume = 0
    for
    return prediction
