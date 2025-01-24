import os
from django.core.files.storage import Storage
from supabase import create_client, Client

class SupabaseStorage(Storage):
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        self.bucket = os.getenv("SUPABASE_BUCKET")
        self.client: Client = create_client(self.url, self.key)

    def _save(self, name, content):
        path = f"{self.bucket}/{name}"
        self.client.storage.from_(self.bucket).upload(path, content.read())
        return name

    def url(self, name):
        return f"{self.url}/storage/v1/object/public/{self.bucket}/{name}"

    def exists(self, name):
        path = f"{self.bucket}/{name}"
        response = self.client.storage.from_(self.bucket).list(path)
        return len(response) > 0