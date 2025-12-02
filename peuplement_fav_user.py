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
        music_envy_today = user[10]
        feeling = user[11]
        music_preference = user[12]
        music_style_preference = user[13]
        music_reason = user[14]
        listening_context = user[15]
        current_music_type = user[16]
        attend_live_concert = user[19]
        explicit_ok = user[21]
        avg_song_length = user[22]
        recommanded_artists = user[24]
        print(user_id, music_envy_today, feeling, music_preference, music_style_preference, music_reason, listening_context, current_music_type, attend_live_concert, explicit_ok, avg_song_length, recommanded_artists)

if __name__ == "__main__":
    main()
    