from database.db_client import supabase

def log_token_usage(user_id, gmail_id, tokens_used):
    supabase.table("token_logs").insert({
        "user_id": user_id,
        "gmail_id": gmail_id,
        "tokens_used": tokens_used
    }).execute()