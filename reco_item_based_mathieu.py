import math
import numpy as np
import pandas as pd 
import psycopg2
import pycountry
from sklearn.preprocessing import MultiLabelBinarizer
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



def get_language_name(code):
    try:
        return pycountry.languages.get(alpha_2=code).name
    except:
        return "Unknown" 

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

    df['track_language'] = df['track_language_code'].apply(get_language_name)

    cur.close()
    conn.close()

    df_genres = pd.DataFrame(data_genres, columns=['track_id', 'genre_title'])

    genres_par_track = df_genres.groupby('track_id')['genre_title'].apply(list)
    df['track_genres'] = df['track_id'].map(genres_par_track)

    return df

def create_vecteur_genre(df):
    mlb = MultiLabelBinarizer()
    genre_matrix = mlb.fit_transform(df['track_genres'])
    df_genres_vecteurs = pd.DataFrame(genre_matrix, columns=mlb.classes_, index=df.index)

    return df_genres_vecteurs

def create_vecteur_echonest(df):
    echonest_features = [
        'danceability', 
        'energy', 
        'valence', 
        'tempo', 
        'loudness', 
        'acousticness', 
        'instrumentalness', 
        'speechiness', 
        'liveness'
    ]
    features_dispo = [col for col in echonest_features if col in df.columns]
    mlb = MultiLabelBinarizer()
    scaler = MinMaxScaler()
    matrix_vectors = scaler.fit_transform(df[features_dispo])
    

    return matrix_vectors

def create_matrice_similitude(df,vecteur):
    cosine_sim = cosine_similarity(vecteur)
    
    indices = pd.Series(df.index, index=df['track_id']).drop_duplicates()
    return cosine_sim, indices

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

#Systeme de recommendation basique, on filtre par genres et langue préférés d'une personne

def recommendation(user,n):
    tracks = load_tracks()

    quota_par_genre = math.ceil(n / len(user["track_genres"]))
    print(quota_par_genre)

    for col_name, value in user.items(): 
        if col_name == "track_genres":
            recommend_tracks = tracks[tracks[col_name].apply(lambda x: any(v in x for v in value))]
        else:
            recommend_tracks = tracks[tracks[col_name].apply(lambda x: value in x)]
    if(recommend_tracks.empty or len(recommend_tracks) < n ):
        recommend_tracks = tracks[tracks["track_genres"].apply(lambda x: user["track_genres"] in x)]
    
    print(recommend_tracks)
    recommend_tracks = recommend_tracks.sample(n=n)
    return recommend_tracks["track_title"].sample(frac=1)

user = {
    "track_genres" : ["Hip-Hop","Rap"],
    "track_language" : "Korean"
}

def recommendation_terminal():
    genres = input("Quelle est votre genre préféré ? ")
    instrumental = input('Voulez-vous des sons avec des paroles(O/N)? ')
    instrumental = True if instrumental == "N" else False
    if(instrumental == False):
        langue = input('Langue des paroles : ')
    else : 
        langue = ""
    n = input('Nombre de tracks : ')


    user = {
        "track_genres" : genres,
        "track_language" : langue,
        "track_instrumental" : instrumental

    }
    print(recommendation(user,n))



# recommendation avec matrice de similitude avec un vecteur de genre pour une musique
def recommendation_id(track_id, df, cosine_sim, indices, n=10):
    try:
        idx = indices[track_id]
    except KeyError:
        return pd.DataFrame() # L'ID n'existe pas

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    sim_scores = sim_scores[1:n+1]

    track_indices = [i[0] for i in sim_scores]

    return df.iloc[track_indices]

tracks = load_tracks()
v = create_vecteur_genre(tracks)
echo = create_vecteur_echonest(tracks)
m, indices = create_matrice_similitude(tracks,echo)

id_test = tracks['track_id'].iloc[0]
titre_test = tracks['track_title'].iloc[0]
        
print(f"Recommandations basées sur : {titre_test} (ID: {id_test})")

recos = recommendation_id(id_test,tracks,m,indices,10)

if not recos.empty:
    print(recos[['track_title','track_genres']])
'''
reste à faire 

charger la base et récupérer les données

établir une liste des vecteurs de cractéristiques des musiques ([pop -> 1, rock -> 2 ...; groupe -> 1, single -> 2; niveau_explicit : pas explicit -> 1, un peu -> 2, moyen -> 3, très -> 4.....])

prénoter certains morceaux avec les artistes / musiques qu'ils ont proposé dans le questionnaire

tester le tout en recommandant et évaluant la qualité de la recommandation

'''

