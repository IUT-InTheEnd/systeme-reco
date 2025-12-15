import psycopg2
import psycopg2.extras
import basicsfunctions
import load
import pandas as pd
import numpy as np
from collections import Counter
import ast

# ----- Part 2: Refinement using favorites -----
# Once user has rated some music/artists/albums,
# refine recommendations by comparing with similar users' favorites

def connection_db():
    return psycopg2.connect(
        dbname="InTheEnd_DB",
        user="InTheEnd_User",
        password="InTheEnd_Password",
        host="localhost",
        port="25000"
    )

def load_user_favorites(user_id, conn):
    """Load user's favorite music, artists, and albums"""
    cursor = conn.cursor()
    
    # Charger les favoris de l'utilisateur
    cursor.execute("""SELECT track_id FROM sae5_6.ajoute_favori WHERE user_id = %s""", (user_id,))
    track_fav = cursor.fetchall()
    
    cursor.execute("""SELECT artist_id FROM sae5_6.user_prefere_artiste WHERE user_id = %s""", (user_id,))
    artist_fav = cursor.fetchall()
    
    cursor.execute("""SELECT album_id FROM sae5_6.user_ajoute_album_favoris WHERE user_id = %s""", (user_id,))
    album_fav = cursor.fetchall()
    
    cursor.execute("""SELECT genre_id FROM sae5_6.ajoute_genre_favoris WHERE user_id = %s""", (user_id,))
    genre_fav = cursor.fetchall()
    
    cursor.execute("""SELECT track_id, nb_ecoute FROM sae5_6.user_ecoute WHERE user_id = %s""", (user_id,))
    listen_data = cursor.fetchall()
    
    cursor.close()
    
    if not track_fav and not artist_fav and not album_fav:
        return {"tracks": [], "artists": [], "albums": []}
    
    return {
        "tracks": [f[0] for f in track_fav if f[0] is not None],
        "artists": list(set([f[0] for f in artist_fav if f[0] is not None])),
        "albums": list(set([f[0] for f in album_fav if f[0] is not None])),
        "listen_data": {f[0]: f[1] for f in listen_data if f[0] is not None},
        "genres": [f[0] for f in genre_fav if f[0] is not None]
    }

def get_track_features(track_id, tracks_df):
    """Extract numeric features from a track"""
    if track_id not in tracks_df.index:
        return None
    
    track = tracks_df.loc[track_id]
    # Select numeric columns for comparison
    numeric_cols = track.select_dtypes(include=[np.number]).columns
    return track[numeric_cols].values

def similarity_user_favorites(user1_favs, user2_favs):
    """
    Calculate similarity between two users based on their favorites
    Returns a similarity score (0-1)
    """
    tracks1 = set(user1_favs.get("tracks", []))
    tracks2 = set(user2_favs.get("tracks", []))
    
    artists1 = set(user1_favs.get("artists", []))
    artists2 = set(user2_favs.get("artists", []))
    
    albums1 = set(user1_favs.get("albums", []))
    albums2 = set(user2_favs.get("albums", []))
    
    # Jaccard similarity for each type
    def jaccard(set_a, set_b):
        if len(set_a | set_b) == 0:
            return 0
        return len(set_a & set_b) / len(set_a | set_b)
    
    track_sim = jaccard(tracks1, tracks2)
    artist_sim = jaccard(artists1, artists2)
    album_sim = jaccard(albums1, albums2)
    
    # Weighted average (can be tuned)
    weights = {"tracks": 0.5, "artists": 0.3, "albums": 0.2}
    total_weight = sum(weights.values())
    
    similarity = (
        track_sim * weights["tracks"] +
        artist_sim * weights["artists"] +
        album_sim * weights["albums"]
    ) / total_weight
    
    return similarity

def find_similar_users_by_favorites(target_user_id, all_users_df, conn, similarity_threshold=0.1):
    """
    Find users similar to target user based on their favorite tracks/artists/albums
    Returns list of (user_id, similarity_score) tuples
    """
    target_favs = load_user_favorites(target_user_id, conn)
    
    if not any([target_favs["tracks"], target_favs["artists"], target_favs["albums"]]):
        print(f"[Part 2] User {target_user_id} has no favorites yet")
        return []
    
    similar_users = []
    
    for user_id in all_users_df["user_id"].unique():
        if user_id == target_user_id:
            continue
        
        user_favs = load_user_favorites(user_id, conn)
        sim = similarity_user_favorites(target_favs, user_favs)
        
        if sim >= similarity_threshold:
            similar_users.append((user_id, sim))
    
    # Sort by similarity score (descending)
    similar_users.sort(key=lambda x: x[1], reverse=True)
    
    return similar_users

def recommend_based_on_similar_users(target_user_id, similar_users, tracks_df, top_k=10):
    """
    Aggregate recommendations from similar users
    Returns top-k tracks not yet rated by target user
    """
    if not similar_users:
        return []
    
    conn = connection_db()
    
    # Get target user's favorites
    target_favs = load_user_favorites(target_user_id, conn)
    target_fav_set = set(target_favs["tracks"])
    
    # Aggregate tracks from similar users with weighting
    track_scores = Counter()
    
    for sim_user_id, similarity_score in similar_users:
        sim_user_favs = load_user_favorites(sim_user_id, conn)
        
        for track_id in sim_user_favs["tracks"]:
            if track_id not in target_fav_set:  # Don't recommend already liked tracks
                track_scores[track_id] += similarity_score
    
    conn.close()
    
    # Get top-k recommendations
    recommendations = track_scores.most_common(top_k)
    
    return recommendations