"""
=============================================================================
RESUME ENDPOINTS
=============================================================================

Handles resume CRUD, AI generation, PDF export, and analytics.

ENDPOINTS:
    GET    /                     - List user's resumes (paginated)
    GET    /{resume_id}          - Get single resume
    POST   /create               - Create manual resume
    POST   /generate-ai          - 🔥 AI-powered resume generation
    PUT    /{resume_id}          - Update resume
    DELETE /{resume_id}          - Soft delete resume
    POST   /{resume_id}/publish  - Publish resume
    POST   /{resume_id}/archive  - Archive resume
    POST   /{resume_id}/download - Generate and download PDF
    GET    /{resume_id}/analytics - View count, application stats

=============================================================================
AUTHOR: SmartCareer AI Team
VERSION: 1.0.0
=============================================================================
"""

# =============================================================================
# IMPORTS
# =============================================================================

import logging
import time
import io
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.dependencies import get_db, get_current_active_user, PaginationParams
from app.models import User, Resume, ResumeStatus, Application, ApplicationStatus
from app.schemas.resume import (
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse,
    ResumeListResponse,
    ResumeGenerateRequest,
    ResumeGenerateResponse,
    ResumeToneEnum,
)
from app.schemas.auth import MessageResponse
from app.config import settings

# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# ROUTER
# =============================================================================

router = APIRouter()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def resume_to_response(resume: Resume) -> ResumeResponse:
    """Convert Resume model to ResumeResponse."""
    return ResumeResponse(
        id=str(resume.id),
        user_id=str(resume.user_id),
        title=resume.title,
        content=resume.content or {},
        status=resume.status,
        ai_generated=resume.ai_generated,
        ai_model_used=resume.ai_model_used,
        pdf_url=resume.pdf_url,
        view_count=resume.view_count,
        ats_score=resume.ats_score,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )


# =============================================================================
# PYDANTIC MODELS FOR NEW ENDPOINTS
# =============================================================================

from pydantic import BaseModel, Field
from enum import Enum


class ResumeTemplate(str, Enum):
    """Available resume templates."""
    MODERN = "modern"          # Clean, modern design with accent colors
    CLASSIC = "classic"        # Traditional, formal layout
    MINIMAL = "minimal"        # Simple, minimalist design
    CREATIVE = "creative"      # Bold, creative design for design roles
    PROFESSIONAL = "professional"  # ATS-optimized professional format
    EXECUTIVE = "executive"    # C-level executive format


class AIResumeGenerateRequest(BaseModel):
    """
    Request schema for AI resume generation.
    
    This is the 🔥 CORE FEATURE of the application.
    """
    
    user_data: Dict[str, Any] = Field(
        ...,
        description="User's data to include in resume",
        examples=[{
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+998901234567",
            "skills": ["Python", "FastAPI", "PostgreSQL", "AWS"],
            "experience": [
                {
                    "company": "Tech Corp",
                    "position": "Senior Developer",
                    "duration": "2022-2024",
                    "description": "Built REST APIs and microservices"
                }
            ],
            "education": [
                {
                    "institution": "MIT",
                    "degree": "Computer Science",
                    "year": "2020"
                }
            ]
        }]
    )
    
    template: ResumeTemplate = Field(
        default=ResumeTemplate.MODERN,
        description="Resume template style"
    )
    
    target_job_title: Optional[str] = Field(
        None,
        max_length=100,
        description="Target job title to optimize for",
        examples=["Senior Software Engineer"]
    )
    
    target_company: Optional[str] = Field(
        None,
        max_length=100,
        description="Target company for personalization",
        examples=["Google"]
    )
    
    job_description: Optional[str] = Field(
        None,
        description="Job description to tailor resume for ATS optimization"
    )
    
    tone: ResumeToneEnum = Field(
        default=ResumeToneEnum.PROFESSIONAL,
        description="Tone/style of the generated content"
    )
    
    include_cover_letter: bool = Field(
        default=False,
        description="Also generate a cover letter"
    )
    
    language: str = Field(
        default="en",
        max_length=5,
        description="Language code (en, uz, ru)"
    )


class AIResumeGenerateResponse(BaseModel):
    """Response from AI resume generation."""
    
    success: bool
    message: str
    
    # Generated resume
    resume: Optional[ResumeResponse] = None
    resume_content: Optional[Dict[str, Any]] = None
    
    # Optional cover letter
    cover_letter: Optional[str] = None
    
    # PDF URL (if generated)
    pdf_url: Optional[str] = None
    
    # ATS analysis
    ats_score: Optional[int] = None
    ats_suggestions: Optional[List[str]] = None
    
    # Metadata
    template_used: Optional[str] = None
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    processing_time_seconds: Optional[float] = None


