import psycopg2
import psycopg2.extras
import basicsfunctions
import load
import pandas as pd
import numpy as np
from collections import Counter
import ast

# ----- Recommandation basée sur les caractéristiques utilisateurs (sans passé par les écoutes sur les musiques) -----

def connection_db():
    return psycopg2.connect(
        dbname="InTheEnd_DB",
        user="InTheEnd_User",
        password="InTheEnd_Password",
        host="localhost",
        port="25000"
    )

def load_user_profile(user_id, conn):
    """
    Charge l'utilisateur
    """
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            u.user_id,
            u.user_age,
            u.user_job,
            u.user_gender,
            u.user_plays_music,
            u.user_instruments,
            u.user_music_contexts,
            up.music_preference,
            up.music_style_preference,
            up.repeat_listening,
            up.avg_song_length,
            up.avg_daily_listen_time,
            up.usual_listening_mode,
            up.likes_discovery,
            up.attend_live_concert,
            up.explicit_ok,
            up.feeling,
            up.listening_context
        FROM sae5_6.user u
        JOIN sae5_6.user_profile up ON u.profile_id = up.user_profile_id
        WHERE u.user_id = %s
    """, (user_id,))
    
    result = cursor.fetchone()
    
    if not result:
        cursor.close()
        return None
    
    profile = {
        'user_id': result[0],
        'user_age': result[1],
        'user_job': result[2],
        'user_gender': result[3],
        'user_plays_music': result[4],
        'user_instruments': result[5] if result[5] else [],
        'user_music_contexts': result[6] if result[6] else [],
        'music_preference': result[7],
        'music_style_preference': result[8],
        'repeat_listening': result[9],
        'avg_song_length': result[10],
        'avg_daily_listen_time': result[11],
        'usual_listening_mode': result[12],
        'likes_discovery': result[13],
        'attend_live_concert': result[14],
        'explicit_ok': result[15],
        'feeling': result[16] if result[16] else [],
        'listening_context': result[17] if result[17] else []
    }
    
    # Charger aussi les genres préférés (comportement musical)
    cursor.execute("""
        SELECT genre_id FROM sae5_6.ajoute_genre_favoris WHERE user_id = %s
    """, (user_id,))
    profile['favorite_genres'] = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    return profile

def similarity_user_profiles(user1_profile, user2_profile):
    """
    Compare les utilisateurs (en forme de vecteur de caractéristiques)    
    Returns: score de similarité entre 0 et 1
    """
    similarity_score = 0
    weights_sum = 0
    
    # LES POIDS SONT ARBITRAIRES, SI PLUS TARD ON SE REND COMPTE QU'IL Y A DES PROBLÈMES ON AJUSTE !!!!!!
        
    # Âge similaire
    if user1_profile.get('user_age') and user2_profile.get('user_age'):
        age_diff = abs(float(user1_profile['user_age']) - float(user2_profile['user_age']))
        age_sim = 1 / (1 + age_diff / 10)  # Normaliser par décennie
        similarity_score += age_sim * 0.15
        weights_sum += 0.15
    
    # Genre
    if user1_profile.get('user_gender') and user2_profile.get('user_gender'):
        gender_sim = 1.0 if user1_profile['user_gender'] == user2_profile['user_gender'] else 0.3
        similarity_score += gender_sim * 0.10
        weights_sum += 0.10
    
    # Métier similaire
    if user1_profile.get('user_job') and user2_profile.get('user_job'):
        job_sim = 1.0 if user1_profile['user_job'] == user2_profile['user_job'] else 0.2
        similarity_score += job_sim * 0.10
        weights_sum += 0.10
    
    # 2. COMPORTEMENT MUSICAL
    
    # Préférence musicale (échelle de goût)
    if user1_profile.get('music_preference') and user2_profile.get('music_preference'):
        pref_diff = abs(float(user1_profile['music_preference']) - float(user2_profile['music_preference']))
        pref_sim = 1 / (1 + pref_diff)
        similarity_score += pref_sim * 0.20
        weights_sum += 0.20
    
    # Style de préférence
    if user1_profile.get('music_style_preference') and user2_profile.get('music_style_preference'):
        style_diff = abs(float(user1_profile['music_style_preference']) - float(user2_profile['music_style_preference']))
        style_sim = 1 / (1 + style_diff)
        similarity_score += style_sim * 0.15
        weights_sum += 0.15
    
    # Temps d'écoute quotidien
    if user1_profile.get('avg_daily_listen_time') and user2_profile.get('avg_daily_listen_time'):
        time_diff = abs(float(user1_profile['avg_daily_listen_time']) - float(user2_profile['avg_daily_listen_time']))
        time_sim = 1 / (1 + time_diff / 60)  # Normaliser par heure
        similarity_score += time_sim * 0.10
        weights_sum += 0.10
    
    # Répétition d'écoute
    if user1_profile.get('repeat_listening') and user2_profile.get('repeat_listening'):
        repeat_diff = abs(float(user1_profile['repeat_listening']) - float(user2_profile['repeat_listening']))
        repeat_sim = 1 / (1 + repeat_diff)
        similarity_score += repeat_sim * 0.10
        weights_sum += 0.10
        
    # Genres préférés (goût musical général)
    genres1 = set(user1_profile.get('favorite_genres', []))
    genres2 = set(user2_profile.get('favorite_genres', []))
    if genres1 or genres2:
        genre_sim = len(genres1 & genres2) / len(genres1 | genres2) if (genres1 | genres2) else 0
        similarity_score += genre_sim * 0.10
        weights_sum += 0.10
    
    # Instruments joués (profil musical)
    instr1 = set(user1_profile.get('user_instruments', []))
    instr2 = set(user2_profile.get('user_instruments', []))
    if instr1 or instr2:
        instr_sim = len(instr1 & instr2) / len(instr1 | instr2) if (instr1 | instr2) else 0
        similarity_score += instr_sim * 0.05
        weights_sum += 0.05
    
    # Contextes d'écoute (habitudes)
    ctx1 = set(user1_profile.get('listening_context', []))
    ctx2 = set(user2_profile.get('listening_context', []))
    if ctx1 or ctx2:
        ctx_sim = len(ctx1 & ctx2) / len(ctx1 | ctx2) if (ctx1 | ctx2) else 0
        similarity_score += ctx_sim * 0.05
        weights_sum += 0.05
    
    # Normaliser par la somme des poids utilisés
    if weights_sum > 0:
        return similarity_score / weights_sum
    return 0

def find_similar_users_by_profile(target_user_id, all_users_df, conn, similarity_threshold=0.3):
    """    
    Trouve les utilisateurs similaires en comparant leurs profils    
    Returns: Liste de (user_id, similarité) triée par similarité décroissante
    """
    target_profile = load_user_profile(target_user_id, conn)
    
    if not target_profile:
        print(f"Impossible de charger le profil de l'utilisateur {target_user_id}")
        return []
    
    similar_users = []
        
    for user_id in all_users_df["user_id"].unique():
        if user_id == target_user_id:
            continue
        
        user_id = int(user_id)
        user_profile = load_user_profile(user_id, conn)
        
        if not user_profile:
            continue
        
        # Calculer similarité de PROFIL (pas d'items)
        sim = similarity_user_profiles(target_profile, user_profile)
        
        if sim >= similarity_threshold:
            similar_users.append((user_id, sim))
    
    # Trier par similarité décroissante
    similar_users.sort(key=lambda x: x[1], reverse=True)
    
    return similar_users

def load_user_favorites(user_id, conn):
    """Charge les favoris d'un utilisateur (pour les recommandations finales)"""
    cursor = conn.cursor()
    
    cursor.execute("""SELECT track_id FROM sae5_6.ajoute_favori WHERE user_id = %s""", (user_id,))
    track_fav = cursor.fetchall()
    
    cursor.close()
    
    return {
        "tracks": [f[0] for f in track_fav if f[0] is not None]
    }

