# Interface pour la démo de chaque algorithme de recommandation
import psycopg2
import load
import reco_user_based_p1
import reco_user_based_p2


def connection_db():
    return psycopg2.connect(
        dbname="InTheEnd_DB",
        user="InTheEnd_User",
        password="InTheEnd_Password",
        host="localhost",
        port="25000"
    )

def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "="*60)
    print("SYSTÈME DE RECOMMANDATION MUSICALE - MENU PRINCIPAL")
    print("="*60)
    print("\n[1] Recommandation User-Based (Part 1 - Profil utilisateur)")
    print("[2] Recommandation User-Based (Part 2 - Favoris)")
    print("[0] Quitter")
    print("-"*60)

def test_user_based_p1(conn):
    """Test de l'algorithme user-based basé sur le profil"""
    print("\n" + "="*60)
    print("RECOMMANDATION USER-BASED - PART 1 (Profil)")
    print("="*60)
    
    user_id = input("\nEntrez l'ID de l'utilisateur: ")
    try:
        user_id = int(user_id)
    except ValueError:
        print("ID invalide!")
        return

def test_user_based_p2(conn):
    """Test de l'algorithme user-based basé sur les favoris"""
    print("\n" + "="*60)
    print("RECOMMANDATION USER-BASED - PART 2 (Favoris)")
    print("="*60)
    
    user_id = input("\nEntrez l'ID de l'utilisateur: ")
    try:
        user_id = int(user_id)
    except ValueError:
        print("ID invalide!")
        return
    
    top_k = input("Nombre de recommandations (défaut: 10): ")
    top_k = int(top_k) if top_k else 10
    
    threshold = input("Seuil de similarité (défaut: 0.1): ")
    threshold = float(threshold) if threshold else 0.1
    
    print(f"\n🔍 Recherche d'utilisateurs similaires pour l'utilisateur {user_id}...")
    
    try:
        # Charger les données
        all_users_df = load.load_users()
        tracks_df = load.load_tracks()
        
        # Trouver des utilisateurs similaires
        similar_users = reco_user_based_p2.find_similar_users_by_favorites(
            user_id, all_users_df, conn, similarity_threshold=threshold
        )
        
        if not similar_users:
            print(f"Aucun utilisateur similaire trouvé (peut-être que l'utilisateur n'a pas de favoris)")
            return
        
        print(f"{len(similar_users)} utilisateurs similaires trouvés")
        
        # Obtenir des recommandations
        recommendations = reco_user_based_p2.recommend_based_on_similar_users(
            user_id, similar_users, tracks_df, get_title=True, top_k=top_k
        )
        
        if not recommendations:
            print("Aucune recommandation disponible")
            return
        
        print(f"\nTop {len(recommendations)} recommandations:")
        print("-"*60)
        for i, (track_id, track_title, artist_name, score) in enumerate(recommendations, 1):
            print(f"{i}. [{track_id}] {track_title} - {artist_name} | Score: {score:.4f}")
        
    except Exception as e:
        print(f"Erreur: {e}")


def main():
    """Fonction principale"""
    conn = connection_db()
    
    print("\nBienvenue dans le système de recommandation musicale!")
    
    while True:
        afficher_menu()
        choix = input("\nChoisissez une option: ")
        
        if choix == "1":
            test_user_based_p1(conn)
        elif choix == "2":
            test_user_based_p2(conn)
        elif choix == "0":
            print("\nAu revoir!")
            break
        else:
            print("\nOption invalide!")
        
        input("\nAppuyez sur Entrée pour continuer...")
    
    conn.close()

if __name__ == "__main__":
    main()
