import psycopg2
import pandas as pd

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
    df = df.loc[:, ~df.columns.duplicated()].copy()

    cur.close()
    conn.close()
    return df


def load_realiser():
    conn = connection_db()
    cur = conn.cursor()
    cur.execute("SELECT * from sae5_6.realiser JOIN sae5_6.artist ON sae5_6.realiser.artist_id = sae5_6.artist.artist_id JOIN sae5_6.track on sae5_6.track.track_id =  sae5_6.realiser.track_id ")
    data = cur.fetchall()
    columns = [desc[0] for desc in cur.description]  
    df = pd.DataFrame(data, columns=columns)
    df.columns = df.columns.map(lambda x: "_".join(x) if isinstance(x, tuple) else x)
    df = df.loc[:, ~df.columns.duplicated()].copy()
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
