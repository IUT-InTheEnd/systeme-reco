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
    """
    
CREATE TABLE sae5_6.user (
    user_id SERIAL PRIMARY KEY,
    user_age FLOAT NOT NULL,
    user_job VARCHAR(100),
    user_plays_music TEXT,
    user_pseudo VARCHAR(100) NOT NULL,
    user_password TEXT NOT NULL,
    user_gender VARCHAR(100),
    user_instruments TEXT,
    user_music_contexts TEXT,
    profile_id INT NOT NULL,
    FOREIGN KEY (profile_id) REFERENCES sae5_6.user_profile(user_profile_id)
);


CREATE TABLE sae5_6.user_profile (
    user_profile_id SERIAL PRIMARY KEY,
    music_envy_today TEXT NOT NULL,
    feeling INT NOT NULL,
    music_preference INT NOT NULL,
    music_style_preference INT NOT NULL,
    music_reason TEXT NOT NULL,
    listening_context TEXT NOT NULL,
    current_music_type INT,
    usual_listening_mode INT NOT NULL,
    likes_discovery INT NOT NULL,
    attend_live_concert INT NOT NULL,
    repeat_listening INT NOT NULL,
    explicit_ok INT NOT NULL,
    avg_song_length FLOAT NOT NULL,
    avg_daily_listen_time FLOAT NOT NULL,
    recommanded_artists TEXT    
);

    """
    
    conn = connection_db()
    cursor = conn.cursor()
    print("Creating fav tracks / artists / album from genres and other data...")
    
    # Pull les datas users et leurs profils
    cursor.execute("SELECT * FROM sae5_6.user u JOIN sae5_6.user_profile up ON u.profile_id = up.user_profile_id;")
    users = cursor.fetchall()
    for user in users:
        user_id = user[0]
        user_age = user[1]
        user_job = user[2]
        user_plays_music = user[3]
        user_gender = user[6]
        user_instruments = user[7]
        user_music_contexts = user[8]
        profile_id = user[9]
        music_envy_today = user[10]
        feeling = user[11]
        music_preference = user[12]
        music_style_preference = user[13]
        music_reason = user[14]
        listening_context = user[15]
        current_music_type = user[16]
        usual_listening_mode = user[17]
        likes_discovery = user[18]
        attend_live_concert = user[19]
        repeat_listening = user[20]
        explicit_ok = user[21]
        avg_song_length = user[22]
        avg_daily_listen_time = user[23]
        recommanded_artists = user[24]

if __name__ == "__main__":
    main()