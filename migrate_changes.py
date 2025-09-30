import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# Make migrations for all installed apps.
call_command('makemigrations')

# Apply migrations for all apps
call_command('migrate')

print("All apps migrated successfully!")
