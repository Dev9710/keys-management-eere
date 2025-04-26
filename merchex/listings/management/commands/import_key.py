import pandas as pd
from django.db import transaction
from django.core.management.base import BaseCommand
from listings.models import KeyType, KeyInstance


class Command(BaseCommand):
    help = 'Importe les données des clés depuis un fichier Excel'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str,
                            help='Chemin vers le fichier Excel')

    def handle(self, *args, **options):
        file_path = options['excel_file']
        self.stdout.write(self.style.SUCCESS(
            f'Importation depuis {file_path}'))

        try:
            # Lire le fichier Excel
            df = pd.read_excel(file_path)

            # Afficher un aperçu des données
            self.stdout.write(f"Colonnes trouvées: {', '.join(df.columns)}")
            self.stdout.write(f"Nombre total de lignes: {len(df)}")

            # Valider la présence des colonnes requises
            required_columns = ['number', 'name', 'place', 'nb_total_key',
                                'nb_attributed_key', 'in_cabinet', 'in_safe']
            missing_columns = [
                col for col in required_columns if col not in df.columns]

            if missing_columns:
                self.stdout.write(self.style.ERROR(
                    f"Colonnes manquantes: {', '.join(missing_columns)}"
                ))
                return

            # Effectuer l'importation dans une transaction pour garantir l'intégrité
            with transaction.atomic():
                # Garder une trace des clés importées
                created_types = 0
                created_instances = 0
                warnings = 0

                for _, row in df.iterrows():
                    # Extraire et nettoyer les données
                    number = int(row['number']) if pd.notna(
                        row['number']) else 0
                    name = str(row['name']) if pd.notna(row['name']) else ''
                    place = str(row['place']) if pd.notna(row['place']) else ''
                    comments = str(row['comments']) if 'comments' in row and pd.notna(
                        row['comments']) else ''

                    total_quantity = int(row['nb_total_key']) if pd.notna(
                        row['nb_total_key']) else 0
                    attributed_keys = int(row['nb_attributed_key']) if pd.notna(
                        row['nb_attributed_key']) else 0
                    in_cabinet = int(row['in_cabinet']) if pd.notna(
                        row['in_cabinet']) else 0
                    in_safe = int(row['in_safe']) if pd.notna(
                        row['in_safe']) else 0

                    # Vérifier la cohérence des données
                    calculated_total = attributed_keys + in_cabinet + in_safe
                    if calculated_total != total_quantity:
                        self.stdout.write(self.style.WARNING(
                            f"Attention pour la clé {number}: "
                            f"La somme des exemplaires ({calculated_total}) ne correspond pas "
                            f"au total déclaré ({total_quantity}). "
                            f"Attribués: {attributed_keys}, Armoire: {in_cabinet}, Coffre: {in_safe}"
                        ))
                        warnings += 1
                        total_quantity = calculated_total  # Ajuster le total pour qu'il soit cohérent

                    # Créer ou mettre à jour le type de clé
                    key_type, created = KeyType.objects.update_or_create(
                        number=number,
                        defaults={
                            'name': name,
                            'place': place,
                            'total_quantity': total_quantity,
                            'in_cabinet': in_cabinet,
                            'in_safe': in_safe,
                            'comments': comments
                        }
                    )

                    if created:
                        created_types += 1
                        self.stdout.write(
                            f"Créé type de clé: {number} - {name}")
                    else:
                        # Si le type de clé existe déjà, supprimer les instances existantes
                        instance_count = KeyInstance.objects.filter(
                            key_type=key_type).count()
                        self.stdout.write(
                            f"Mis à jour type de clé: {number} - {name} (suppression de {instance_count} instances)")
                        KeyInstance.objects.filter(key_type=key_type).delete()

                    # 1. Créer les instances attribuées (non disponibles)
                    attributed_instances = []
                    for i in range(attributed_keys):
                        attributed_instances.append(
                            KeyInstance(
                                key_type=key_type,
                                is_available=False,  # Non disponible car déjà attribuée
                                condition='Bon',
                                location='Utilisateur'  # Localisation chez un utilisateur
                            )
                        )

                    # 2. Créer les instances dans l'armoire
                    cabinet_instances = []
                    for i in range(in_cabinet):
                        cabinet_instances.append(
                            KeyInstance(
                                key_type=key_type,
                                is_available=True,  # Disponible
                                condition='Bon',
                                location='Cabinet'  # Localisation dans l'armoire
                            )
                        )

                    # 3. Créer les instances dans le coffre
                    safe_instances = []
                    for i in range(in_safe):
                        safe_instances.append(
                            KeyInstance(
                                key_type=key_type,
                                is_available=True,  # Disponible
                                condition='Bon',
                                location='Coffre'  # Localisation dans le coffre
                            )
                        )

                    # Création en masse des instances
                    instances_created = 0
                    if attributed_instances:
                        KeyInstance.objects.bulk_create(attributed_instances)
                        instances_created += len(attributed_instances)

                    if cabinet_instances:
                        KeyInstance.objects.bulk_create(cabinet_instances)
                        instances_created += len(cabinet_instances)

                    if safe_instances:
                        KeyInstance.objects.bulk_create(safe_instances)
                        instances_created += len(safe_instances)

                    created_instances += instances_created
                    self.stdout.write(
                        f"   Créé {instances_created} instances de clé")

                # Résumé de l'importation
                success_message = (
                    f"Importation terminée avec succès: \n"
                    f"- {created_types} types de clés créés ou mis à jour\n"
                    f"- {created_instances} instances de clés créées\n"
                )

                if warnings > 0:
                    success_message += f"- {warnings} avertissements (incohérences de quantités)\n"

                self.stdout.write(self.style.SUCCESS(success_message))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Erreur lors de l'importation: {str(e)}"))
