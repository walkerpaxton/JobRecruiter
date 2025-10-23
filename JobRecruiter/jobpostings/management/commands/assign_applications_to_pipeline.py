from django.core.management.base import BaseCommand
from jobpostings.models import Application, PipelineStage


class Command(BaseCommand):
    help = 'Assign existing applications to the first pipeline stage'

    def handle(self, *args, **options):
        # Get the first pipeline stage (Applied)
        first_stage = PipelineStage.objects.filter(name='Applied').first()
        
        if not first_stage:
            self.stdout.write(
                self.style.ERROR('No "Applied" pipeline stage found. Please run create_default_pipeline_stages first.')
            )
            return
        
        # Get all applications without a pipeline stage
        unassigned_applications = Application.objects.filter(pipeline_stage__isnull=True)
        
        if not unassigned_applications.exists():
            self.stdout.write(
                self.style.SUCCESS('All applications already have pipeline stages assigned.')
            )
            return
        
        # Assign them to the first stage
        updated_count = unassigned_applications.update(pipeline_stage=first_stage)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully assigned {updated_count} applications to the "Applied" pipeline stage.')
        )
