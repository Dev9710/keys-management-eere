# management/commands/check_key_consistency.py
from django.core.management.base import BaseCommand
from listings.models import KeyInstance, KeyAssignment

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Instances marquées non disponibles sans assignment
        orphan_instances = KeyInstance.objects.filter(
            is_available=False
        ).exclude(
            keyassignment__is_active=True
        )
        
        print(f"🔍 {orphan_instances.count()} instances orphelines trouvées")
        for instance in orphan_instances:
            print(f"   - Clé #{instance.key_type.number}: Instance {instance.id}")
            
        # Assignments actifs sur instances disponibles  
        ghost_assignments = KeyAssignment.objects.filter(
            is_active=True,
            key_instance__is_available=True
        )
        
        print(f"👻 {ghost_assignments.count()} assignments fantômes trouvées")
        for assignment in ghost_assignments:
            print(f"   - {assignment.user.firstname} {assignment.user.name}: "
                  f"Clé #{assignment.key_instance.key_type.number}")