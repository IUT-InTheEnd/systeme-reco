import reco_steph_echonest
import reco_user_based_p2
import load

def hybride_recommendation(track_id, n, compareGenre, target_user_id, get_title=False, top_k=10):
    conn = reco_user_based_p2.connection_db()
    all_users_df = load.load_users()

    # Charger les données des pistes
    tracks_df = load.load_tracks()

    # Trouver des utilisateurs similaires
    similar_users = reco_user_based_p2.find_similar_users_by_favorites(target_user_id, all_users_df, conn, similarity_threshold=0.1)

    # Obtenir des recommandations user-based
    recommendations_ub = reco_user_based_p2.recommend_based_on_similar_users(target_user_id, similar_users, tracks_df, get_title=True, top_k=top_k)

    # Obtenir des recommandations item-based
    recommendations_ib = reco_steph_echonest.echonest_recommend(target_user_id, track_id, n, compareGenre)

    conn.close()

    print("Recommandations user-based :")
    for rec in recommendations_ub:
        print(rec)

    print("Recommandations item-based :")
    for rec2 in recommendations_ib:
        print(rec2)

    recommendations = []

    # ---------- CAS 1 : pas de user-based ----------
    if len(recommendations_ub) == 0:
        for rec2 in recommendations_ib:
            recommendations.append(rec2[0])

    # ---------- CAS 2 : pas de item-based ----------
    elif len(recommendations_ib) == 0:
        for rec in recommendations_ub:
            recommendations.append(rec[0])

    # ---------- CAS 3 : assez de recommandations ----------
    elif len(recommendations_ub) + len(recommendations_ib) >= n:
        # Intersection
        for rec in recommendations_ub:
            for rec2 in recommendations_ib:
                if rec2[0] == rec[0]:
                    recommendations.append(rec[0])

        # Compléter si nécessaire
        if len(recommendations) < n:
            i = 0
            j = 0
            while len(recommendations) < n:
                if i < len(recommendations_ub):
                    if recommendations_ub[i][0] not in recommendations:
                        recommendations.append(recommendations_ub[i][0])
                if len(recommendations) < n and j < len(recommendations_ib):
                    if recommendations_ib[j][0] not in recommendations:
                        recommendations.append(recommendations_ib[j][0])
                i += 1
                j += 1

    # ---------- CAS 4 : pas assez de recommandations ----------
    else:
        # Intersection
        for rec in recommendations_ub:
            for rec2 in recommendations_ib:
                if rec2[0] == rec[0]:
                    recommendations.append(rec[0])

        # Compléter
        if len(recommendations) < n:
            i = 0
            j = 0
            while len(recommendations) < n:
                if i < len(recommendations_ub):
                    if recommendations_ub[i][0] not in recommendations:
                        recommendations.append(recommendations_ub[i][0])
                if len(recommendations) < n and j < len(recommendations_ib):
                    if recommendations_ib[j][0] not in recommendations:
                        recommendations.append(recommendations_ib[j][0])
                i += 1
                j += 1

        print("Pas assez de recommandations disponibles pour atteindre le nombre demandé.")

    return recommendations


# ---------- TEST ----------
simi = hybride_recommendation(156031, 10, True, 4, False, 10)

print("Recommandations hybrides :")
for rec in simi:
    print(rec)