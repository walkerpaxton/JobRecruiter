"""
Management command to export data to CSV for reporting purposes.
Usage:
    python manage.py export_data --type users --output users.csv
    python manage.py export_data --type job_postings --output jobs.csv
    python manage.py export_data --type applications --output applications.csv
    python manage.py export_data --type messages --output messages.csv
    python manage.py export_data --type all --output all_data.zip
"""
import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile, JobSeekerProfile, EmployerProfile
from jobpostings.models import JobPosting, Application
from messaging.models import Message, EmailMessage, Conversation


class Command(BaseCommand):
    help = 'Export data to CSV files for reporting purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['users', 'job_postings', 'applications', 'messages', 'all'],
            default='all',
            help='Type of data to export'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (optional, defaults to type_timestamp.csv)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='exports',
            help='Directory to save export files (default: exports)'
        )

    def handle(self, *args, **options):
        export_type = options['type']
        output_dir = options['output_dir']
        output_file = options.get('output')

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        if export_type == 'all':
            self.export_all(output_dir)
        elif export_type == 'users':
            self.export_users(output_dir, output_file)
        elif export_type == 'job_postings':
            self.export_job_postings(output_dir, output_file)
        elif export_type == 'applications':
            self.export_applications(output_dir, output_file)
        elif export_type == 'messages':
            self.export_messages(output_dir, output_file)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {export_type} data to {output_dir}/')
        )

    def export_all(self, output_dir):
        """Export all data types"""
        self.export_users(output_dir)
        self.export_job_postings(output_dir)
        self.export_applications(output_dir)
        self.export_messages(output_dir)
        self.stdout.write(self.style.SUCCESS('All data exported successfully!'))

    def export_users(self, output_dir, output_file=None):
        """Export user and profile data"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'users_{timestamp}.csv'

        filepath = os.path.join(output_dir, output_file)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'User ID', 'Username', 'Email', 'First Name', 'Last Name',
                'Account Type', 'Date Joined', 'Last Login',
                'Full Name', 'Preferred Name', 'Phone', 'City', 'State',
                'LinkedIn', 'Company Name', 'Company Website', 'Industry',
                'Company Size', 'Created At', 'Updated At'
            ])

            # Write data
            users = User.objects.all().select_related('profile').prefetch_related(
                'profile__jobseekerprofile', 'profile__employerprofile'
            )
            
            for user in users:
                try:
                    profile = user.profile
                    account_type = profile.account_type
                    
                    # Get jobseeker or employer profile data
                    full_name = ''
                    preferred_name = ''
                    phone = ''
                    city = ''
                    state = ''
                    linkedin = ''
                    company_name = ''
                    company_website = ''
                    industry = ''
                    company_size = ''
                    
                    if account_type == 'jobseeker':
                        try:
                            js_profile = profile.jobseekerprofile
                            full_name = js_profile.full_name or ''
                            preferred_name = js_profile.preferred_name or ''
                            phone = js_profile.phone or ''
                            city = js_profile.city or ''
                            state = js_profile.state or ''
                            linkedin = js_profile.linkedin or ''
                        except JobSeekerProfile.DoesNotExist:
                            pass
                    elif account_type == 'employer':
                        try:
                            emp_profile = profile.employerprofile
                            company_name = emp_profile.company_name or ''
                            company_website = emp_profile.company_website or ''
                            industry = emp_profile.industry or ''
                            company_size = emp_profile.company_size or ''
                        except EmployerProfile.DoesNotExist:
                            pass
                    
                    writer.writerow([
                        user.id,
                        user.username,
                        user.email or '',
                        user.first_name or '',
                        user.last_name or '',
                        account_type,
                        user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else '',
                        user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
                        full_name,
                        preferred_name,
                        phone,
                        city,
                        state,
                        linkedin,
                        company_name,
                        company_website,
                        industry,
                        company_size,
                        profile.created_at.strftime('%Y-%m-%d %H:%M:%S') if profile.created_at else '',
                        profile.updated_at.strftime('%Y-%m-%d %H:%M:%S') if profile.updated_at else '',
                    ])
                except Profile.DoesNotExist:
                    # User without profile
                    writer.writerow([
                        user.id,
                        user.username,
                        user.email or '',
                        user.first_name or '',
                        user.last_name or '',
                        'No Profile',
                        user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else '',
                        user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
                        '', '', '', '', '', '', '', '', '', '', ''
                    ])

        self.stdout.write(self.style.SUCCESS(f'Exported {users.count()} users to {filepath}'))

    def export_job_postings(self, output_dir, output_file=None):
        """Export job postings data"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'job_postings_{timestamp}.csv'

        filepath = os.path.join(output_dir, output_file)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'ID', 'Title', 'Company Name', 'City', 'State', 'Address',
                'Pay Min', 'Pay Max', 'Currency', 'Employment Type',
                'Description', 'Benefits', 'Application URL', 'Application Email',
                'Posted By', 'Created At', 'Updated At', 'Is Active',
                'Total Applications'
            ])

            # Write data
            jobs = JobPosting.objects.all().select_related('posted_by').prefetch_related('applications')
            
            for job in jobs:
                writer.writerow([
                    job.id,
                    job.title,
                    job.company_name,
                    job.city,
                    job.state,
                    job.address or '',
                    job.pay_min or '',
                    job.pay_max or '',
                    job.currency,
                    job.get_employment_type_display(),
                    job.description[:500] + '...' if len(job.description) > 500 else job.description,
                    job.benefits[:500] + '...' if len(job.benefits) > 500 else (job.benefits or ''),
                    job.application_url or '',
                    job.application_email or '',
                    job.posted_by.username if job.posted_by else '',
                    job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    job.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'Yes' if job.is_active else 'No',
                    job.applications.count()
                ])

        self.stdout.write(self.style.SUCCESS(f'Exported {jobs.count()} job postings to {filepath}'))

    def export_applications(self, output_dir, output_file=None):
        """Export applications data"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'applications_{timestamp}.csv'

        filepath = os.path.join(output_dir, output_file)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'ID', 'Job Title', 'Company Name', 'Applicant Username', 'Applicant Email',
                'Applicant Name', 'Status', 'Pipeline Stage', 'Cover Letter',
                'Notes', 'Applied At', 'Updated At', 'Stage Updated At'
            ])

            # Write data
            applications = Application.objects.all().select_related(
                'job_posting', 'applicant', 'pipeline_stage'
            )
            
            for app in applications:
                applicant_name = app.get_applicant_name()
                writer.writerow([
                    app.id,
                    app.job_posting.title,
                    app.job_posting.company_name,
                    app.applicant.username,
                    app.get_applicant_email() or '',
                    applicant_name,
                    app.get_status_display(),
                    app.pipeline_stage.name if app.pipeline_stage else '',
                    app.cover_letter[:500] + '...' if len(app.cover_letter) > 500 else app.cover_letter,
                    app.notes[:500] + '...' if len(app.notes) > 500 else (app.notes or ''),
                    app.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
                    app.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    app.stage_updated_at.strftime('%Y-%m-%d %H:%M:%S') if app.stage_updated_at else '',
                ])

        self.stdout.write(self.style.SUCCESS(f'Exported {applications.count()} applications to {filepath}'))

    def export_messages(self, output_dir, output_file=None):
        """Export messages and email data"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f'messages_{timestamp}.csv'

        filepath = os.path.join(output_dir, output_file)

        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'Type', 'ID', 'Sender', 'Recipient', 'Subject/Content Preview',
                'Status', 'Is Read', 'Created At', 'Sent At'
            ])

            # Export EmailMessages
            emails = EmailMessage.objects.all().select_related('sender', 'recipient')
            for email in emails:
                writer.writerow([
                    'Email',
                    email.id,
                    email.sender.username,
                    email.recipient.username,
                    email.subject[:100],
                    email.get_status_display(),
                    'Yes' if email.is_read else 'No',
                    email.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    email.sent_at.strftime('%Y-%m-%d %H:%M:%S') if email.sent_at else '',
                ])

            # Export Messages (from conversations)
            messages = Message.objects.all().select_related('sender', 'conversation')
            for msg in messages:
                # Get recipient from conversation
                recipient = msg.conversation.get_other_participant(msg.sender)
                recipient_username = recipient.username if recipient else 'Unknown'
                
                writer.writerow([
                    'Message',
                    msg.id,
                    msg.sender.username,
                    recipient_username,
                    msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
                    'Sent',
                    'Yes' if msg.is_read else 'No',
                    msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    '',
                ])

        total_count = EmailMessage.objects.count() + Message.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Exported {total_count} messages to {filepath}'))