def recommend_based_on_similar_users(target_user_id, similar_users, conn, get_title=False, top_k=10):
    """    
    Maintenant qu'on a trouvé les utilisateurs similaires
    Retourne Top-k musiques pondérées par similarité de PROFIL
    """
    if not similar_users:
        return []
    
    # Charger les favoris de l'utilisateur cible
    target_favs = load_user_favorites(target_user_id, conn)
    target_fav_set = set(target_favs["tracks"])
    
    # Agréger les scores des pistes recommandées
    track_scores = Counter()
    
    for sim_user_id, similarity_score in similar_users:
        sim_user_favs = load_user_favorites(sim_user_id, conn)
        
        for track_id in sim_user_favs["tracks"]:
            if track_id not in target_fav_set:
                # Pondérer par la similarité de PROFIL (pas d'items)
                track_scores[track_id] += similarity_score
    
    # Obtenir les top-k recommandations
    recommendations = track_scores.most_common(top_k)
    
    # Ajouter les titres si demandé
    if get_title:
        cursor = conn.cursor()
        recommendations_with_titles = []
        for track_id, score in recommendations:
            cursor.execute("""
                SELECT a.track_title, t.artist_name 
                FROM sae5_6.track a 
                JOIN sae5_6.realiser r ON a.track_id = r.track_id 
                JOIN sae5_6.artist t ON r.artist_id = t.artist_id 
                WHERE a.track_id = %s
                LIMIT 1
            """, (track_id,))
            result = cursor.fetchone()
            track_title = result[0] if result else "Unknown Title"
            artist_name = result[1] if result else "Unknown Artist"
            recommendations_with_titles.append((track_id, track_title, artist_name, score))
        cursor.close()
        return recommendations_with_titles
    
    return recommendations

if __name__ == "__main__":
    conn = connection_db()
    
    # Charge tous les utilisateurs
    all_users_df = load.load_users()
    
    for user_id in all_users_df["user_id"].unique()[:5]:  # Tester sur 5 users
        target_user_id = int(user_id)
        
        print(f"Utilisateur {target_user_id}")
        
        # ÉTAPE 1 : Trouver des utilisateurs avec des PROFILS similaires
        similar_users = find_similar_users_by_profile(
            target_user_id, all_users_df, conn, similarity_threshold=0.3
        )
        
        print(f"Trouvé {len(similar_users)} utilisateurs avec profils similaires")
        if similar_users and len(similar_users) > 0:
            print(f"Top 3 User similaire : {similar_users[:3]}")
        
        # ÉTAPE 2 : Recommander basé sur ces utilisateurs similaires
        recommendations = recommend_based_on_similar_users(
            target_user_id, similar_users, conn, get_title=True, top_k=10
        )
        
        print(f"Top 10 recommandations:")
        for i, rec in enumerate(recommendations, 1):
            if len(rec) == 4:
                track_id, title, artist, score = rec
                print(f"{i:2d}. {title} - {artist} (score: {score:.2f})")
    
    conn.close()
