# Pipeline Feature - Kanban Board for Applicant Management

## Overview
The Pipeline feature allows recruiters to organize and manage job applicants using a visual Kanban board interface. This helps streamline the hiring process by providing a clear view of where each candidate stands in the recruitment pipeline.

## Features

### 1. Kanban Board Interface
- **Visual Pipeline**: Applications are organized into columns representing different stages of the hiring process
- **Drag & Drop**: Move applications between stages by dragging and dropping cards
- **Color-coded Stages**: Each pipeline stage has a distinct color for easy identification
- **Real-time Updates**: Changes are saved immediately via AJAX

### 2. Pipeline Stages
The system comes with 8 default pipeline stages:
1. **Applied** (Blue) - Application received and under initial review
2. **Phone Screen** (Purple) - Initial phone screening scheduled or completed
3. **Technical Interview** (Amber) - Technical skills assessment
4. **Final Interview** (Red) - Final interview with hiring manager/team
5. **Reference Check** (Emerald) - Checking references and background
6. **Offer** (Green) - Job offer extended
7. **Hired** (Dark Green) - Candidate accepted offer and started
8. **Rejected** (Gray) - Application rejected

### 3. Application Management
- **Detailed View**: Click on any application to see full candidate details
- **Internal Notes**: Add and edit private notes for each application
- **Candidate Information**: View cover letter, resume, profile details, and contact information
- **Timeline Tracking**: See when applications were submitted and stages were updated

### 4. Statistics Dashboard
- **Total Applications**: Count of all applications for the job
- **In Progress**: Applications currently being processed
- **Hired**: Successfully hired candidates
- **Rejected**: Rejected applications

## How to Use

### For Recruiters/Employers:

1. **Access Pipeline**: 
   - Go to "My Posted Jobs"
   - Click "Pipeline" button for any job with applications
   - Or use the "Pipeline View" button from the applicants list

2. **Move Applications**:
   - Drag application cards between columns to change their stage
   - The system automatically saves changes

3. **View Details**:
   - Click the dropdown menu on any application card
   - Select "View Details" to see full candidate information

4. **Add Notes**:
   - Click the dropdown menu on any application card
   - Select "Edit Notes" to add private internal notes

5. **Switch Views**:
   - Use "List View" button to return to traditional applicant list
   - Use "View Job" button to see the job posting details

## Technical Implementation

### Models
- **PipelineStage**: Defines the stages in the hiring pipeline
- **Application**: Extended with pipeline_stage, notes, and stage_updated_at fields

### Views
- **pipeline_view**: Main Kanban board interface
- **update_application_stage**: AJAX endpoint for moving applications
- **update_application_notes**: AJAX endpoint for updating notes
- **application_detail_modal**: AJAX endpoint for application details

### Templates
- **pipeline.html**: Main Kanban board template with drag & drop functionality
- **Updated view_applicants.html**: Added pipeline link
- **Updated my_posted_jobs.html**: Added pipeline buttons

### Management Commands
- **create_default_pipeline_stages**: Creates the 8 default pipeline stages
- **assign_applications_to_pipeline**: Assigns existing applications to the "Applied" stage

## Setup Instructions

1. **Run Migrations**:
   ```bash
   python manage.py makemigrations jobpostings
   python manage.py migrate
   ```

2. **Create Default Stages**:
   ```bash
   python manage.py create_default_pipeline_stages
   ```

3. **Assign Existing Applications**:
   ```bash
   python manage.py assign_applications_to_pipeline
   ```

## Customization

### Adding New Pipeline Stages
1. Go to Django Admin → Pipeline Stages
2. Add new stages with appropriate colors and order
3. Set `is_final_positive` or `is_final_negative` for final outcomes

### Modifying Stage Colors
- Edit the `color` field in PipelineStage model
- Use hex color codes (e.g., #FF5733)

### Reordering Stages
- Modify the `order` field in PipelineStage model
- Lower numbers appear first in the pipeline

## Browser Compatibility
- Modern browsers with JavaScript enabled
- Drag & drop requires HTML5 support
- Responsive design works on desktop and mobile devices

## Security
- Only job posting owners can access the pipeline
- All AJAX endpoints include proper authentication checks
- CSRF protection enabled for all state-changing operations
