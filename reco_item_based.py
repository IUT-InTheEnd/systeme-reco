import psycopg2
import pandas as pd
import basicsfunctions


def connection_db():
    return psycopg2.connect(
        dbname="InTheEnd_DB",
        user="InTheEnd_User",
        password="InTheEnd_Password",
        host="localhost",
        port="25000"
    )


def load_tracks():
    
    conn = connection_db()
    cur = conn.cursor()
    cur.execute("SELECT * from sae5_6.track JOIN sae5_6.track_echonest on sae5_6.track.track_id =  sae5_6.track_echonest.track_id")
    data = cur.fetchall()
    columns = [desc[0] for desc in cur.description]  
    df = pd.DataFrame(data, columns=columns)

    cur.close()
    conn.close()
    return df

def load_users():
    
    conn = connection_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sae5_6.user u JOIN sae5_6.user_profile up ON u.profile_id = up.user_profile_id;")
    data = cur.fetchall()
    columns = [desc[0] for desc in cur.description]  
    df = pd.DataFrame(data, columns=columns)

    cur.close()
    conn.close()
    return df


tracks = load_tracks()
users = load_users()

# print(tracks)
# print(users)



############## vecteurs pour echonest ##############

# echonest = []

# # création de vecteurs pour les echonest
# for _, row in tracks.iterrows():
#     echonest.append([
#         row['track_id'][0], row['acousticness'], row['energy'],
#         row['instrumentalness'], row['liveness'], row['speechiness'],
#         row['valence'], row['danceability'], row['tempo'],
#         row['artist_discovery'], row['artist_hottness'],
#         row['artist_familiarity'], row['track_hottness'],
#         row['track_currency']
#     ])

# print(echonest[0:10])





