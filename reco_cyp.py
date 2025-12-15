import psycopg2
import pandas as pd
import numpy as np
import ast
from collections import Counter

# ----- Connexion à la DB -----
def connection_db():
    return psycopg2.connect(
        dbname="InTheEnd_DB",
        user="InTheEnd_User",
        password="InTheEnd_Password",
        host="localhost",
        port="25000"
    )

# ----- Colonnes -----
columns = [
    "user_id", "user_age", "user_job", "user_plays_music", "user_gender",
    "user_instruments", "user_music_contexts", "profile_id", "music_envy_today",
    "feeling", "music_preference", "music_style_preference", "music_reason",
    "listening_context", "current_music_type", "usual_listening_mode",
    "likes_discovery", "attend_live_concert", "repeat_listening", "explicit_ok",
    "avg_song_length", "avg_daily_listen_time"
]

numeric_cols = [
    "user_age", "music_preference", "music_style_preference",
    "repeat_listening", "avg_song_length", "avg_daily_listen_time"
]

categorical_cols = [
    "user_job", "user_gender", "music_reason",
    "current_music_type", "usual_listening_mode",
    "likes_discovery", "attend_live_concert", "explicit_ok"
]

bool_cols = ["user_plays_music"]

multilabel_cols = [
    "user_instruments", "user_music_contexts",
    "feeling", "listening_context"
]

# ----- Fonction pour transformer les colonnes multi-label en listes -----
def ensure_list(x):
    if isinstance(x, list):
        return x
    elif isinstance(x, str) and x.startswith("["):
        return ast.literal_eval(x)
    elif x is None or (isinstance(x, float) and np.isnan(x)):
        return []
    else:
        return [x]

# ----- Fonction pour compléter un utilisateur peu rempli -----
def complete_user(new_user, df, numeric_cols, categorical_cols, bool_cols, multilabel_cols):
    user_completed = new_user.copy()

    def is_provided(v):
        if v is None: return False
        if isinstance(v, str): return v.strip() != ""
        if isinstance(v, (list, tuple, set)): return len(v) > 0
        if isinstance(v, float) and np.isnan(v): return False
        return True

    def norm_scalar(v):
        if v is None: return None
        if isinstance(v, float) and np.isnan(v): return None
        return str(v).strip().lower()

    def norm_numeric(v):
        try:
            return float(v)
        except Exception:
            return None

    def norm_bool(v):
        try:
            return int(v)
        except Exception:
            return None

    def norm_list(v):
        lst = ensure_list(v)
        return [str(x).strip().lower() for x in lst if x is not None and str(x).strip() != ""]


    # colonnes effectivement fournies
    provided = {k: v for k, v in user_completed.items() if k in df.columns and is_provided(v)}

    if len(provided) == 0:
        # new_user vide -> utiliser tous les utilisateurs pour le calcul
        print("[complete_user] new_user vide -> utilisation de tous les utilisateurs pour le calcul")
        filtered = df.copy()
    else:
        # WIP : faire un OR à 50%
        # user conservé s'il partage au moins une valeur avec new_user
        mask = pd.Series(False, index=df.index)

        for col, val in provided.items():
            if col in multilabel_cols:
                prov_set = set(norm_list(val))
                if len(prov_set) == 0:
                    continue
                ser = df[col].apply(lambda items: set(norm_list(items)))
                mask_col = ser.apply(lambda s: len(s & prov_set) > 0)
                mask |= mask_col.fillna(False)
            elif col in numeric_cols:
                num = norm_numeric(val)
                if num is None:
                    norm_val = norm_scalar(val)
                    mask_col = df[col].fillna("").astype(str).str.strip().str.lower() == norm_val
                else:
                    ser_num = pd.to_numeric(df[col], errors='coerce')
                    mask_col = ser_num.notna() & (np.isclose(ser_num, num))
                mask |= mask_col.fillna(False)
            elif col in bool_cols:
                b = norm_bool(val)
                if b is None:
                    mask_col = df[col].fillna("").astype(str).str.strip().str.lower() == norm_scalar(val)
                else:
                    ser_bool = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                    mask_col = (ser_bool == int(b))
                mask |= mask_col.fillna(False)
            else:
                norm_val = norm_scalar(val)
                mask_col = df[col].fillna("").astype(str).str.strip().str.lower() == norm_val
                mask |= mask_col.fillna(False)

        # --- DEBUG / LOG: nombre d'utilisateurs retenus + exemples (pour vérifier que ça marche) ---
        n_selected = int(mask.sum())
        total = len(df)
        print(f"[complete_user] utilisateurs retenus pour le calcul : {n_selected}/{total}")
        if n_selected > 0:
            # affiche jusqu'à 5 ids pour vérification
            if "user_id" in df.columns:
                print("[complete_user] exemples user_id retenus :", df.loc[mask, "user_id"].head(5).tolist())
            # pour chaque colonne multilabel fournie, affiche l'intersection moyenne / exemples
            for col in multilabel_cols:
                if col in provided:
                    prov_set = set(norm_list(provided[col]))
                    if prov_set:
                        inter_counts = df.loc[mask, col].apply(lambda items: len(set(norm_list(items)) & prov_set) if isinstance(items, (list, tuple, set)) else 0)
                        print(f"[complete_user] '{col}' intersections (sélection) — max:{int(inter_counts.max())}, mean:{float(inter_counts.mean()):.2f}")
        else:
            print("[complete_user] aucun utilisateur ne partage de valeur avec new_user -> fallback au dataset complet")

        filtered = df[mask].copy()
        # Tout est utilisé si aucun utilisateur ne correspond
        if filtered.shape[0] == 0:
            filtered = df
            
    # compléter uniquement les colonnes non fournies
    for col in numeric_cols:
        if col in user_completed and not is_provided(user_completed[col]):
            if col in filtered.columns and filtered[col].dropna().shape[0] > 0:
                user_completed[col] = filtered[col].mean()
            else:
                user_completed[col] = df[col].mean() if col in df.columns else 0

    for col in categorical_cols:
        if col in user_completed and not is_provided(user_completed[col]):
            if col in filtered.columns and filtered[col].dropna().shape[0] > 0:
                user_completed[col] = filtered[col].mode().iloc[0]
            else:
                user_completed[col] = df[col].mode().iloc[0] if col in df.columns and df[col].dropna().shape[0] > 0 else ""

    for col in bool_cols:
        if col in user_completed and not is_provided(user_completed[col]):
            if col in filtered.columns and filtered[col].dropna().shape[0] > 0:
                user_completed[col] = int(filtered[col].mode().iloc[0])
            else:
                user_completed[col] = int(df[col].mode().iloc[0]) if col in df.columns and df[col].dropna().shape[0] > 0 else 0

    TOP_K = 3
    for col in multilabel_cols:
        if col in user_completed:
            provided_items = user_completed.get(col)
            provided_items = ensure_list(provided_items)
            if is_provided(provided_items):
                user_completed[col] = provided_items
            else:
                counter = Counter()
                if col in filtered.columns:
                    for items in filtered[col]:
                        if isinstance(items, (list, tuple, set)):
                            counter.update(items)
                user_completed[col] = [item for item, _ in counter.most_common(TOP_K)]

    return user_completed

