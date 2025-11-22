# Data Export Feature

This document describes how to export data from JobRecruiter for reporting and analysis purposes.

## Overview

The export functionality allows administrators to export data in CSV format for:
- User and profile data
- Job postings
- Applications
- Messages and emails

## Methods of Export

### 1. Management Command (Recommended for Bulk Exports)

Use the `export_data` management command to export data from the command line.

#### Basic Usage

```bash
# Export all data types
python manage.py export_data --type all

# Export specific data types
python manage.py export_data --type users
python manage.py export_data --type job_postings
python manage.py export_data --type applications
python manage.py export_data --type messages
```

#### Advanced Usage

```bash
# Specify output directory
python manage.py export_data --type users --output-dir /path/to/exports

# Specify custom filename
python manage.py export_data --type users --output users_2024.csv

# Combine options
python manage.py export_data --type job_postings --output-dir exports --output jobs.csv
```

#### Export Types

- **users**: Exports all user accounts with profile information (JobSeekers and Employers)
- **job_postings**: Exports all job postings with details
- **applications**: Exports all job applications
- **messages**: Exports both email messages and conversation messages
- **all**: Exports all data types to separate CSV files

#### Output Location

By default, exports are saved to an `exports/` directory in the project root. Files are named with timestamps if no custom filename is provided:
- `users_20240101_120000.csv`
- `job_postings_20240101_120000.csv`
- etc.

### 2. Django Admin Interface

Export selected items directly from the Django admin interface.

#### Steps:

1. Log in to the Django admin panel: `http://127.0.0.1:8000/admin`
2. Navigate to any model (Users, Profiles, Job Postings, Applications, Messages, etc.)
3. Select the items you want to export using the checkboxes
4. Choose "Export selected items to CSV" from the "Action" dropdown
5. Click "Go"
6. The CSV file will be downloaded automatically

#### Available Models with Export:

- **Accounts**: Profile, JobSeekerProfile, EmployerProfile
- **Job Postings**: JobPosting, Application, PipelineStage
- **Messaging**: Conversation, Message, MessageNotification, EmailMessage

## Export Data Fields

### Users Export
- User ID, Username, Email, First Name, Last Name
- Account Type (Job Seeker/Employer)
- Date Joined, Last Login
- Profile information (name, location, contact info)
- Company information (for employers)

### Job Postings Export
- Job details (title, company, location, salary)
- Employment type, description, benefits
- Application URLs and emails
- Posted by, creation date, status
- Total number of applications

### Applications Export
- Job information
- Applicant details (username, email, name)
- Application status and pipeline stage
- Cover letter, notes
- Application dates

### Messages Export
- Message type (Email or Message)
- Sender and recipient
- Subject/content preview
- Status, read status
- Timestamps

## Best Practices

1. **Regular Exports**: Schedule regular exports for backup and reporting
2. **Data Privacy**: Ensure exported CSV files are stored securely
3. **File Management**: Clean up old export files periodically
4. **Large Datasets**: For very large datasets, consider filtering before export

## Example: Scheduled Export Script

You can create a cron job or scheduled task to run exports automatically:

```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * cd /path/to/JobRecruiter/JobRecruiter && python manage.py export_data --type all --output-dir /backups/exports
```

## Troubleshooting

### Permission Errors
- Ensure the output directory exists and is writable
- Check file permissions on the project directory

### Memory Issues
- For very large datasets, export in smaller batches
- Use filters in the admin interface before exporting

### Missing Data
- Ensure all migrations have been run: `python manage.py migrate`
- Check that related objects exist (e.g., profiles for users)

## Support

For issues or questions about the export functionality, contact the development team or refer to the Django management command documentation.

