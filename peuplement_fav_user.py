import psycopg2
import psycopg2.extras

def connection_db():
    return psycopg2.connect(
        dbname="InTheEnd_DB",
        user="InTheEnd_User",
        password="InTheEnd_Password",
        host="localhost",
        port="25000"
    )

def main():    
    conn = connection_db()
    cursor = conn.cursor()
    print("Creating fav tracks / artists / album from genres and other data...")
    
    # Pull les datas users et leurs profils
    cursor.execute("SELECT * FROM sae5_6.user u JOIN sae5_6.user_profile up ON u.profile_id = up.user_profile_id;")
    users = cursor.fetchall()
    for user in users:
        user_id = user[0]
        use_age_moyenne = user[1]
        user_job = user[2]
        user_plays_music = user[3]
        user_pseudo = user[4]
        user_password = user[5]
        user_sex = user[6]
        user_instruments = user[7]
        user_music_contexts = user[8]
        user_profile_id = user[9]
        user_profile_id_id = user[10]
        user_music_envy_today = user[11]
        user_feeling = user[12]
        user_music_preference = user[13]
        user_music_style_preference = user[14]
        user_music_reason = user[15]
        user_listening_context = user[16]
        user_current_music_type = user[17]
        user_usual_listening_mode = user[18]
        user_likes_discovery = user[19]
        user_attend_live_concert = user[20]
        user_repeat_listening = user[21]
        user_explicit_ok = user[22]
        user_avg_song_length = user[23]
        user_avg_daily_listen_time = user[24]
        user_recommanded_artists = user[25]
        
        # Récupère les genres préférés de l'utilisateur
        cursor.execute("SELECT genre_id FROM sae5_6.ajoute_genre_favoris WHERE user_id = %s;", (user_id,))
        fav_genres = cursor.fetchall()
        fav_genres_ids = []
        fav_genres_ids = [genre[0] for genre in fav_genres]

            
        # Récupère les musics qui satisfait le genre favoris, l'explicit ok, la durée moyenne des chansons et un like sur chaque user_recommanded_artists
        query = """
                SELECT m.track_id, m.artist_id, m.album_id
                FROM sae5_6.track m
                WHERE m.genre_id = ANY(%s)
                AND (%s = 1 OR m.explicit = 0)
                AND m.duration <= %s + 30
                AND m.duration >= %s - 30
                AND (%s = '{}' OR m.artist_id = ANY(%s))
                LIMIT 10;
            """
        
        fav_musics = cursor.fetchall()
        print(fav_musics)
        ()    
if __name__ == "__main__":
    main()
    