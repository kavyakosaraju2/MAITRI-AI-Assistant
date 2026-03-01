from database.db_client import supabase

response = supabase.table("users").select("*").execute()

print("Connected successfully!")
print(response.data)