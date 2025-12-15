import pandas as pd
import basicsfunctions
import load


tracks = load.load_tracks()
users = load.load_users()
artists_tracks = load.load_realiser()
genres = load.load_genres()

# print(tracks)
# print(users)


# vecteurs pour echonest
echonest = {}

for _, row in tracks.iterrows():
    track_id = row['track_id'] #pour les tracks sans echonest

    # les tracks avec echonest, track_id est une Serie
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

def hasSameParentGenre(track_id1, track_id2):
    g1 = tracks.loc[tracks['track_id'] == track_id1, 'track_genres'].values[0]
    g2 = tracks.loc[tracks['track_id'] == track_id2, 'track_genres'].values[0]

    # vérification robuste
    if not isinstance(g1, list) or not isinstance(g2, list):
        return False
    if len(g1) == None or len(g2) == None:
        return False

    parents1 = genres.loc[
        genres['genre_title'].isin(g1),
        'genre_parent_id'
    ].dropna()

    parents2 = genres.loc[
        genres['genre_title'].isin(g2),
        'genre_parent_id'
    ].dropna()

    return len(set(parents1) & set(parents2)) > 0


def hasSameGenre(track_id1, track_id2):
    g1 = tracks.loc[tracks['track_id'] == track_id1, 'track_genres'].values[0]
    g2 = tracks.loc[tracks['track_id'] == track_id2, 'track_genres'].values[0]

    # vérification robuste
    if not isinstance(g1, list) or not isinstance(g2, list):
        return False
    if len(g1) == None or len(g2) == None:
        return False

    return len(set(g1) & set(g2)) > 0

def get_explicit_track(track_id):
    explicit = tracks.loc[tracks['track_id'] == track_id, 'track_explicit'].values[0]
    return explicit

def get_explicit_user(user_id):
    explicit = users.loc[users['user_id'] == user_id, 'explicit_ok'].values[0]
    return explicit > 0

def echonest_recommend(user, track_id, n, compareGenre): #prend en entrée un id de track et un nombre n qui va correspondre au nombre de tracks recommandés qui vont être renvoyés 
    if(track_id in echonest.keys()): #on vérifie si le track comporte des données echonest
        sim = [] #liste qui va contenir des tuples comrpenant le track_id et la similarité 
        echo = echonest[track_id] #on récupère les données echonest du track prit en entré
        for key in echonest.keys():  #on parcourt tous les tracks d'echonest
            if(key!=track_id): #on vérifie si le track_id en entrée est différent de celui qu'on compare actuellement
                if (get_explicit_user(user) == get_explicit_track(key)): #on regarde si les préférences explicites de l'utilisateur correspondent à celles du track de départ
                    similarity = basicsfunctions.simCos(echo, echonest[key]) #calcul de la similarité avec simCos du fichier basicsfunctions réalisé en TD
                    # on ajoute les similarités des tracks qui font parti du même genre parent que le track de départ
                    if(compareGenre and (hasSameGenre(track_id, key) or hasSameParentGenre(track_id, key))):
                        sim.append((key, similarity))#on ajoute la similarité couplé avec son track_id dans la liste sim
                    elif not compareGenre: #s'il ne veut pas que ce soit du même genre forcément
                        sim.append((key, similarity))

        sim.sort(key=lambda x: x[1], reverse=True) #on trie par "score" de similarité
        if(len(sim) < n):
            n = len(sim)
            print("Pas assez de musiques similaires dans la base de données, on en renvoie que ", n)

        # si l'utilisateur aime la nouveauté, on remplace la nème recommandation renvoyée par une musique moins similaire
        if users.loc[users['user_id'] == user, 'likes_discovery'].values[0] > 0:
            if n > 0 and len(sim) >= n:
                sim[n-1] = sim[-1]

        return sim[:n] #on renvoie les n track_id qui ont des echonest similaires
    else:
        return "Track_id sans données echonest"


#test
track_id_test = 139
user_id_test = 1
simi = echonest_recommend(user_id_test, track_id_test, 10, True)

#on écupère le titre et l'artiste 
rows_test = artists_tracks.loc[
    artists_tracks['track_id'] == track_id_test,
    ['track_title', 'artist_name']
]

if rows_test.empty:
    print(f"Musique de départ : Track {track_id_test} - Artiste inconnu")
else:
    titre_test = rows_test.iloc[0].tolist()
    print(f"Musique de départ : {titre_test[0]} - {titre_test[1]}")


# affichage des titres et artistes des n musiques les plus similaires
print("\nMusiques recommandées :")
for couple in simi:
    track_id = couple[0]
    titre = artists_tracks.loc[artists_tracks['track_id'] == track_id,['track_title', 'artist_name']].iloc[0].tolist()
    print(f"{titre[0]} - {titre[1]}")



# après écoute des morceaux -> résultat plutot satisfaisant