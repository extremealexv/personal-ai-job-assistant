"""AI-powered resume tailoring service."""
import json
import logging
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.ai_exceptions import AIProviderError
from app.models.job import JobPosting
from app.models.prompt import PromptTask, PromptTemplate
from app.models.resume import MasterResume, ResumeVersion
from app.providers.openai_provider import OpenAIProvider
from app.providers.gemini_provider import GeminiProvider
from app.schemas.resume import ResumeVersionCreate

logger = logging.getLogger(__name__)


class AIResumeTailoringService:
    """Service for AI-powered resume tailoring."""

    def __init__(self):
        """Initialize the resume tailoring service with configured AI provider."""
        # Select provider based on config
        if settings.ai_provider == "gemini":
            logger.info("Using Google Gemini as AI provider")
            self.ai_provider = GeminiProvider()
        elif settings.ai_provider == "openai":
            logger.info("Using OpenAI as AI provider")
            self.ai_provider = OpenAIProvider()
        else:
            logger.warning(f"Unknown AI provider '{settings.ai_provider}', defaulting to Gemini")
            self.ai_provider = GeminiProvider()

    async def tailor_resume_for_job(
        self,
        db: AsyncSession,
        user_id: UUID,
        master_resume_id: UUID,
        job_posting_id: UUID,
        *,
        prompt_template_id: Optional[UUID] = None,
        version_name: Optional[str] = None,
    ) -> ResumeVersion:
        """Tailor a master resume for a specific job posting.

        Args:
            db: Database session
            user_id: User ID
            master_resume_id: Master resume to tailor
            job_posting_id: Target job posting
            prompt_template_id: Optional custom prompt template
            version_name: Optional custom version name

        Returns:
            New resume version with tailored content

        Raises:
            ValueError: If master resume or job not found
            AIProviderError: If AI generation fails
        """
        # Fetch master resume with all relationships
        result = await db.execute(
            select(MasterResume)
            .where(MasterResume.id == master_resume_id)
            .where(MasterResume.user_id == user_id)
            .options(
                selectinload(MasterResume.work_experiences),
                selectinload(MasterResume.education),
                selectinload(MasterResume.skills),
                selectinload(MasterResume.certifications),
            )
        )
        master_resume = result.scalar_one_or_none()

        if not master_resume:
            raise ValueError(f"Master resume {master_resume_id} not found")

        # Fetch job posting
        result = await db.execute(
            select(JobPosting)
            .where(JobPosting.id == job_posting_id)
            .where(JobPosting.user_id == user_id)
        )
        job_posting = result.scalar_one_or_none()

        if not job_posting:
            raise ValueError(f"Job posting {job_posting_id} not found")

        # Get prompt template
        if prompt_template_id:
            result = await db.execute(
                select(PromptTemplate)
                .where(PromptTemplate.id == prompt_template_id)
                .where(PromptTemplate.user_id == user_id)
            )
            prompt_template = result.scalar_one_or_none()
            if not prompt_template:
                raise ValueError(f"Prompt template {prompt_template_id} not found")
        else:
            # Use default template for resume tailoring
            result = await db.execute(
                select(PromptTemplate)
                .where(PromptTemplate.user_id == user_id)
                .where(PromptTemplate.task_type == PromptTask.RESUME_TAILOR)
                .where(PromptTemplate.is_active == True)
                .order_by(PromptTemplate.created_at.desc())
                .limit(1)
            )
            prompt_template = result.scalar_one_or_none()

            if not prompt_template:
                raise ValueError("No active resume tailoring prompt template found")

        # Convert master resume to structured dict
        master_resume_dict = self._serialize_master_resume(master_resume)

        # Generate tailored resume using AI
        logger.info(
            f"Tailoring resume {master_resume_id} for job {job_posting_id} "
            f"using prompt template {prompt_template.id}"
        )

        try:
            ai_response = await self.ai_provider.tailor_resume(
                master_resume=master_resume_dict,
                job_description=job_posting.job_description or "",
                prompt_template=prompt_template.prompt_text,
                company_name=job_posting.company_name,
                user_id=user_id,
            )
        except Exception as e:
            logger.error(f"AI resume tailoring failed: {e}")
            raise AIProviderError(f"Failed to tailor resume: {e}")

        # Parse AI response
        try:
            modifications = json.loads(ai_response.content)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response as JSON: {ai_response.content[:500]}")
            # Try to extract JSON from markdown code blocks
            modifications = self._extract_json_from_response(ai_response.content)

        # Generate version name if not provided
        if not version_name:
            version_name = f"{job_posting.job_title} at {job_posting.company_name}"

        # Create resume version
        resume_version = ResumeVersion(
            master_resume_id=master_resume_id,
            job_posting_id=job_posting_id,
            version_name=version_name,
            target_role=job_posting.job_title,
            target_company=job_posting.company_name,
            modifications=modifications,
            prompt_template_id=prompt_template.id,
            ai_model_used=ai_response.model,
            generation_timestamp=datetime.now(),
        )

        db.add(resume_version)
        await db.commit()
        await db.refresh(resume_version)

        logger.info(
            f"Created resume version {resume_version.id} - "
            f"Cost: ${ai_response.usage.estimated_cost:.4f}, "
            f"Tokens: {ai_response.usage.total_tokens}"
        )

        return resume_version

    def _serialize_master_resume(self, master_resume: MasterResume) -> dict[str, Any]:
        """Convert master resume to structured dictionary for AI processing."""
        return {
            "personal_info": {
                "full_name": master_resume.full_name,
                "email": master_resume.email,
                "phone": master_resume.phone,
                "location": master_resume.location,
                "linkedin": master_resume.linkedin_url,
                "github": master_resume.github_url,
                "portfolio": master_resume.portfolio_url,
                "summary": master_resume.summary,
            },
            "work_experiences": [
                {
                    "company": exp.company_name,
                    "title": exp.job_title,
                    "employment_type": exp.employment_type.value if exp.employment_type else None,
                    "location": exp.location,
                    "start_date": exp.start_date.isoformat() if exp.start_date else None,
                    "end_date": exp.end_date.isoformat() if exp.end_date else None,
                    "is_current": exp.is_current,
                    "description": exp.description,
                    "achievements": exp.achievements,
                    "technologies": exp.technologies,
                }
                for exp in sorted(master_resume.work_experiences, key=lambda x: x.display_order)
            ],
            "education": [
                {
                    "institution": edu.institution,
                    "degree": edu.degree_type.value if edu.degree_type else None,
                    "field_of_study": edu.field_of_study,
                    "location": edu.location,
                    "start_date": edu.start_date.isoformat() if edu.start_date else None,
                    "end_date": edu.end_date.isoformat() if edu.end_date else None,
                    "gpa": float(edu.gpa) if edu.gpa else None,
                    "honors": edu.honors,
                    "activities": edu.activities,
                }
                for edu in sorted(master_resume.education, key=lambda x: x.display_order)
            ],
            "skills": [
                {
                    "name": skill.skill_name,
                    "category": skill.category.value if skill.category else None,
                    "proficiency": skill.proficiency_level,
                    "years": skill.years_of_experience,
                }
                for skill in sorted(master_resume.skills, key=lambda x: x.display_order)
            ],
            "certifications": [
                {
                    "name": cert.certification_name,
                    "issuer": cert.issuing_organization,
                    "issue_date": cert.issue_date.isoformat() if cert.issue_date else None,
                    "expiration_date": (
                        cert.expiration_date.isoformat() if cert.expiration_date else None
                    ),
                    "credential_id": cert.credential_id,
                    "credential_url": cert.credential_url,
                }
                for cert in sorted(master_resume.certifications, key=lambda x: x.display_order)
            ],
        }

    def _extract_json_from_response(self, content: str) -> dict[str, Any]:
        """Extract JSON from AI response that may be wrapped in markdown code blocks."""
        import re

        # Try to find JSON in markdown code blocks - use non-greedy match with proper JSON structure
        # First, try to extract from ```json ... ``` blocks
        json_pattern = r"```json\s*\n(.*?)\n```"
        match = re.search(json_pattern, content, re.DOTALL)
        
        if match:
            try:
                json_str = match.group(1).strip()
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from markdown block: {e}")

        # Try generic code blocks
        json_pattern = r"```\s*\n(.*?)\n```"
        match = re.search(json_pattern, content, re.DOTALL)
        
        if match:
            try:
                json_str = match.group(1).strip()
                # Check if it starts with { to be JSON
                if json_str.startswith('{'):
                    return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from generic code block: {e}")

        # If no markdown blocks, try direct parsing
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            # Return minimal structure
            logger.warning("Could not parse AI response, returning minimal structure")
            return {"modifications": content, "error": "Could not parse as JSON"}

    async def get_resume_diff(
        self, db: AsyncSession, resume_version_id: UUID, user_id: UUID
    ) -> dict[str, Any]:
        """Get diff between master resume and tailored version.

        Args:
            db: Database session
            resume_version_id: Resume version to compare
            user_id: User ID

        Returns:
            Dictionary with added, modified, and removed sections

        Raises:
            ValueError: If resume version not found
        """
        # Fetch resume version with master resume
        result = await db.execute(
            select(ResumeVersion)
            .where(ResumeVersion.id == resume_version_id)
            .options(
                selectinload(ResumeVersion.master_resume).selectinload(
                    MasterResume.work_experiences
                ),
                selectinload(ResumeVersion.master_resume).selectinload(MasterResume.education),
                selectinload(ResumeVersion.master_resume).selectinload(MasterResume.skills),
            )
        )
        resume_version = result.scalar_one_or_none()

        if not resume_version:
            raise ValueError(f"Resume version {resume_version_id} not found")

        # Serialize master resume
        master_data = self._serialize_master_resume(resume_version.master_resume)

        # Get modifications
        modifications = resume_version.modifications or {}

        # Calculate diff
        diff = {
            "version_name": resume_version.version_name,
            "target_role": resume_version.target_role,
            "target_company": resume_version.target_company,
            "modifications": modifications,
            "master_sections": list(master_data.keys()),
            "modified_sections": list(modifications.keys()) if isinstance(modifications, dict) else [],
        }

        return diff


# Global instance
ai_resume_tailoring_service = AIResumeTailoringService()
