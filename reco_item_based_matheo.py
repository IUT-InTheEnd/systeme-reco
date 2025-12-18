import math
import numpy as np
import pandas as pd 
import psycopg2
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

# fonctions de base sur les vecteurs

def prodScal(a, b):
    if len(a) != len(b):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    res = 0
    for i in range(len(a)):
        res += a[i] * b[i]
    return res

def norm(vect):
    res = 0
    for x in vect:
        res += x**2
    return math.sqrt(res)

def inter(vectA, vectB):
    if len(vectA) != len(vectB):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    count = 0
    for i in range(len(vectA)):
        if ((vectA[i] == vectB[i]) and (vectA[i] != 0)):    
            count += 1
    return count

def union(vectA, vectB):
    if len(vectA) != len(vectB):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    count = 0
    for i in range(len(vectA)):
        if (vectA[i] != 0 or vectB[i] != 0):
            count += 1
    return count

def distEucl(vectA, vectB):
    if len(vectA) != len(vectB):
        raise ValueError("Les vecteurs doivent avoir la même longueur")
    res = 0
    for i in range(len(vectA)):
        res+= (vectA[i] - vectB[i])**2
    return math.sqrt(res)


# fonctions de similarité

def simCos(vectA, vectB):
    normA = norm(vectA)
    normB = norm(vectB)
    if normA == 0 or normB == 0:
        raise ValueError("La norme d'un vecteur ne peut pas être zéro")
    return prodScal(vectA, vectB) / (normA * normB)

def simEucl1(vectA, vectB):
    return 1 / (1 + distEucl(vectA, vectB))

def simEucl2(vectA, vectB):
    return math.exp(-distEucl(vectA, vectB))

def jacc(vectA, vectB):
    u = union(vectA, vectB)
    if u == 0:
        return 0  
    return inter(vectA, vectB) / u


# fonction de prédiction item-based 

def itemBased(u, i, matr, items):
    sNumerateur = 0
    sDenominateur = 0

    # calcul des similarités entre l'item i et tous les autres items
    sim = [0] * len(items)
    for j in range(len(items)):
        if j != i:
            sim[j] = simCos(items[i], items[j]) 
        else:
            sim[j] = 0

    # calcul de la prédiction
    for j in range(len(items)):
        if matr[u][j] != 0:               
            sNumerateur += matr[u][j] * sim[j] # somme du produit entre la note de u pour chaque item et la similarité de l'item et i
            sDenominateur += abs(sim[j]) # somme des similarités entre les tous les items et i

    if sDenominateur == 0: # eviter la division par zero
        return 0  

    return sNumerateur / sDenominateur


# tester l'item-based sur chaque musique que l'utilisateur n'a pas écouté et recommander les musiques avec la prédiction la plus élevée
def recommend(u, matr, items, n):
    predictions = []

    for i in range(len(items)):
        if matr[u][i] == 0:   # l’utilisateur n’a pas noté l’item
            pred = itemBased(u, i, matr, items)
            predictions.append((i, pred))

    predictions.sort(key=lambda x: x[1], reverse=True) # trier pour pouvoir renvoyer les n meilleures

    return predictions[:n]  # retourner les K meilleurs


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
    
    cur.execute("SELECT * from sae5_6.track JOIN sae5_6.track_echonest on sae5_6.track.track_id = sae5_6.track_echonest.track_id")
    data = cur.fetchall()
    columns = [desc[0] for desc in cur.description]  
    df = pd.DataFrame(data, columns=columns)
    df = df.loc[:, ~df.columns.duplicated()]


    query = """
    SELECT track_id, genre_title FROM sae5_6.genre 
    JOIN sae5_6.contient_genres on sae5_6.contient_genres.genre_id = sae5_6.genre.genre_id
    """

    cur.execute(query)
    data_genres = cur.fetchall()
    cur.close()
    conn.close()

    df_genres = pd.DataFrame(data_genres, columns=['track_id', 'genre_title'])

    genres_par_track = df_genres.groupby('track_id')['genre_title'].apply(list)
    df['track_genres'] = df['track_id'].map(genres_par_track)

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

