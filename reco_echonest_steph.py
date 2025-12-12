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
    df = df.loc[:, ~df.columns.duplicated()].copy()

    cur.close()
    conn.close()
    return df


def load_realiser():
    conn = connection_db()
    cur = conn.cursor()
    cur.execute("SELECT * from sae5_6.realiser JOIN sae5_6.artist ON sae5_6.realiser.artist_id = sae5_6.artist.artist_id JOIN sae5_6.track on sae5_6.track.track_id =  sae5_6.realiser.track_id ")
    data = cur.fetchall()
    columns = [desc[0] for desc in cur.description]  
    df = pd.DataFrame(data, columns=columns)
    df.columns = df.columns.map(lambda x: "_".join(x) if isinstance(x, tuple) else x)
    df = df.loc[:, ~df.columns.duplicated()].copy()
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
artists_tracks = load_realiser()

# print(tracks)
# print(users)



############## vecteurs pour echonest ##############
echonest = {}

for _, row in tracks.iterrows():
    track_id = row['track_id']

    # si track_id est une Series :
    if isinstance(track_id, pd.Series):
        track_id = track_id.iloc[0]

    echonest[track_id] = [
        row['acousticness'],
        row['energy'],
        row['instrumentalness'],
        row['liveness'],
        row['speechiness'],
        row['valence'],
        row['danceability'],
        row['tempo']
    ]


# print(echonest[0:10])




def echonest_recommend(track_id, n): #prend en entrée un id de track et un nombre n qui va correspondre au nombre de tracks recommandés qui vont être renvoyés 
    if(track_id in echonest.keys()): #on vérifie si le track comporte des données echonest
        sim = [] # liste qui va contenir des tuples comrpenant le track_id et la similarité 
        echo = echonest[track_id] #on récupère les données echonest du track prit en entré
        for key in echonest.keys():  #on parcourt tous les tracks d'echonest
            if(key!=track_id): #on vérifie si le track_id en entrée est différent de celui qu'on compare actuellement
                similarity = basicsfunctions.simCos(echo, echonest[key]) #calcul de la similarité avec simCos du fichier basicsfunctions réalisé en TD
                sim.append((key, similarity))#on ajoute la similarité couplé avec son track_id dans la liste sim

        sim.sort(key=lambda x: x[1], reverse=True) #on trie par "score" de similarité
        return sim[:n] #on renvoie les n track_id qui ont des echonest similaires
    else:
        return "Track_id sans données echonest"

#test
track_id_test = 140
simi = echonest_recommend(track_id_test, 10)

#on écupère le titre et l'artiste 
titre_test = artists_tracks.loc[artists_tracks['track_id'] == track_id_test, ['track_title', 'artist_name']].iloc[0].tolist()

print(f"Musique de départ : {titre_test[0]} - {titre_test[1]}")

print("\nMusiques recommandées :")
for couple in simi:
    track_id = couple[0]
    titre = artists_tracks.loc[artists_tracks['track_id'] == track_id,['track_title', 'artist_name']].iloc[0].tolist()
    print(f"{titre[0]} - {titre[1]}")

# après écoute des morceaux -> résultat plutot satisfaisant