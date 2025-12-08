import math
import pandas as pd 
import psycopg2

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

print(tracks)
print(users)

print(tracks.columns.tolist())

tracks20 = tracks.head(20)

def attributeVectors(tracks):
    vectors = ['acousticness', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence', 'danceability', 'tempo']
    valeurs = [col for col in vectors if col in tracks.columns]
    tracks['vector'] = tracks.apply(lambda row : [round(row[col], 2) for col in valeurs], axis=1)
    return tracks

tracksVectors = attributeVectors(tracks20)

print(tracksVectors['acousticness', 'energy', 'instrumentalness', 'liveness', 'speechiness', 'valence', 'danceability', 'tempo','vector'])
'''

établir une liste des vecteurs de cractéristiques des musiques ([pop -> 1, rock -> 2 ...; groupe -> 1, single -> 2; niveau_explicit : pas explicit -> 1, un peu -> 2, moyen -> 3, très -> 4.....])

prénoter certains morceaux avec les artistes / musiques qu'ils ont proposé dans le questionnaire

tester le tout en recommandant et évaluant la qualité de la recommandation

'''