def load_artists_albums():
    conn = connection_db()
    cur = conn.cursor()
    cur.execute("SELECT * from sae5_6.artist JOIN sae5_6.artiste_chante on sae5_6.artist.artist_id = sae5_6.artiste_chante.artist_id JOIN sae5_6.realiser on sae5_6.realiser.artist_id = sae5_6.artist.artist_id JOIN sae5_6.album on sae5_6.album.album_id = sae5_6.realiser.album_id")
    dataArt = cur.fetchall()
    columns = [desc[0] for desc in cur.description]  
    df = pd.DataFrame(dataArt, columns=columns)
    df = df.loc[:, ~df.columns.duplicated()]
    query = """
    SELECT sae5_6.artist.artist_id,  sae5_6.artist.artist_name, 
    sae5_6.album.album_id, sae5_6.album.album_title, 
    sae5_6.artist.artist_favorites, sae5_6.artist.artist_listens, 
    sae5_6.album.album_favorites, sae5_6.album.album_listens, sae5_6.album.album_type   
    FROM sae5_6.artist 
    JOIN sae5_6.realiser on sae5_6.realiser.artist_id = sae5_6.artist.artist_id
    JOIN sae5_6.album on sae5_6.realiser.album_id = sae5_6.album.album_id
    """
    cur.execute(query)
    data_genres = cur.fetchall()
    cur.close()
    conn.close()
    df_artist_album = pd.DataFrame(data_genres, columns=['artist_id', 'artist_name', 'album_id', 'album_title', 
                                                   'artist_favorites', 'artist_listens', 
                                                   'album_favorites', 'album_listens', 'album_type'])
    return df_artist_album

def load_realiser():
    conn = connection_db()
    cur = conn.cursor()
    cur.execute("SELECT track_id, artist_id, album_id FROM sae5_6.realiser")
    data = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(data, columns=columns)
    cur.close()
    conn.close()
    return df


def init():
    df_tracks = load_tracks()
    df_artist_album = load_artists_albums()
    df_realiser = load_realiser()
    df_init = pd.merge(df_tracks, df_realiser, on='track_id', how='inner')
    df_init = pd.merge(df_init, df_artist_album, on=['artist_id', 'album_id'], how='inner')
    df_init = df_init.drop_duplicates(subset=['track_id']).reset_index(drop=True)
    liste = ['artist_listens', 'artist_favorites', 'album_listens', 'album_favorites']
    for element in liste:
        df_init[element] = np.log1p(df_init[element].fillna(0))
    return df_init


def create_vecteurs(df, mode):
    scaler = MinMaxScaler()
    features = pd.DataFrame(index=df.index)
    if mode == "1" or mode == "3":
        artist_data = df[['artist_listens', 'artist_favorites']]
        features[['art_listens', 'art_fav']] = scaler.fit_transform(artist_data)
    if mode == "2" or mode == "3":
        album_data = df[['album_listens', 'album_favorites']]
        features[['alb_listens', 'alb_fav']] = scaler.fit_transform(album_data)
        
        dummies = pd.get_dummies(df['album_type'], prefix='type')
        features = pd.concat([features, dummies], axis=1)
    return features


def recommandation_artiste_album(df_complet, track_id_cible, mode_choisi):
    if track_id_cible not in df_complet['track_id'].values:
        print("erreur")
        return
    matrice = create_vecteurs(df_complet, mode_choisi)
    i_cible = df_complet[df_complet['track_id'] == track_id_cible].index[0]
    vecteur_cible = matrice.iloc[[i_cible]]
    resSimilarite = cosine_similarity(vecteur_cible, matrice)
    scores = resSimilarite[0]
    scores_i = list(enumerate(scores))
    scores_top = sorted(scores_i, key=lambda x: x[1], reverse=True)
    top_5 = [x for x in scores_top if x[0] != i_cible][:5]
    decouverte = scores_top[-1]
    afficher_joli_resultat(df_complet, i_cible, top_5, decouverte)


def afficher_joli_resultat(df, id_cible, liste_recos, couple_decouverte):
    tracks_cible = df.iloc[id_cible]
    print(f"resultats pour : {tracks_cible['track_title']}")
    print(f"de : {tracks_cible['artist_name']}")
    print(f"dans l'album : {tracks_cible['album_title']} ({tracks_cible['album_type']})")    
    print("========= Nos recommandations =========")
    for i, score in liste_recos:
        ligne = df.iloc[i]
        print(f"{score} - {ligne['track_title']} - {ligne['artist_name']}")
        print("-------------------------------------------")

    print("========= Nouveaux morceaux ========= ")
    i_decouverte, score_decouverte = couple_decouverte
    decouverte = df.iloc[i_decouverte]
    print(f"{score_decouverte} - {decouverte['track_title']} - {decouverte['artist_name']}")
    print("-------------------------------------------")



def main():
    df_test = init()
    while True:
        input_cible = input("id track : ")
        try:
            track_id = int(input_cible)
            print("[1] - Artiste, [2] - Album,[3] - Les deux")
            mode = input("choix :")
            recommandation_artiste_album(df_test, track_id, mode)
        except ValueError:
            print("erreur")
            

main()