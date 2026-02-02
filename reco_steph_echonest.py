import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import basicsfunctions
import load

# ============================================================
# Chargement des données
# ============================================================

tracks = load.load_tracks()
users = load.load_users()
artists_tracks = load.load_realiser()
genres = load.load_genres()

# ============================================================
# Normalisation du tempo
# ============================================================

scaler = MinMaxScaler()
tracks['tempo_norm'] = scaler.fit_transform(tracks[['tempo']])

# ============================================================
# Construction des vecteurs Echonest (vectorisée)
# ============================================================

ECHONEST_FEATURES = [
    'acousticness',
    'energy',
    'instrumentalness',
    'liveness',
    'speechiness',
    'valence',
    'danceability',
    'tempo_norm'
]

echonest = dict(
    zip(
        tracks['track_id'],
        tracks[ECHONEST_FEATURES].to_numpy().tolist()
    )
)

# ============================================================
# Pré-calculs (accès O(1))
# ============================================================

# explicit par track
track_explicit = tracks.set_index('track_id')['track_explicit'].to_dict()

# genres par track
track_genres = tracks.set_index('track_id')['track_genres'].to_dict()

# mapping genre -> parent
genre_to_parent = (
    genres
    .set_index('genre_title')['genre_parent_id']
    .dropna()
    .to_dict()
)

# parents par track
track_parent_genres = {}
for tid, g_list in track_genres.items():
    if isinstance(g_list, list):
        track_parent_genres[tid] = {
            genre_to_parent[g]
            for g in g_list
            if g in genre_to_parent
        }
    else:
        track_parent_genres[tid] = set()

# préférences utilisateurs
user_explicit_ok = users.set_index('user_id')['explicit_ok'].to_dict()
user_discovery = users.set_index('user_id')['likes_discovery'].to_dict()

# ============================================================
# Fonctions utilitaires
# ============================================================

def verifie_explicit(user_id, track_id):
    """
    user explicit : false -> track explicit interdit
    user explicit : true  -> tout autorisé
    """
    return (
        user_explicit_ok[user_id] >= 0
        or not track_explicit.get(track_id, False)
    )


def has_same_genre(t1, t2):
    return bool(
        set(track_genres.get(t1, []))
        & set(track_genres.get(t2, []))
    )


def has_same_parent_genre(t1, t2):
    return bool(
        track_parent_genres.get(t1, set())
        & track_parent_genres.get(t2, set())
    )

# ============================================================
# Recommandation Echonest (optimisée)
# ============================================================

def echonest_recommend(user_id, track_id, n=5, compareGenre=True):

    if track_id not in echonest:
        print("Track_id sans données echonest")
        return []

    base_vector = echonest[track_id]
    base_genres = set(track_genres.get(track_id, []))
    base_parents = track_parent_genres.get(track_id, set())

    similarities = []

    for other_id, other_vector in echonest.items():
        if other_id == track_id:
            continue

        # filtre explicit
        if not verifie_explicit(user_id, other_id):
            continue

        # 🎵 filtre genre
        if compareGenre:
            other_genres = track_genres.get(other_id, [])
            if not isinstance(other_genres, list):
                other_genres = []
            other_genres = set(other_genres)

            base_genres = track_genres.get(track_id, [])
            if not isinstance(base_genres, list):
                base_genres = []
            base_genres = set(base_genres)

            if not (
                base_genres & other_genres
                or base_parents & track_parent_genres.get(other_id, set())
            ):
                continue

        # similarité cosinus
        sim = basicsfunctions.simCos(base_vector, other_vector)
        similarities.append((other_id, sim))

    if not similarities:
        return []

    similarities.sort(key=lambda x: x[1], reverse=True)
    n = min(n, len(similarities))

    # 🌱 mode découverte
    if user_discovery[user_id] > 2 and n > 1:
        return similarities[:n-1] + [similarities[-1]]

    return similarities[:n]



#test
#track_id_test = 1052 # musique explicite
track_id_test = 156031 # musique rajoutée proposée par un utilisateur
# track_id_test = 4104 # musique non explicite
user_id_test = 1  # user qui aime les musiques explicites et la découverte
# user_id_test = 10 # user qui n'aime pas les musiques explicites et la découverte
simi = echonest_recommend(user_id_test, track_id_test, 5, True)

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


#affichage des titres et artistes des n musiques les plus similaires
print("\nMusiques recommandées :")
for couple in simi:
    track_id = couple[0]
    similarity = couple[1]
    titre = artists_tracks.loc[artists_tracks['track_id'] == track_id,['track_title', 'artist_name']].iloc[0].tolist()
    print(f"{titre[0]} - {titre[1]} (similarity: {similarity})")