def main():
    conn = connection_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sae5_6.user u JOIN sae5_6.user_profile up ON u.profile_id = up.user_profile_id;")
    users = cursor.fetchall()

    cols_db = [desc[0] for desc in cursor.description]    # colonnes de la BDD
    cols_keep = [c for c in columns if c in cols_db]      # intersection dans l'ordre de `columns`
    idx_map = {c: cols_db.index(c) for c in cols_keep}    # position de chaque colonne dans `users`

    # Convertir en dictionnaires en ne gardant que les colonnes sélectionnées
    user_dicts = []
    for user in users:
        d = {k: user[idx_map[k]] for k in cols_keep}
        for col in multilabel_cols:
            if col in d:
                d[col] = ensure_list(d[col])
        user_dicts.append(d)
    
    df = pd.DataFrame(user_dicts)
    
    # Convertir les colonnes numériques en float (coerce les valeurs invalides en NaN)
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Nouvel utilisateur
    new_user = {
        "user_age": None,
        "user_job": "",
        "user_plays_music": None,
        "user_gender": "Femme",
        "user_instruments": [],
        "user_music_contexts": [],
        "music_envy_today": None,
        "feeling": [],
        "music_preference": None,
        "music_style_preference": None,
        "music_reason": "",
        "listening_context": [],
        "current_music_type": "",
        "usual_listening_mode": "",
        "likes_discovery": "",
        "attend_live_concert": "",
        "repeat_listening": None,
        "explicit_ok": "",
        "avg_song_length": None,
        "avg_daily_listen_time": None
    }
    
    completed_user = complete_user(new_user, df, numeric_cols, categorical_cols, bool_cols, multilabel_cols)
    
    # --- Transformer en DataFrame (une seule ligne) ---
    final_cols = cols_keep if 'cols_keep' in locals() else [c for c in columns if c in df.columns]
    completed_df = pd.DataFrame([completed_user], columns=final_cols)

    # caster les colonnes numériques
    for c in numeric_cols:
        if c in completed_df.columns:
            completed_df[c] = pd.to_numeric(completed_df[c], errors='coerce').fillna(0)

    # caster les booléens en int (0/1)
    for c in bool_cols:
        if c in completed_df.columns:
            completed_df[c] = completed_df[c].apply(lambda v: int(v) if (pd.notna(v) and v != "") else 0)

    # s'assurer que les colonnes multilabel contiennent des listes
    def to_list_cell(x):
        if isinstance(x, list):
            return x
        if isinstance(x, str) and x.startswith("["):
            try:
                return ast.literal_eval(x)
            except Exception:
                return [x]
        if pd.isna(x):
            return []
        return [x]

    for c in multilabel_cols:
        if c in completed_df.columns:
            completed_df[c] = completed_df[c].apply(to_list_cell)

    print("Completed user (DataFrame):")

    completed_df.drop(columns=["user_id", "profile_id"], errors='ignore', inplace=True)

    print(completed_df)

if __name__ == "__main__":
    main()
