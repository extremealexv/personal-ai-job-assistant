"""AI-powered cover letter generation service."""
import json
import logging
import re
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.ai_exceptions import AIProviderError
from app.models.job import Application, CoverLetter, JobPosting
from app.models.prompt import PromptTask, PromptTemplate
from app.models.resume import MasterResume, ResumeVersion
from app.providers.gemini_provider import GeminiProvider
from app.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class AICoverLetterService:
    """Service for AI-powered cover letter generation."""

    def __init__(self):
        """Initialize AI cover letter service with configured provider."""
        # Select AI provider based on configuration
        if settings.ai_provider == "gemini":
            logger.info("Using Google Gemini as AI provider for cover letters")
            self.ai_provider = GeminiProvider()
        elif settings.ai_provider == "openai":
            logger.info("Using OpenAI as AI provider for cover letters")
            self.ai_provider = OpenAIProvider()
        else:
            raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")

    async def generate_cover_letter(
        self,
        db: AsyncSession,
        application_id: UUID,
        user_id: UUID,
        prompt_template_id: Optional[UUID] = None,
    ) -> CoverLetter:
        """
        Generate an AI-powered cover letter for an application.

        Args:
            db: Database session
            application_id: Application to generate cover letter for
            user_id: User ID for authorization
            prompt_template_id: Optional prompt template to use

        Returns:
            Generated cover letter

        Raises:
            ValueError: If application, job, or resume not found
            AIProviderError: If AI generation fails
        """
        # Fetch application with job and resume
        result = await db.execute(
            select(Application)
            .options(
                selectinload(Application.job_posting),
                selectinload(Application.resume_version).selectinload(
                    ResumeVersion.master_resume
                ),
            )
            .where(Application.id == application_id, Application.user_id == user_id)
        )
        application = result.scalar_one_or_none()

        if not application:
            raise ValueError(f"Application {application_id} not found")

        if not application.job_posting:
            raise ValueError("Application has no associated job posting")

        if not application.resume_version:
            raise ValueError("Application has no associated resume version")

        job_posting = application.job_posting
        resume_version = application.resume_version

        # Get or use default prompt template
        if prompt_template_id:
            template_result = await db.execute(
                select(PromptTemplate).where(
                    PromptTemplate.id == prompt_template_id,
                    PromptTemplate.user_id == user_id,
                )
            )
            prompt_template = template_result.scalar_one_or_none()
            if not prompt_template:
                raise ValueError(f"Prompt template {prompt_template_id} not found")
        else:
            # Get default cover letter template
            template_result = await db.execute(
                select(PromptTemplate)
                .where(
                    PromptTemplate.user_id == user_id,
                    PromptTemplate.task_type == PromptTask.COVER_LETTER,
                    PromptTemplate.is_active == True,  # noqa: E712
                )
                .order_by(PromptTemplate.created_at.desc())
                .limit(1)
            )
            prompt_template = template_result.scalar_one_or_none()
            if not prompt_template:
                raise ValueError("No active cover letter prompt template found")

        logger.info(
            f"Generating cover letter for application {application_id} "
            f"using prompt template {prompt_template.id}"
        )

        # Prepare resume summary from resume version modifications
        resume_summary = self._create_resume_summary(resume_version)

        # Generate cover letter using AI
        try:
            ai_response = await self.ai_provider.generate_cover_letter(
                resume_summary=resume_summary,
                job_description=job_posting.job_description or "",
                prompt_template=prompt_template.prompt_text,
                company_name=job_posting.company_name,
                job_title=job_posting.job_title,
                user_id=user_id,
            )
        except Exception as e:
            logger.error(f"AI cover letter generation failed: {e}")
            raise AIProviderError(f"Failed to generate cover letter: {e}")

        # Parse AI response - may be wrapped in markdown code blocks
        content = self._extract_text_from_response(ai_response.content)

        # Get the next version number for this application
        from sqlalchemy import func

        version_result = await db.execute(
            select(func.max(CoverLetter.version_number)).where(
                CoverLetter.application_id == application_id
            )
        )
        max_version = version_result.scalar()
        next_version = (max_version or 0) + 1

        # If this is version 1, make it active. Otherwise, keep existing active version
        is_active = next_version == 1

        # Create cover letter
        cover_letter = CoverLetter(
            application_id=application_id,
            content=content,
            prompt_template_id=prompt_template.id,
            ai_model_used=ai_response.model,
            version_number=next_version,
            is_active=is_active,
            generation_timestamp=datetime.now(),  # Fixed: use datetime.now() not token count
        )

        db.add(cover_letter)
        await db.commit()
        await db.refresh(cover_letter)

        logger.info(
            f"Created cover letter {cover_letter.id} (v{next_version}) - "
            f"Model: {ai_response.model}, Length: {len(content)} chars"
        )

        return cover_letter

    def _create_resume_summary(self, resume_version: ResumeVersion) -> str:
        """Create a concise resume summary from resume version modifications."""
        modifications = resume_version.modifications

        if not modifications or not isinstance(modifications, dict):
            return "No resume information available"

        # Extract key information
        summary_parts = []

        # Add summary if available
        if "summary" in modifications:
            summary_parts.append(modifications["summary"])

        # Add work experience highlights
        if "work_experience" in modifications:
            work_exp = modifications["work_experience"]
            if isinstance(work_exp, list) and work_exp:
                summary_parts.append("\nKey Experience:")
                for exp in work_exp[:2]:  # Top 2 most recent
                    if isinstance(exp, dict):
                        title = exp.get("title", "")
                        company = exp.get("company", "")
                        if title and company:
                            summary_parts.append(f"- {title} at {company}")

                            # Add top achievements
                            achievements = exp.get("achievements", [])
                            if isinstance(achievements, list):
                                for achievement in achievements[:2]:  # Top 2 achievements
                                    if achievement:
                                        summary_parts.append(f"  • {achievement}")

        # Add skills if available
        if "skills" in modifications:
            skills = modifications["skills"]
            if isinstance(skills, dict):
                # Extract skills from categories
                all_skills = []
                for category_skills in skills.values():
                    if isinstance(category_skills, list):
                        all_skills.extend(category_skills)

                if all_skills:
                    summary_parts.append(f"\nKey Skills: {', '.join(all_skills[:10])}")
            elif isinstance(skills, list):
                summary_parts.append(f"\nKey Skills: {', '.join(skills[:10])}")

        return "\n".join(summary_parts)

    def _extract_text_from_response(self, content: str) -> str:
        """Extract plain text from AI response that may be wrapped in markdown."""
        # Remove markdown code blocks if present
        content = content.strip()

        # Try to find text in markdown code blocks
        # Pattern: ```text or ```markdown or just ```
        markdown_pattern = r"```(?:text|markdown)?\s*\n(.*?)\n```"
        match = re.search(markdown_pattern, content, re.DOTALL)

        if match:
            logger.debug("Extracted cover letter from markdown code block")
            return match.group(1).strip()

        # No markdown blocks found, return as-is
        return content


# Global instance
ai_cover_letter_service = AICoverLetterService()
