import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'med_tourism.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('✔️ Суперюзер создан: admin/admin')
else:
    print('⚠️ Суперюзер уже существует')
    user = User.objects.get(username='admin')
    user.is_superuser = True
    user.is_staff = True
    user.set_password('admin')
    user.save()
    print('✅ Данные суперюзера обновлены')
