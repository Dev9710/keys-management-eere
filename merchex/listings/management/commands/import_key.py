import pandas as pd
from django.core.management.base import BaseCommand
from listings.models import Key  # Ajustez l'import en fonction de votre structure

class Command(BaseCommand):
    help = 'Import keys from an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='training-django-env\merchex\listings\data\keys.xlsx')

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        data = pd.read_excel(excel_file)

        for index, row in data.iterrows():
            key = Key(
                number=row['number'] if pd.notna(row['number']) else None,  # Default to None for integers
                name=row['name'] if pd.notna(row['name']) else '',  # Default to empty string
                place=row['place'] if pd.notna(row['place']) else '',  # Default to empty string
                initial_key_number=row['initial_key_number'] if pd.notna(row['initial_key_number']) else None,  # Default to None
                key_used=row['key_used'] if pd.notna(row['key_used']) else None,  # Default to None
                key_available=row['key_available'] if pd.notna(row['key_available']) else None,  # Default to None
                in_cabinet=(row['in_cabinet'] in [True, 1, 'TRUE', 'true', '1']) if pd.notna(row['in_cabinet']) else False,  # Default to False
                in_safe=(row['in_safe'] in [True, 1, 'TRUE', 'true', '1']) if pd.notna(row['in_safe']) else False,  # Default to False
                comments=row['comments'] if pd.notna(row['comments']) else ''  # Default to empty string
            )
            key.save()

        self.stdout.write(self.style.SUCCESS('Keys imported successfully'))
