import pandas as pd
import basicsfunctions
import load


tracks = load.load_tracks()
users = load.load_users()
artists_tracks = load.load_realiser()

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

# affichage du titre et de l'artiste du track de test
print(f"Musique de départ : {titre_test[0]} - {titre_test[1]}")

# affichage des titres et artistes des n musiques les plus similaires
print("\nMusiques recommandées :")
for couple in simi:
    track_id = couple[0]
    titre = artists_tracks.loc[artists_tracks['track_id'] == track_id,['track_title', 'artist_name']].iloc[0].tolist()
    print(f"{titre[0]} - {titre[1]}")

# après écoute des morceaux -> résultat plutot satisfaisant