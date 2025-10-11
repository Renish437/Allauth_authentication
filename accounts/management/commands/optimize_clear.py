# accounts/management/commands/optimize_clear.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
import subprocess

class Command(BaseCommand):
    help = 'Clear cache, pyc files, and rebuild static files.'

    def handle(self, *args, **options):
        self.stdout.write('🧹 Clearing cache...')
        cache.clear()

        self.stdout.write('🧽 Removing __pycache__ and .pyc files...')
        subprocess.call("find . -name '*.pyc' -delete", shell=True)
        subprocess.call("find . -name '__pycache__' -type d -exec rm -r {} +", shell=True)

        self.stdout.write('📦 Collecting static files...')
        subprocess.call("python manage.py collectstatic --noinput", shell=True)

        self.stdout.write(self.style.SUCCESS('✅ Optimization and cleanup complete!'))
