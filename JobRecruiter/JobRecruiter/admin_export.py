"""
Custom admin view for exporting all data to CSV
"""
import csv
import zipfile
import io
from datetime import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.auth.models import User
from accounts.models import Profile, JobSeekerProfile, EmployerProfile, SavedSearch
from jobpostings.models import JobPosting, Application, PipelineStage
from messaging.models import Message, EmailMessage, Conversation, MessageNotification


def export_all_data_view(request):
    """
    Export all application data to CSV files in a zip archive.
    """
    if not request.user.is_staff:
        return HttpResponse('Unauthorized', status=403)
    
    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Export Users
        users_csv = io.StringIO()
        writer = csv.writer(users_csv)
        writer.writerow(['ID', 'Username', 'Email', 'First Name', 'Last Name', 'Date Joined', 'Last Login', 'Is Staff', 'Is Active'])
        for user in User.objects.all():
            writer.writerow([
                user.id,
                user.username,
                user.email or '',
                user.first_name or '',
                user.last_name or '',
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else '',
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
                'Yes' if user.is_staff else 'No',
                'Yes' if user.is_active else 'No',
            ])
        zip_file.writestr(f'users_{timestamp}.csv', users_csv.getvalue())
        
        # Export Profiles
        profiles_csv = io.StringIO()
        writer = csv.writer(profiles_csv)
        writer.writerow(['ID', 'User', 'Account Type', 'Created At', 'Updated At'])
        for profile in Profile.objects.all():
            writer.writerow([
                profile.id,
                profile.user.username,
                profile.account_type,
                profile.created_at.strftime('%Y-%m-%d %H:%M:%S') if profile.created_at else '',
                profile.updated_at.strftime('%Y-%m-%d %H:%M:%S') if profile.updated_at else '',
            ])
        zip_file.writestr(f'profiles_{timestamp}.csv', profiles_csv.getvalue())
        
        # Export Job Seeker Profiles
        jobseekers_csv = io.StringIO()
        writer = csv.writer(jobseekers_csv)
        writer.writerow(['Profile ID', 'User', 'Full Name', 'Preferred Name', 'City', 'State', 'Phone', 'LinkedIn', 'Technical Skills', 'Soft Skills'])
        for profile in JobSeekerProfile.objects.all().select_related('profile', 'profile__user'):
            writer.writerow([
                profile.profile.id,
                profile.profile.user.username,
                profile.full_name or '',
                profile.preferred_name or '',
                profile.city or '',
                profile.state or '',
                profile.phone or '',
                profile.linkedin or '',
                profile.technical_skills or '',
                profile.soft_skills or '',
            ])
        zip_file.writestr(f'jobseekers_{timestamp}.csv', jobseekers_csv.getvalue())
        
        # Export Employer Profiles
        employers_csv = io.StringIO()
        writer = csv.writer(employers_csv)
        writer.writerow(['Profile ID', 'User', 'Company Name', 'Company Website', 'Location', 'Industry', 'Company Size'])
        for profile in EmployerProfile.objects.all().select_related('profile', 'profile__user'):
            writer.writerow([
                profile.profile.id,
                profile.profile.user.username,
                profile.company_name or '',
                profile.company_website or '',
                profile.location or '',
                profile.industry or '',
                profile.company_size or '',
            ])
        zip_file.writestr(f'employers_{timestamp}.csv', employers_csv.getvalue())
        
        # Export Job Postings
        jobs_csv = io.StringIO()
        writer = csv.writer(jobs_csv)
        writer.writerow(['ID', 'Title', 'Company Name', 'City', 'State', 'Address', 'Pay Min', 'Pay Max', 'Currency', 'Employment Type', 'Is Active', 'Posted By', 'Created At', 'Required Skills'])
        for job in JobPosting.objects.all().select_related('posted_by'):
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
                job.employment_type,
                'Yes' if job.is_active else 'No',
                job.posted_by.username if job.posted_by else '',
                job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                job.required_skills or '',
            ])
        zip_file.writestr(f'job_postings_{timestamp}.csv', jobs_csv.getvalue())
        
        # Export Applications
        applications_csv = io.StringIO()
        writer = csv.writer(applications_csv)
        writer.writerow(['ID', 'Job Title', 'Company', 'Applicant', 'Applicant Email', 'Status', 'Pipeline Stage', 'Applied At'])
        for app in Application.objects.all().select_related('job_posting', 'applicant', 'pipeline_stage'):
            writer.writerow([
                app.id,
                app.job_posting.title,
                app.job_posting.company_name,
                app.applicant.username,
                app.applicant.email or '',
                app.status,
                app.pipeline_stage.name if app.pipeline_stage else '',
                app.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        zip_file.writestr(f'applications_{timestamp}.csv', applications_csv.getvalue())
        
        # Export Pipeline Stages
        stages_csv = io.StringIO()
        writer = csv.writer(stages_csv)
        writer.writerow(['ID', 'Name', 'Description', 'Order', 'Color', 'Is Final Positive', 'Is Final Negative', 'Created At'])
        for stage in PipelineStage.objects.all():
            writer.writerow([
                stage.id,
                stage.name,
                stage.description or '',
                stage.order,
                stage.color,
                'Yes' if stage.is_final_positive else 'No',
                'Yes' if stage.is_final_negative else 'No',
                stage.created_at.strftime('%Y-%m-%d %H:%M:%S') if stage.created_at else '',
            ])
        zip_file.writestr(f'pipeline_stages_{timestamp}.csv', stages_csv.getvalue())
        
        # Export Email Messages
        emails_csv = io.StringIO()
        writer = csv.writer(emails_csv)
        writer.writerow(['ID', 'Sender', 'Recipient', 'Subject', 'Status', 'Is Read', 'Created At', 'Sent At'])
        for email in EmailMessage.objects.all().select_related('sender', 'recipient'):
            writer.writerow([
                email.id,
                email.sender.username,
                email.recipient.username,
                email.subject,
                email.status,
                'Yes' if email.is_read else 'No',
                email.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                email.sent_at.strftime('%Y-%m-%d %H:%M:%S') if email.sent_at else '',
            ])
        zip_file.writestr(f'email_messages_{timestamp}.csv', emails_csv.getvalue())
        
        # Export Messages
        messages_csv = io.StringIO()
        writer = csv.writer(messages_csv)
        writer.writerow(['ID', 'Sender', 'Content Preview', 'Is Read', 'Timestamp'])
        for msg in Message.objects.all().select_related('sender', 'conversation'):
            writer.writerow([
                msg.id,
                msg.sender.username,
                msg.content[:100] + '...' if len(msg.content) > 100 else msg.content,
                'Yes' if msg.is_read else 'No',
                msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        zip_file.writestr(f'messages_{timestamp}.csv', messages_csv.getvalue())
        
        # Export Conversations
        conversations_csv = io.StringIO()
        writer = csv.writer(conversations_csv)
        writer.writerow(['ID', 'Participants', 'Created At', 'Updated At'])
        for conv in Conversation.objects.all().prefetch_related('participants'):
            participants = ', '.join([p.username for p in conv.participants.all()])
            writer.writerow([
                conv.id,
                participants,
                conv.created_at.strftime('%Y-%m-%d %H:%M:%S') if conv.created_at else '',
                conv.updated_at.strftime('%Y-%m-%d %H:%M:%S') if conv.updated_at else '',
            ])
        zip_file.writestr(f'conversations_{timestamp}.csv', conversations_csv.getvalue())
        
        # Export Saved Searches
        saved_searches_csv = io.StringIO()
        writer = csv.writer(saved_searches_csv)
        writer.writerow(['ID', 'Recruiter', 'Name', 'Location', 'Keywords', 'Created At', 'Last Notified'])
        for search in SavedSearch.objects.all().select_related('recruiter', 'recruiter__profile', 'recruiter__profile__user'):
            writer.writerow([
                search.id,
                search.recruiter.profile.user.username if search.recruiter.profile else '',
                search.name,
                search.location or '',
                search.keywords or '',
                search.created_at.strftime('%Y-%m-%d %H:%M:%S') if search.created_at else '',
                search.last_notified.strftime('%Y-%m-%d %H:%M:%S') if search.last_notified else '',
            ])
        zip_file.writestr(f'saved_searches_{timestamp}.csv', saved_searches_csv.getvalue())
    
    # Prepare response
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer.read(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="all_data_export_{timestamp}.zip"'
    return response

