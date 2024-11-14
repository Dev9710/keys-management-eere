import pandas as pd
from django.core.management.base import BaseCommand
from listings.models import User, Team  # Importer le modèle Team

class Command(BaseCommand):
    help = 'Importer les membres de l\'équipe à partir d\'un fichier Excel'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Chemin vers le fichier Excel contenant les membres de l\'équipe.')

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        data = pd.read_excel(excel_file)
        data.columns = data.columns.str.strip()

        for index, row in data.iterrows():
            # Récupérer le nom de l'équipe et le normaliser
            team_name = row['team'].strip() if pd.notna(row['team']) else None  # Suppression des espaces autour
            
            # Convertir en majuscules pour comparaison (ou minuscule, selon ce qui est stocké dans la base)
            if team_name:
                team_name = team_name.upper()  # Normaliser en majuscules pour correspondre à votre table

                print(f"Nom de l'équipe récupéré : '{team_name}'")  # Débogage

                try:
                    # Obtenir l'instance de l'équipe
                    team_instance = Team.objects.filter(name=team_name).first()
                except Team.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'L\'équipe "{team_name}" n\'existe pas. Cette entrée est ignorée.'))
                    continue  # Passer cette itération si l'équipe n'existe pas

                # Créer une instance de User
                user = User(
                    name=row['name'] if pd.notna(row['name']) else '',  # Par défaut, une chaîne vide
                    firstname=row['firstname'] if pd.notna(row['firstname']) else '',  # Par défaut, une chaîne vide
                    team=team_instance,  # Assigner l'instance de l'équipe
                    comment=row['comment'] if pd.notna(row['comment']) else ''  # Par défaut, une chaîne vide
                )
                user.save()
            else:
                self.stdout.write(self.style.WARNING(f'La ligne {index} n\'a pas d\'équipe spécifiée. Cette entrée est ignorée.'))

        self.stdout.write(self.style.SUCCESS('Les membres de l\'équipe ont été importés avec succès'))
