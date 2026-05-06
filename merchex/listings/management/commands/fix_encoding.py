from django.core.management.base import BaseCommand
from django.db import transaction
from listings.models import KeyType


def fix_mojibake(text):
    """Corrige le Mojibake : octets UTF-8 interprétés comme Latin-1."""
    if not text:
        return text
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text


class Command(BaseCommand):
    help = "Corrige l'encodage des champs 'place' et 'comments' de KeyType (Mojibake UTF-8 -> Latin-1)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les corrections sans les appliquer',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        fixed = 0
        unchanged = 0

        keys = list(KeyType.objects.all())
        self.stdout.write(f"{len(keys)} types de cles a verifier...")

        try:
            with transaction.atomic():
                for key in keys:
                    changed = False

                    new_place = fix_mojibake(key.place)
                    new_comments = fix_mojibake(key.comments)

                    if new_place != key.place:
                        self.stdout.write(
                            f"  Cle {key.number} - place:    {key.place!r} -> {new_place!r}"
                        )
                        changed = True

                    if new_comments != key.comments:
                        self.stdout.write(
                            f"  Cle {key.number} - comments: {key.comments!r} -> {new_comments!r}"
                        )
                        changed = True

                    if changed:
                        fixed += 1
                        if not dry_run:
                            KeyType.objects.filter(pk=key.pk).update(
                                place=new_place,
                                comments=new_comments,
                            )
                    else:
                        unchanged += 1

                if dry_run:
                    raise Exception("dry-run: aucune modification appliquee")

        except Exception as e:
            if dry_run:
                self.stdout.write(self.style.WARNING(
                    f"\n[DRY-RUN] {fixed} enregistrement(s) a corriger, "
                    f"{unchanged} inchange(s). Aucune modification appliquee."
                ))
            else:
                self.stdout.write(self.style.ERROR(f"Erreur: {e}"))
            return

        self.stdout.write(self.style.SUCCESS(
            f"\n{fixed} enregistrement(s) corrige(s), {unchanged} inchange(s)."
        ))
