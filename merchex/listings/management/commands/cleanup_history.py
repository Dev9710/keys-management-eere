from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from listings.models import ActionLog


class Command(BaseCommand):
    help = 'Nettoie l\'historique des actions anciennes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=getattr(settings, 'HISTORY_RETENTION_DAYS', 365),
            help='Nombre de jours à conserver (défaut: 365)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait supprimé sans le faire'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']

        cutoff_date = timezone.now() - timedelta(days=days)
        old_actions = ActionLog.objects.filter(timestamp__lt=cutoff_date)
        count = old_actions.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'Mode dry-run: {count} actions seraient supprimées')
            )
        else:
            old_actions.delete()
            self.stdout.write(
                self.style.SUCCESS(f'{count} actions anciennes supprimées')
            )

# Pour exécuter : python manage.py cleanup_history
# Pour voir ce qui serait supprimé : python manage.py cleanup_history --dry-run
