from django.core.management.base import BaseCommand
from jobpostings.models import PipelineStage


class Command(BaseCommand):
    help = 'Create default pipeline stages for the hiring process'

    def handle(self, *args, **options):
        default_stages = [
            {
                'name': 'Applied',
                'description': 'Application received and under initial review',
                'color': '#3B82F6',  # Blue
                'order': 1,
                'is_final_positive': False,
                'is_final_negative': False,
            },
            {
                'name': 'Phone Screen',
                'description': 'Initial phone screening scheduled or completed',
                'color': '#8B5CF6',  # Purple
                'order': 2,
                'is_final_positive': False,
                'is_final_negative': False,
            },
            {
                'name': 'Technical Interview',
                'description': 'Technical skills assessment',
                'color': '#F59E0B',  # Amber
                'order': 3,
                'is_final_positive': False,
                'is_final_negative': False,
            },
            {
                'name': 'Final Interview',
                'description': 'Final interview with hiring manager/team',
                'color': '#EF4444',  # Red
                'order': 4,
                'is_final_positive': False,
                'is_final_negative': False,
            },
            {
                'name': 'Reference Check',
                'description': 'Checking references and background',
                'color': '#10B981',  # Emerald
                'order': 5,
                'is_final_positive': False,
                'is_final_negative': False,
            },
            {
                'name': 'Offer',
                'description': 'Job offer extended',
                'color': '#059669',  # Green
                'order': 6,
                'is_final_positive': True,
                'is_final_negative': False,
            },
            {
                'name': 'Hired',
                'description': 'Candidate accepted offer and started',
                'color': '#047857',  # Dark Green
                'order': 7,
                'is_final_positive': True,
                'is_final_negative': False,
            },
            {
                'name': 'Rejected',
                'description': 'Application rejected',
                'color': '#6B7280',  # Gray
                'order': 8,
                'is_final_positive': False,
                'is_final_negative': True,
            },
        ]

        created_count = 0
        for stage_data in default_stages:
            stage, created = PipelineStage.objects.get_or_create(
                name=stage_data['name'],
                defaults=stage_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created pipeline stage: {stage.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Pipeline stage already exists: {stage.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new pipeline stages')
        )
