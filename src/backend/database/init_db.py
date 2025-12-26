#!/usr/bin/env python3
"""
Database initialization script for Personal AI Job Assistant.

This script creates the database schema and optionally seeds with default data.

Usage:
    python init_db.py                    # Create schema only
    python init_db.py --seed             # Create schema and seed data
    python init_db.py --drop --seed      # Drop existing, recreate, and seed
"""

import argparse
import asyncio
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/ai_job_assistant"

# Path to schema SQL file
SCHEMA_FILE = Path(__file__).parent / "schema.sql"


async def drop_schema(engine):
    """Drop all tables and types."""
    print("🗑️  Dropping existing schema...")
    
    async with engine.begin() as conn:
        # Drop tables
        await conn.execute(text("""
            DROP TABLE IF EXISTS analytics_snapshots CASCADE;
            DROP TABLE IF EXISTS interview_events CASCADE;
            DROP TABLE IF EXISTS email_threads CASCADE;
            DROP TABLE IF EXISTS credentials CASCADE;
            DROP TABLE IF EXISTS cover_letters CASCADE;
            DROP TABLE IF EXISTS applications CASCADE;
            DROP TABLE IF EXISTS resume_versions CASCADE;
            DROP TABLE IF EXISTS prompt_templates CASCADE;
            DROP TABLE IF EXISTS job_postings CASCADE;
            DROP TABLE IF EXISTS certifications CASCADE;
            DROP TABLE IF EXISTS skills CASCADE;
            DROP TABLE IF EXISTS education CASCADE;
            DROP TABLE IF EXISTS work_experiences CASCADE;
            DROP TABLE IF EXISTS master_resumes CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
        """))
        
        # Drop types
        await conn.execute(text("""
            DROP TYPE IF EXISTS interview_type CASCADE;
            DROP TYPE IF EXISTS email_classification CASCADE;
            DROP TYPE IF EXISTS prompt_task CASCADE;
            DROP TYPE IF EXISTS application_status CASCADE;
            DROP TYPE IF EXISTS job_source CASCADE;
            DROP TYPE IF EXISTS job_status CASCADE;
            DROP TYPE IF EXISTS skill_category CASCADE;
            DROP TYPE IF EXISTS degree_type CASCADE;
            DROP TYPE IF EXISTS experience_type CASCADE;
        """))
        
        # Drop extensions (optional, comment out if shared with other DBs)
        # await conn.execute(text("DROP EXTENSION IF EXISTS pg_trgm CASCADE;"))
        # await conn.execute(text("DROP EXTENSION IF EXISTS pgcrypto CASCADE;"))
        # await conn.execute(text("DROP EXTENSION IF EXISTS \"uuid-ossp\" CASCADE;"))
    
    print("✅ Schema dropped successfully")


async def create_schema(engine):
    """Execute schema SQL file."""
    print(f"📝 Creating schema from {SCHEMA_FILE}...")
    
    if not SCHEMA_FILE.exists():
        print(f"❌ Schema file not found: {SCHEMA_FILE}")
        sys.exit(1)
    
    schema_sql = SCHEMA_FILE.read_text()
    
    async with engine.begin() as conn:
        # Split by statement (rough approach, works for most SQL)
        statements = [s.strip() for s in schema_sql.split(";") if s.strip()]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    await conn.execute(text(statement))
                except Exception as e:
                    print(f"⚠️  Warning executing statement {i}: {e}")
                    # Continue with other statements
    
    print("✅ Schema created successfully")


