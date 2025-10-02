import os
import django
from django.core.management import call_command

# ---- Step 1: Define project root ----
# Adjust this if manage.py is in a different location
project_root = os.path.dirname(os.path.abspath(__file__))

# Change working directory to project root
os.chdir(project_root)
print(f"📂 Changed directory to: {project_root}")

# ---- Step 2: Setup Django environment ----
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "NokoDabo.settings")
django.setup()

# ---- Step 3: Run makemigrations for all apps ----
print("📌 Making migrations for all apps...")
call_command("makemigrations")

# ---- Step 4: Apply migrations ----
print("📌 Applying migrations...")
call_command("migrate")

print("✅ All migrations applied successfully!")