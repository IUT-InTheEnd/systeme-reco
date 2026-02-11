use postgres::{Client, Error};
use crate::db_helper;

// ----- Colonnes -----
const columns: [&str; 22] = [
"user_id", "user_age", "user_job", "user_plays_music", "user_gender",
"user_instruments", "user_music_contexts", "profile_id", "music_envy_today",
"feeling", "music_preference", "music_style_preference", "music_reason",
"listening_context", "current_music_type", "usual_listening_mode",
"likes_discovery", "attend_live_concert", "repeat_listening", "explicit_ok",
"avg_song_length", "avg_daily_listen_time"
];

const numeric_cols: [&str; 12] = [
"user_age", "music_preference", "music_style_preference", "attend_live_concert",
"explicit_ok", "current_music_type", "repeat_listening",
"avg_daily_listen_time", "feeling", "usual_listening_mode", "likes_discovery",
"user_plays_music"
];

const categorical_cols: [&str; 3] = [
"user_job", "user_gender","avg_song_length",
];

const multilabel_cols: [&str; 7] = [
"user_instruments", "user_music_contexts", "listening_context", "music_reason",
"music_envy_today", "preference_language", "genres_favoris"
];

fn pull_data_user(mut client: Client) -> Result<(), Error> {
    let users_row = client.query("SELECT * FROM \"user\" u JOIN user_profile up ON u.profile_id = up.user_profile_id;", &[])?;

    let langs_row = client.query("SELECT up.user_id, l.language_label FROM user_parle up JOIN language l ON up.language_id = l.language_id", &[])?;
    Ok(())
}