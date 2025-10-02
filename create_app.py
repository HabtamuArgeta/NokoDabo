import os
import django

project_dir = os.path.dirname(os.path.abspath(__file__))
app_name = 'branches'

# ---- Step 1: Create app folder if it doesn't exist ----
app_path = os.path.join(project_dir, app_name)
if not os.path.exists(app_path):
    os.makedirs(app_path)
    print(f"Created app folder '{app_name}'")
else:
    print(f"App folder '{app_name}' already exists.")

# ---- Step 2: Create basic app files ----
files = ['__init__.py', 'admin.py', 'apps.py', 'models.py', 'views.py']
for f in files:
    file_path = os.path.join(app_path, f)
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            if f == 'apps.py':
                file.write(f"""from django.apps import AppConfig\n\nclass BakeryConfig(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = '{app_name}'\n""")
            else:
                file.write("")  # empty file
        print(f"Created {f}")
    else:
        print(f"{f} already exists")

# ---- Step 3: Add app to INSTALLED_APPS ----
settings_file = os.path.join(project_dir, 'NokoDabo', 'settings.py')
with open(settings_file, 'r') as file:
    content = file.read()

if f"'{app_name}'" not in content:
    # Insert before the last closing bracket of INSTALLED_APPS
    content = content.replace(
        'INSTALLED_APPS = [',
        f'INSTALLED_APPS = [\n    \'{app_name}\','
    )
    with open(settings_file, 'w') as file:
        file.write(content)
    print(f"Added '{app_name}' to INSTALLED_APPS")
else:
    print(f"'{app_name}' already in INSTALLED_APPS")

# ---- Step 4: Setup Django environment to run migrations ----
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NokoDabo.settings')
django.setup()

from django.core.management import call_command

# ---- Step 5: Make migrations and migrate ----
call_command('makemigrations', app_name)
call_command('migrate')

print("App creation and migration completed!")
