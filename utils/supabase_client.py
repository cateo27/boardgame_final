import os
from supabase import create_client
from dotenv import load_dotenv


load_dotenv()

url = "https://ymwdvqmfblnewoiicpkk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inltd2R2cW1mYmxuZXdvaWljcGtrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk1OTQwNDUsImV4cCI6MjA4NTE3MDA0NX0.pYML1VPXRrehBlx6qnf9sWTrQ_gdiLLZ7FaQksLMpzY"

supabase = create_client(url, key)