async def seed_data(engine):
    """Seed database with default/test data."""
    print("🌱 Seeding database with default data...")
    
    async with engine.begin() as conn:
        # Create default user
        await conn.execute(text("""
            INSERT INTO users (email, password_hash, full_name, is_active, email_verified)
            VALUES (
                'user@example.com',
                '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ooYh/8Y7Kh.C',  -- 'password123'
                'Test User',
                TRUE,
                TRUE
            )
            ON CONFLICT (email) DO NOTHING
            RETURNING id;
        """))
        
        result = await conn.execute(text("SELECT id FROM users WHERE email = 'user@example.com';"))
        user_row = result.fetchone()
        
        if not user_row:
            print("❌ Failed to create user")
            return
        
        user_id = str(user_row[0])
        print(f"✅ Created user: user@example.com (ID: {user_id})")
        
        # Create default prompt templates
        prompts = [
            {
                "task": "resume_tailor",
                "role": "backend_engineer",
                "name": "Backend Engineer Resume Optimization",
                "prompt": """You are an expert resume writer specializing in backend engineering roles.
                
Your task: Optimize this resume for a backend engineering position at a tech company.

Guidelines:
- Emphasize backend technologies, system design, and scalability
- Quantify achievements with metrics (e.g., "reduced latency by 40%")
- Use strong action verbs (designed, implemented, optimized, architected)
- Highlight relevant technologies from the job description
- Maintain executive-level professional tone
- Keep bullet points concise and impactful

Master Resume:
{master_resume}

Job Description:
{job_description}

Return the optimized resume as JSON with the same structure as the input."""
            },
            {
                "task": "cover_letter",
                "role": "backend_engineer",
                "name": "Backend Engineer Cover Letter",
                "prompt": """You are an expert career advisor writing executive-level cover letters.

Your task: Write a persuasive cover letter for this backend engineering position.

Guidelines:
- Professional, confident tone (not overly formal or casual)
- 3-4 paragraphs maximum
- Opening: Express genuine interest in the company/role
- Body: Highlight 2-3 relevant achievements with impact
- Closing: Strong call to action
- Avoid clichés like "I am a perfect fit" or "I am passionate"
- Show, don't tell (use specific examples)

Candidate Resume:
{resume}

Job Description:
{job_description}

Company Info:
{company_name}

Return the cover letter as plain text (no JSON)."""
            }
        ]
        
        for prompt_data in prompts:
            await conn.execute(text("""
                INSERT INTO prompt_templates (
                    user_id, task_type, role_type, name, prompt_text, 
                    is_system_prompt, version, is_active
                )
                VALUES (
                    :user_id, :task_type, :role_type, :name, :prompt_text,
                    FALSE, 1, TRUE
                )
                ON CONFLICT DO NOTHING;
            """), {
                "user_id": user_id,
                "task_type": prompt_data["task"],
                "role_type": prompt_data["role"],
                "name": prompt_data["name"],
                "prompt_text": prompt_data["prompt"]
            })
        
        print(f"✅ Created {len(prompts)} default prompt templates")
        
        # Create sample job posting
        await conn.execute(text("""
            INSERT INTO job_postings (
                user_id, company_name, job_title, job_url, source,
                location, employment_type, remote_policy, status,
                job_description, interest_level
            )
            VALUES (
                :user_id,
                'TechCorp Inc.',
                'Senior Backend Engineer',
                'https://techcorp.com/careers/senior-backend-engineer',
                'manual',
                'San Francisco, CA',
                'Full-time',
                'Hybrid',
                'saved',
                'We are looking for a Senior Backend Engineer to join our team...',
                5
            )
            ON CONFLICT DO NOTHING;
        """), {"user_id": user_id})
        
        print("✅ Created sample job posting")
    
    print("✅ Database seeded successfully")


async def verify_schema(engine):
    """Verify schema was created correctly."""
    print("🔍 Verifying schema...")
    
    async with engine.begin() as conn:
        # Check if key tables exist
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result.fetchall()]
        
        expected_tables = [
            'users', 'master_resumes', 'work_experiences', 'education',
            'skills', 'certifications', 'job_postings', 'resume_versions',
            'prompt_templates', 'applications', 'cover_letters',
            'credentials', 'email_threads', 'interview_events',
            'analytics_snapshots'
        ]
        
        missing = set(expected_tables) - set(tables)
        
        if missing:
            print(f"⚠️  Missing tables: {missing}")
        else:
            print(f"✅ All {len(tables)} tables created successfully")
            
        # Check extensions
        result = await conn.execute(text("""
            SELECT extname FROM pg_extension 
            WHERE extname IN ('uuid-ossp', 'pgcrypto', 'pg_trgm');
        """))
        
        extensions = [row[0] for row in result.fetchall()]
        print(f"✅ Extensions enabled: {', '.join(extensions)}")


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Initialize Personal AI Job Assistant database"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing schema before creating"
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Seed database with default data"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify schema, don't create"
    )
    parser.add_argument(
        "--database-url",
        default=DATABASE_URL,
        help="Database connection URL"
    )
    
    args = parser.parse_args()
    
    print("🚀 Personal AI Job Assistant - Database Initialization")
    print(f"📍 Database URL: {args.database_url.split('@')[1]}")  # Hide credentials
    print()
    
    # Create engine
    engine = create_async_engine(args.database_url, echo=False)
    
    try:
        if args.verify_only:
            await verify_schema(engine)
            return
        
        if args.drop:
            await drop_schema(engine)
        
        await create_schema(engine)
        await verify_schema(engine)
        
        if args.seed:
            await seed_data(engine)
        
        print()
        print("✨ Database initialization complete!")
        print()
        print("Next steps:")
        print("  1. Update DATABASE_URL in your .env file")
        print("  2. Create a master resume via API or web interface")
        print("  3. Start adding job postings")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