class ResumeAnalyticsResponse(BaseModel):
    """Analytics data for a resume."""
    
    resume_id: str
    title: str
    
    # View statistics
    total_views: int
    views_this_week: int
    views_this_month: int
    
    # Application statistics
    total_applications: int
    pending_applications: int
    interview_applications: int
    accepted_applications: int
    rejected_applications: int
    
    # Success metrics
    interview_rate: float  # % of applications that got interviews
    success_rate: float    # % of applications that got accepted
    
    # ATS info
    ats_score: Optional[int] = None
    ats_keywords_matched: Optional[int] = None
    
    # Timeline
    created_at: datetime
    last_updated: datetime
    last_used_in_application: Optional[datetime] = None


class PDFDownloadResponse(BaseModel):
    """Response for PDF download request."""
    
    success: bool
    message: str
    pdf_url: Optional[str] = None
    download_expires_at: Optional[datetime] = None


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get(
    "/",
    response_model=ResumeListResponse,
    summary="List user's resumes",
    description="""
    Get paginated list of current user's resumes.
    
    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 20, max: 100)
    - `status`: Filter by status (draft, published, archived)
    
    **Returns:**
    - List of resumes with pagination info
    """
)
async def list_resumes(
    pagination: PaginationParams = Depends(),
    status_filter: Optional[str] = Query(
        None, 
        alias="status",
        description="Filter by status: draft, published, archived"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List current user's resumes with pagination."""
    
    query = db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.is_deleted == False
    )
    
    # Apply status filter
    if status_filter:
        query = query.filter(Resume.status == status_filter)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    resumes = query.order_by(Resume.updated_at.desc()).offset(
        pagination.skip
    ).limit(pagination.limit).all()
    
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    
    logger.info(f"Listed {len(resumes)} resumes for user: {current_user.id}")
    
    return ResumeListResponse(
        resumes=[resume_to_response(r) for r in resumes],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    )


@router.get(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Get single resume",
    description="""
    Get a specific resume by ID.
    
    Only the owner can access their resumes.
    """
)
async def get_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific resume by ID."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_deleted == False
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    logger.debug(f"Retrieved resume: {resume_id}")
    
    return resume_to_response(resume)


@router.post(
    "/create",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create manual resume",
    description="""
    Create a new resume manually (without AI generation).
    
    **Request Body:**
    - `title`: Resume title for identification
    - `content`: Structured resume data (JSONB)
    
    **Content Structure:**
    ```json
    {
        "personal_info": { "name": "...", "email": "...", "phone": "..." },
        "professional_summary": { "text": "..." },
        "work_experience": [...],
        "education": [...],
        "skills": { "technical_skills": [...], "soft_skills": [...] }
    }
    ```
    """
)
async def create_resume(
    resume_data: ResumeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new resume manually."""
    
    # Create resume
    resume = Resume(
        user_id=current_user.id,
        title=resume_data.title,
        content=resume_data.content,
        status=resume_data.status.value if resume_data.status else ResumeStatus.DRAFT.value,
        ai_generated=False,
    )
    
    db.add(resume)
    db.commit()
    db.refresh(resume)
    
    logger.info(f"Resume created: {resume.id} for user: {current_user.id}")
    
    return resume_to_response(resume)


@router.post(
    "/generate-ai",
    response_model=AIResumeGenerateResponse,
    summary="🔥 Generate resume with AI",
    description="""
    **CORE FEATURE** - Generate a professional resume using AI.
    
    This endpoint uses OpenAI GPT-4 to create a polished, ATS-optimized resume
    based on the user's data and preferences.
    
    **Features:**
    - Multiple template styles (modern, classic, minimal, creative)
    - ATS optimization with keyword matching
    - Job description tailoring
    - Optional cover letter generation
    - Multi-language support (en, uz, ru)
    
    **Request Body:**
    ```json
    {
        "user_data": {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "FastAPI"],
            "experience": [{"company": "...", "position": "..."}],
            "education": [{"institution": "...", "degree": "..."}]
        },
        "template": "modern",
        "target_job_title": "Senior Software Engineer",
        "tone": "professional"
    }
    ```
    
    **Response:**
    - Generated resume saved to database
    - Structured JSON content
    - ATS score and suggestions
    - Processing metadata
    """
)
async def generate_ai_resume(
    request: AIResumeGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate a professional resume using AI."""
    
    start_time = time.time()
    
    logger.info(f"🤖 AI resume generation started for user: {current_user.id}")
    logger.info(f"   Template: {request.template.value}")
    logger.info(f"   Target job: {request.target_job_title or 'Not specified'}")
    
    try:
        # Import AI service
        from app.services.ai_service import AIService, AIConfigurationError, AIGenerationError
        
        # Initialize AI service
        try:
            ai_service = AIService()
        except AIConfigurationError as e:
            logger.error(f"AI service not configured: {e}")
            return AIResumeGenerateResponse(
                success=False,
                message=f"AI service is not configured: {e}. Please add your OpenAI API key."
            )
        
        # Extract data from user_data
        user_data = request.user_data
        
        # Determine job title from request or user data
        job_title = request.target_job_title
        if not job_title and user_data.get("experience"):
            # Use most recent job position
            exp = user_data.get("experience", [])
            if exp and isinstance(exp, list) and len(exp) > 0:
                job_title = exp[0].get("position", "Professional")
        job_title = job_title or "Professional"
        
        # Extract skills
        skills = user_data.get("skills", [])
        if not skills:
            skills = ["Communication", "Problem Solving", "Teamwork"]
        
        # Determine education level
        education = user_data.get("education", [])
        education_level = "Bachelor's Degree"
        field_of_study = "General Studies"
        if education and isinstance(education, list) and len(education) > 0:
            edu = education[0]
            education_level = edu.get("degree", "Bachelor's Degree")
            field_of_study = edu.get("field", edu.get("major", "General Studies"))
        
        # Calculate years of experience
        experience = user_data.get("experience", [])
        years_experience = len(experience) * 2  # Rough estimate
        
        # Map template to tone
        tone_map = {
            ResumeTemplate.MODERN: ResumeToneEnum.PROFESSIONAL,
            ResumeTemplate.CLASSIC: ResumeToneEnum.PROFESSIONAL,
            ResumeTemplate.MINIMAL: ResumeToneEnum.TECHNICAL,
            ResumeTemplate.CREATIVE: ResumeToneEnum.CREATIVE,
            ResumeTemplate.PROFESSIONAL: ResumeToneEnum.PROFESSIONAL,
            ResumeTemplate.EXECUTIVE: ResumeToneEnum.EXECUTIVE,
        }
        tone = request.tone or tone_map.get(request.template, ResumeToneEnum.PROFESSIONAL)
        
        # Generate resume content using AI
        logger.info("   Calling OpenAI API...")
        
        content = await ai_service.generate_resume(
            job_title=job_title,
            years_experience=years_experience,
            skills=skills,
            education_level=education_level,
            field_of_study=field_of_study,
            industry=user_data.get("industry", "Technology"),
            target_company=request.target_company,
            job_description=request.job_description,
            tone=tone,
            include_projects=bool(user_data.get("projects")),
            include_certifications=bool(user_data.get("certifications")),
            user_input_data=user_data,  # Pass all user data
        )
        
        # Add template metadata to content
        if isinstance(content, dict):
            content["_metadata"] = {
                "template": request.template.value,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "language": request.language,
            }
        
        # Calculate ATS score (simple implementation)
        ats_score = _calculate_ats_score(content, request.job_description)
        ats_suggestions = _get_ats_suggestions(content, request.job_description)
        
        # Generate cover letter if requested
        cover_letter = None
        if request.include_cover_letter:
            # TODO: Implement cover letter generation
            cover_letter = "Cover letter generation coming soon!"
        
        # Create resume in database
        resume_title = f"{job_title} Resume - {request.template.value.title()}"
        resume = Resume(
            user_id=current_user.id,
            title=resume_title,
            content=content,
            status=ResumeStatus.DRAFT.value,
            ai_generated=True,
            ai_model_used=settings.OPENAI_MODEL,
            ats_score=ats_score,
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Get token usage
        usage = ai_service.get_usage_summary()
        tokens_used = usage.get("total_tokens", 0)
        
        logger.info(f"✅ AI resume generated: {resume.id}")
        logger.info(f"   Processing time: {processing_time:.2f}s")
        logger.info(f"   Tokens used: {tokens_used}")
        logger.info(f"   ATS Score: {ats_score}")
        
        return AIResumeGenerateResponse(
            success=True,
            message="Resume generated successfully!",
            resume=resume_to_response(resume),
            resume_content=content,
            cover_letter=cover_letter,
            ats_score=ats_score,
            ats_suggestions=ats_suggestions,
            template_used=request.template.value,
            tokens_used=tokens_used,
            model_used=settings.OPENAI_MODEL,
            processing_time_seconds=round(processing_time, 2),
        )
        
    except AIGenerationError as e:
        logger.error(f"AI generation error: {e}")
        return AIResumeGenerateResponse(
            success=False,
            message=f"AI generation failed: {str(e)}"
        )
    except Exception as e:
        logger.exception(f"Unexpected error during resume generation: {e}")
        return AIResumeGenerateResponse(
            success=False,
            message="An unexpected error occurred during resume generation. Please try again."
        )


@router.put(
    "/{resume_id}",
    response_model=ResumeResponse,
    summary="Update resume",
    description="""
    Update an existing resume.
    
    Only the owner can update their resumes.
    Partial updates are supported (only send fields to update).
    """
)
async def update_resume(
    resume_id: UUID,
    update_data: ResumeUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an existing resume."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_deleted == False
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        if field == "status" and value:
            setattr(resume, field, value.value)
        elif hasattr(resume, field) and value is not None:
            setattr(resume, field, value)
    
    db.commit()
    db.refresh(resume)
    
    logger.info(f"Resume updated: {resume.id}")
    
    return resume_to_response(resume)


@router.delete(
    "/{resume_id}",
    response_model=MessageResponse,
    summary="Delete resume",
    description="""
    Soft delete a resume.
    
    The resume is not permanently deleted but marked as deleted.
    It can be restored by an admin if needed.
    """
)
async def delete_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Soft delete a resume."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_deleted == False
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    resume.soft_delete()
    db.commit()
    
    logger.info(f"Resume deleted: {resume.id}")
    
    return MessageResponse(
        message="Resume deleted successfully",
        success=True
    )


@router.post(
    "/{resume_id}/publish",
    response_model=ResumeResponse,
    summary="Publish resume",
    description="""
    Publish a resume (make it ready for job applications).
    
    Only published resumes can be used in job applications.
    """
)
async def publish_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Publish a resume."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_deleted == False
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    resume.publish()
    db.commit()
    db.refresh(resume)
    
    logger.info(f"Resume published: {resume.id}")
    
    return resume_to_response(resume)


@router.post(
    "/{resume_id}/archive",
    response_model=ResumeResponse,
    summary="Archive resume",
    description="""
    Archive a resume.
    
    Archived resumes are kept for history but can't be used in new applications.
    """
)
async def archive_resume(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Archive a resume."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_deleted == False
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    resume.archive()
    db.commit()
    db.refresh(resume)
    
    logger.info(f"Resume archived: {resume.id}")
    
    return resume_to_response(resume)


@router.post(
    "/{resume_id}/download",
    response_model=PDFDownloadResponse,
    summary="Generate and download PDF",
    description="""
    Generate a PDF version of the resume.
    
    The PDF is generated from the resume content and template.
    Returns a URL to download the PDF (valid for 1 hour).
    
    **Note:** For direct PDF streaming, use the `/download-stream` endpoint.
    """
)
async def download_resume_pdf(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate and return PDF download link."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_deleted == False
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    try:
        # Generate PDF (placeholder - implement actual PDF generation)
        pdf_url = await _generate_pdf(resume)
        
        # Update resume with PDF URL
        resume.pdf_url = pdf_url
        db.commit()
        
        # Set expiration (1 hour from now)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        logger.info(f"PDF generated for resume: {resume.id}")
        
        return PDFDownloadResponse(
            success=True,
            message="PDF generated successfully",
            pdf_url=pdf_url,
            download_expires_at=expires_at,
        )
        
    except Exception as e:
        logger.exception(f"PDF generation failed: {e}")
        return PDFDownloadResponse(
            success=False,
            message=f"PDF generation failed: {str(e)}"
        )


@router.get(
    "/{resume_id}/analytics",
    response_model=ResumeAnalyticsResponse,
    summary="Get resume analytics",
    description="""
    Get analytics and statistics for a resume.
    
    **Includes:**
    - View statistics (total, this week, this month)
    - Application statistics (pending, interview, accepted, rejected)
    - Success metrics (interview rate, success rate)
    - ATS information
    """
)
async def get_resume_analytics(
    resume_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a resume."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id,
        Resume.is_deleted == False
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get application statistics
    applications = db.query(Application).filter(
        Application.resume_id == resume_id,
        Application.is_deleted == False
    ).all()
    
    total_applications = len(applications)
    pending_count = sum(1 for a in applications if a.status == ApplicationStatus.PENDING.value)
    interview_count = sum(1 for a in applications if a.status == ApplicationStatus.INTERVIEW.value)
    accepted_count = sum(1 for a in applications if a.status == ApplicationStatus.ACCEPTED.value)
    rejected_count = sum(1 for a in applications if a.status == ApplicationStatus.REJECTED.value)
    
    # Calculate rates
    interview_rate = 0.0
    success_rate = 0.0
    if total_applications > 0:
        interview_rate = (interview_count + accepted_count) / total_applications * 100
        success_rate = accepted_count / total_applications * 100
    
    # Get last application date
    last_application = db.query(Application).filter(
        Application.resume_id == resume_id,
        Application.is_deleted == False
    ).order_by(Application.applied_at.desc()).first()
    
    last_used = last_application.applied_at if last_application else None
    
    # Calculate views (placeholder - implement actual view tracking)
    views_this_week = resume.view_count // 4  # Rough estimate
    views_this_month = resume.view_count
    
    logger.info(f"Analytics retrieved for resume: {resume.id}")
    
    return ResumeAnalyticsResponse(
        resume_id=str(resume.id),
        title=resume.title,
        total_views=resume.view_count,
        views_this_week=views_this_week,
        views_this_month=views_this_month,
        total_applications=total_applications,
        pending_applications=pending_count,
        interview_applications=interview_count,
        accepted_applications=accepted_count,
        rejected_applications=rejected_count,
        interview_rate=round(interview_rate, 1),
        success_rate=round(success_rate, 1),
        ats_score=resume.ats_score,
        ats_keywords_matched=None,  # TODO: Implement keyword tracking
        created_at=resume.created_at,
        last_updated=resume.updated_at,
        last_used_in_application=last_used,
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

from datetime import timedelta


def _calculate_ats_score(content: Dict[str, Any], job_description: Optional[str]) -> int:
    """
    Calculate ATS (Applicant Tracking System) compatibility score.
    
    Factors:
    - Has all required sections (summary, experience, education, skills)
    - Keyword density
    - Proper formatting
    - Quantified achievements
    """
    score = 0
    
    # Check for required sections (20 points each)
    if content.get("professional_summary"):
        score += 20
    if content.get("work_experience"):
        score += 20
    if content.get("education"):
        score += 20
    if content.get("skills"):
        score += 20
    
    # Check for contact info (10 points)
    personal_info = content.get("personal_info", {})
    if personal_info.get("email") and personal_info.get("phone"):
        score += 10
    
    # Check for quantified achievements (10 points)
    work_exp = content.get("work_experience", [])
    if work_exp:
        for exp in work_exp:
            achievements = exp.get("achievements", [])
            if achievements:
                score += 10
                break
    
    return min(score, 100)


def _get_ats_suggestions(content: Dict[str, Any], job_description: Optional[str]) -> List[str]:
    """
    Get suggestions for improving ATS compatibility.
    """
    suggestions = []
    
    if not content.get("professional_summary"):
        suggestions.append("Add a professional summary to highlight your key qualifications")
    
    if not content.get("work_experience"):
        suggestions.append("Add your work experience with specific achievements")
    
    work_exp = content.get("work_experience", [])
    has_quantified = any(
        exp.get("achievements") 
        for exp in work_exp
    )
    if not has_quantified:
        suggestions.append("Add quantified achievements (e.g., 'Increased sales by 25%')")
    
    skills = content.get("skills", {})
    if not skills:
        suggestions.append("Add a skills section with relevant keywords")
    
    if job_description:
        suggestions.append("Review the job description and ensure key terms are included")
    
    return suggestions


async def _generate_pdf(resume: Resume) -> str:
    """
    Generate PDF from resume content.
    
    In production, this would:
    1. Use a template engine (Jinja2, WeasyPrint, etc.)
    2. Generate PDF
    3. Upload to S3 or similar storage
    4. Return presigned URL
    
    For now, returns a placeholder URL.
    """
    # TODO: Implement actual PDF generation
    # Options:
    # - WeasyPrint for HTML to PDF
    # - ReportLab for programmatic PDF
    # - External service (HTML to PDF API)
    
    # Placeholder URL
    pdf_url = f"/api/v1/resumes/{resume.id}/pdf"
    
    return pdf_url
