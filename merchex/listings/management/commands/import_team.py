import pandas as pd
from django.core.management.base import BaseCommand
from listings.models import Team  # Ajustez l'import en fonction de votre structure

class Command(BaseCommand):
    help = 'Import teams from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='training-django-env\merchex\listings\data\teams.xlsx')

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        data = pd.read_excel(excel_file)

        for index, row in data.iterrows():
            team = Team(
                name=row['name'] if pd.notna(row['name']) else '',  # Default to empty string
            )
            team.save()

        self.stdout.write(self.style.SUCCESS('Teams imported successfully'))
