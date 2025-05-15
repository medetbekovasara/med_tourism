import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'med_tourism.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('✔️ Суперюзер создан: admin/admin')
else:
    print('⚠️ Суперюзер уже существует')
