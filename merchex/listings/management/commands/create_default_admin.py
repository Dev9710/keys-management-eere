from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Crée un administrateur par défaut dans la base de données'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la réinitialisation du mot de passe si l\'administrateur existe déjà',
        )

    def handle(self, *args, **options):
        admin_username = 'admin'
        admin_email = 'admin@eere.org'
        admin_password = 'AdminEERE2025!'

        User = get_user_model()

        # Vérifier si l'administrateur existe déjà
        try:
            admin = User.objects.get(username=admin_username)
            if options['force']:
                admin.set_password(admin_password)
                admin.save()
                self.stdout.write(self.style.SUCCESS(
                    f'Mot de passe réinitialisé pour l\'administrateur: {admin_username}'))
            else:
                self.stdout.write(self.style.WARNING(
                    f'L\'administrateur {admin_username} existe déjà. Utilisez --force pour réinitialiser le mot de passe.'))
        except User.DoesNotExist:
            # Créer un nouvel administrateur
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                first_name='Administrateur',
                last_name='Système',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS(
                f'Administrateur créé avec succès: {admin_username}'))

        # Afficher les informations de connexion
        self.stdout.write(self.style.SUCCESS('Informations de connexion:'))
        self.stdout.write(f'Username: {admin_username}')
        self.stdout.write(f'Password: {admin_password}')
        self.stdout.write(f'Email: {admin_email}')
