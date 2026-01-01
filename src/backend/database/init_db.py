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
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment variables from .env file in project root
# Path: src/backend/database/init_db.py
#   .parent -> src/backend/database/
#   .parent.parent -> src/backend/
#   .parent.parent.parent -> src/
#   .parent.parent.parent.parent -> project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
    print(f"📍 Loaded environment from: {ENV_FILE}")
else:
    print(f"⚠️  No .env file found at: {ENV_FILE}")
    print("   Using environment variables or defaults")

# Try to load from environment first, fall back to default
DATABASE_URL = os.getenv(
    "DATABASE_ASYNC_URL", "postgresql+asyncpg://postgres:password@localhost:5432/ai_job_assistant"
)

# Show which database we're connecting to (without password)
if "@" in DATABASE_URL:
    db_info = DATABASE_URL.split("@")[1]
    user_info = DATABASE_URL.split("//")[1].split("@")[0].split(":")[0]
    print(f"🔌 Connecting as user: {user_info} to {db_info}")

# Path to schema SQL file
SCHEMA_FILE = Path(__file__).parent / "schema.sql"


async def check_connection(engine=None):
    """Test database connection."""
    should_dispose = False
    if engine is None:
        engine = create_async_engine(DATABASE_URL, echo=False)
        should_dispose = True

    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ Database connected: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    finally:
        if should_dispose:
            await engine.dispose()


async def drop_schema(engine):
    """Drop all tables and types."""
    print("🗑️  Dropping existing schema...")

    # List of tables to drop (in reverse dependency order)
    tables = [
        "analytics_snapshots",
        "interview_events",
        "email_threads",
        "credentials",
        "cover_letters",
        "applications",
        "resume_versions",
        "prompt_templates",
        "job_postings",
        "certifications",
        "skills",
        "education",
        "work_experiences",
        "master_resumes",
        "users",
    ]

    # List of types to drop
    types = [
        "interview_type",
        "email_classification",
        "prompt_task",
        "application_status",
        "job_source",
        "job_status",
        "skill_category",
        "degree_type",
        "experience_type",
    ]

    async with engine.begin() as conn:
        # Drop tables one by one
        for table in tables:
            try:
                await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            except Exception as e:
                print(f"⚠️  Warning dropping table {table}: {e}")

        # Drop types one by one
        for type_name in types:
            try:
                await conn.execute(text(f"DROP TYPE IF EXISTS {type_name} CASCADE"))
            except Exception as e:
                print(f"⚠️  Warning dropping type {type_name}: {e}")

    print("✅ Schema dropped successfully")


async def create_schema(engine):
    """Execute schema SQL file."""
    print(f"📝 Creating schema from {SCHEMA_FILE}...")

    if not SCHEMA_FILE.exists():
        print(f"❌ Schema file not found: {SCHEMA_FILE}")
        sys.exit(1)

    schema_sql = SCHEMA_FILE.read_text()

    # Execute using raw asyncpg connection to handle multi-statement SQL
    async with engine.connect() as conn:
        # Get the raw asyncpg connection
        raw_conn = await conn.get_raw_connection()

        try:
            # Execute the entire SQL file - asyncpg's execute() handles multiple statements
            await raw_conn.driver_connection.execute(schema_sql)
            print("✅ Schema created successfully")
        except Exception as e:
            print(f"❌ Error creating schema: {e}")
            raise


async def seed_data(engine):
    """Seed database with default/test data."""
    print("🌱 Seeding database with default data...")

    async with engine.begin() as conn:
        # Create default user
        await conn.execute(
            text(
                """
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
        """
            )
        )

        result = await conn.execute(text("SELECT id FROM users WHERE email = 'user@example.com';"))
        user_row = result.fetchone()

        if not user_row:
            print("❌ Failed to create user")
            return

        user_id = str(user_row[0])
        print(f"✅ Created user: user@example.com (ID: {user_id})")

        # Create default prompt templates
        prompts = [
            # Backend Engineer Templates
            {
                "task": "resume_tailor",
                "role": "backend_engineer",
                "name": "Backend Engineer Resume Optimizer",
                "prompt": """You are an expert resume writer specializing in backend engineering positions at top tech companies. Your goal is to optimize the candidate's resume for a specific job posting while maintaining authenticity and ATS compatibility.

ROLE CONTEXT:
- Target Role: Backend Engineer / Senior Backend Engineer
- Key Technologies: [Will be extracted from job description]
- Optimization Goal: Maximize relevance and impact

OPTIMIZATION GUIDELINES:

1. Impact & Metrics (Highest Priority):
   - Quantify every achievement with specific numbers
   - Scale: users served, requests handled, data volume processed
   - Performance: latency improvements, throughput gains, cost reductions
   - Team impact: people mentored, cross-functional collaborations

2. Technical Skills Alignment:
   - Match job requirements with candidate's experience
   - Highlight relevant languages, frameworks, and tools
   - Emphasize distributed systems, scalability, and performance work
   - Showcase system design and architecture experience

3. Executive Positioning:
   - Use strong action verbs: Architected, Scaled, Optimized, Led, Designed
   - Focus on business impact alongside technical achievements
   - Demonstrate problem-solving and technical leadership

4. ATS Optimization:
   - Include exact keyword matches from job description
   - Use standard section headers (Work Experience, Education, Technical Skills)
   - Maintain consistent formatting

5. Content Strategy:
   - Reorder bullet points by relevance to target role
   - Expand highly relevant experience, condense less relevant
   - Add context for lesser-known companies or projects

INPUT:
Master Resume: {master_resume}
Job Description: {job_description}
Target Company: {company_name}

OUTPUT FORMAT:
Return optimized resume as JSON with this structure:
{
  "summary": "2-3 sentence executive summary tailored to role",
  "work_experience": [...],
  "skills": {...},
  "education": [...],
  "changes_made": ["Explanation of major changes..."]
}

CRITICAL RULES:
- NEVER fabricate experience, dates, or achievements
- NEVER change company names or employment dates
- MAINTAIN factual accuracy - all claims must be defensible""",
            },
            {
                "task": "cover_letter",
                "role": "backend_engineer",
                "name": "Backend Engineer Cover Letter",
                "prompt": """You are an expert cover letter writer specializing in executive-level communication for backend engineering roles. Craft a compelling, personalized cover letter that demonstrates genuine interest and strong fit.

INPUT CONTEXT:
- Candidate Background: {resume_summary}
- Target Company: {company_name}
- Target Role: {job_title}
- Job Description: {job_description}

STRUCTURE:

Opening (2-3 sentences):
- Strong hook showing genuine interest in company's mission/products
- Brief relevant background statement
- Clear intent to apply for specific role

Body Paragraph 1 - Relevant Experience:
- 1-2 most impressive achievements directly relevant to role
- Specific technical examples with quantifiable results
- Demonstrate understanding of role's technical challenges

Body Paragraph 2 - Company Alignment:
- Research into company culture, products, engineering blog
- Connect personal interests to company's mission
- Explain why THIS opportunity specifically

Body Paragraph 3 - Unique Value:
- What you uniquely bring beyond resume
- Leadership, mentorship, or collaboration examples
- Forward-looking vision for impact

Closing:
- Confident expression of interest
- Thank you for consideration

GUIDELINES:
- Tone: Professional, confident, enthusiastic (not desperate)
- Length: 300-400 words (3-4 paragraphs)
- Specificity: Use company name, specific products, role title
- Authenticity: Avoid generic praise

AVOID:
- Clichés like "I am a perfect fit"
- Restating entire resume
- Desperate or apologetic language
- Typos or formatting errors

OUTPUT: Complete cover letter as plain text, ready for submission.""",
            },
            # Data Scientist Template
            {
                "task": "resume_tailor",
                "role": "data_scientist",
                "name": "Data Scientist Resume Optimizer",
                "prompt": """You are an expert resume writer specializing in data science and machine learning positions. Optimize this resume for maximum impact.

OPTIMIZATION FOCUS:

1. Quantifiable Impact:
   - Model performance: accuracy, precision, recall, F1, AUC improvements
   - Business metrics: revenue impact, cost savings, efficiency gains
   - Scale: dataset sizes, processing throughput

2. Technical Skills:
   - ML frameworks: TensorFlow, PyTorch, scikit-learn
   - Programming: Python, R, SQL
   - Data engineering: Spark, Airflow, Kafka
   - Cloud ML: AWS SageMaker, GCP Vertex AI, Azure ML

3. Research & Academic:
   - Publications, conferences, patents
   - Kaggle competitions
   - Open-source contributions

INPUT:
Master Resume: {master_resume}
Job Description: {job_description}

OUTPUT: Optimized resume as JSON emphasizing data-driven achievements.

RULES: Never exaggerate metrics, distinguish personal vs team contributions.""",
            },
            # Full Stack Template
            {
                "task": "resume_tailor",
                "role": "fullstack_engineer",
                "name": "Full Stack Engineer Resume Optimizer",
                "prompt": """You are an expert resume writer for full stack positions. Optimize to showcase both frontend and backend expertise.

FOCUS:
- Frontend: React, Vue, Angular, TypeScript, responsive design
- Backend: Node.js, Python, Java, databases, APIs, microservices
- DevOps: CI/CD, Docker, Kubernetes
- End-to-end feature ownership

INPUT:
Master Resume: {master_resume}
Job Description: {job_description}

OUTPUT: Optimized resume as JSON with balanced full-stack emphasis.""",
            },
            # VP of Technology
            {
                "task": "resume_tailor",
                "role": "vp_technology",
                "name": "VP of Technology Resume Optimizer",
                "prompt": """You are an expert resume writer specializing in executive technology leadership positions. Optimize this resume for VP of Technology or CTO-track roles.

EXECUTIVE LEADERSHIP FOCUS:

1. Strategic Technology Vision:
   - Technology strategy aligned with business objectives
   - Digital transformation initiatives and outcomes
   - Innovation programs and R&D leadership
   - Technology roadmap development and execution
   - Build vs buy decisions and their business impact

2. Organizational Leadership:
   - Team size and structure (engineering, product, infrastructure)
   - Leadership development and succession planning
   - Engineering culture and talent strategy
   - Cross-functional collaboration (product, sales, operations)
   - Executive stakeholder management (CEO, board, investors)

3. Business Impact & Metrics:
   - Revenue enabled by technology initiatives
   - Cost optimization through technology (infrastructure, operations)
   - Time-to-market improvements
   - System reliability and uptime achievements
   - Technology debt reduction initiatives

4. Technical Excellence:
   - Architecture decisions and their business justification
   - Modernization of legacy systems
   - Cloud migration strategy and execution
   - Security and compliance leadership
   - Scalability achievements (users, transactions, data volume)

5. Budget & Resource Management:
   - Technology budget size and management
   - Vendor relationships and negotiations
   - ROI on technology investments
   - Resource allocation and prioritization

INPUT:
Master Resume: {master_resume}
Job Description: {job_description}
Target Company: {company_name}

OUTPUT: Optimized resume emphasizing strategic leadership, business impact, and organizational influence.

CRITICAL: Focus on business outcomes, not just technical achievements. Demonstrate board-level communication skills.""",
            },
            # Head of IT Infrastructure
            {
                "task": "resume_tailor",
                "role": "head_it_infrastructure",
                "name": "Head of IT Infrastructure Resume Optimizer",
                "prompt": """You are an expert resume writer specializing in IT infrastructure leadership roles. Optimize for Head of Infrastructure, Director of Infrastructure, or VP Infrastructure Engineering positions.

INFRASTRUCTURE LEADERSHIP FOCUS:

1. Infrastructure Strategy & Architecture:
   - Data center strategy (on-prem, cloud, hybrid)
   - Cloud platform management (AWS, Azure, GCP)
   - Network architecture and capacity planning
   - Disaster recovery and business continuity
   - Infrastructure modernization roadmaps

2. Reliability & Performance:
   - System uptime and availability (99.9%+)
   - Incident reduction and MTTR improvements
   - Performance optimization initiatives
   - Capacity planning and growth management
   - Scalability achievements (traffic, users, data)

3. Cost Management:
   - Infrastructure cost optimization (cloud spend, licensing)
   - TCO reduction initiatives
   - Vendor management and negotiations
   - Budget forecasting and management
   - Resource utilization improvements

4. Security & Compliance:
   - Security posture improvements
   - Compliance certifications (SOC 2, ISO 27001, HIPAA, PCI-DSS)
   - Vulnerability management and remediation
   - Security incident response and prevention
   - Identity and access management

5. Team & Operations:
   - Team size and structure (infrastructure, SRE, network, security)
   - On-call rotation and incident response
   - Automation and infrastructure as code
   - Monitoring and observability platforms
   - Documentation and knowledge management

6. Technology Stack:
   - Virtualization (VMware, Hyper-V)
   - Containerization (Docker, Kubernetes)
   - Configuration management (Ansible, Terraform, Chef, Puppet)
   - Monitoring tools (Datadog, Splunk, Prometheus, Grafana)
   - CI/CD pipeline infrastructure

INPUT:
Master Resume: {master_resume}
Job Description: {job_description}

OUTPUT: Optimized resume emphasizing reliability, cost efficiency, and infrastructure excellence.

METRICS TO HIGHLIGHT: Uptime %, cost savings, incident reduction, capacity increases, automation gains.""",
            },
            # Head of IT Operations
            {
                "task": "resume_tailor",
                "role": "head_it_operations",
                "name": "Head of IT Operations Resume Optimizer",
                "prompt": """You are an expert resume writer specializing in IT operations leadership. Optimize for Head of IT Operations, Director of Operations, or VP of IT Operations roles.

IT OPERATIONS LEADERSHIP FOCUS:

1. Operational Excellence:
   - Service level achievement (SLA/SLO compliance)
   - Incident and problem management
   - Change management success rates
   - Mean time to resolution (MTTR) improvements
   - Operational efficiency metrics

2. Service Delivery:
   - End-user satisfaction scores
   - Service desk/help desk leadership
   - IT service catalog management
   - Request fulfillment processes
   - Service availability and reliability

3. Process & Governance:
   - ITIL framework implementation
   - Standard operating procedures (SOPs)
   - Quality assurance and audits
   - Change advisory board (CAB) leadership
   - Risk management and mitigation

4. Team Leadership:
   - Operations team size and structure
   - 24/7 operations coverage
   - Training and skill development
   - Performance management
   - Vendor and contractor management

5. Automation & Tools:
   - IT operations automation (runbooks, scripts)
   - Monitoring and alerting platforms
   - Ticketing systems (ServiceNow, Jira Service Management)
   - Asset and configuration management
   - Self-service portal implementation

6. Business Continuity:
   - Disaster recovery planning and testing
   - Business continuity procedures
   - High availability design
   - Backup and recovery operations
   - Crisis management and communication

7. Cost & Budget:
   - Operations budget management
   - Cost per ticket/incident optimization
   - Tool consolidation and rationalization
   - Outsourcing vs in-house decisions

INPUT:
Master Resume: {master_resume}
Job Description: {job_description}

OUTPUT: Optimized resume emphasizing operational excellence, service delivery, and continuous improvement.

KEY METRICS: SLA compliance %, MTTR, incident volume reduction, user satisfaction scores, cost per ticket.""",
            },
            # Head of ITSM
            {
                "task": "resume_tailor",
                "role": "head_itsm",
                "name": "Head of ITSM Resume Optimizer",
                "prompt": """You are an expert resume writer specializing in IT Service Management leadership. Optimize for Head of ITSM, ITSM Manager, or Service Management Director roles.

ITSM LEADERSHIP FOCUS:

1. ITIL Framework Expertise:
   - ITIL v3/v4 implementation and maturity
   - Service strategy and design
   - Service transition and operations
   - Continual service improvement (CSI)
   - ITIL certification level (Foundation, Practitioner, Expert, Master)

2. Service Management Processes:
   - Incident management optimization
   - Problem management and root cause analysis
   - Change management and CAB effectiveness
   - Service request fulfillment
   - Configuration management database (CMDB)
   - Asset and license management
   - Knowledge management

3. Service Metrics & Reporting:
   - Service level achievement (SLA compliance)
   - First call resolution (FCR) rates
   - Customer satisfaction scores (CSAT)
   - Mean time to resolution (MTTR)
   - Change success rates
   - Service availability and uptime
   - KPI dashboards and executive reporting

4. Service Improvement:
   - Process maturity assessments
   - Gap analysis and remediation
   - Process automation initiatives
   - Service catalog development
   - Self-service capabilities
   - Continuous improvement programs

5. Tools & Technology:
   - ITSM platform expertise (ServiceNow, BMC Remedy, Jira Service Management)
   - Integration with monitoring tools
   - Workflow automation
   - Reporting and analytics tools
   - AI/ML for ticket routing and resolution

6. Stakeholder Management:
   - Service owner relationships
   - Business unit partnerships
   - Vendor and supplier management
   - Executive communication and reporting
   - Customer service excellence

7. Team & Culture:
   - ITSM team leadership and development
   - Service desk optimization
   - Training and certification programs
   - Process documentation and standards
   - Service-oriented culture development

INPUT:
Master Resume: {master_resume}
Job Description: {job_description}

OUTPUT: Optimized resume emphasizing ITIL expertise, process maturity, and service excellence.

CERTIFICATIONS TO HIGHLIGHT: ITIL, COBIT, ISO 20000, PMP, Six Sigma.
KEY METRICS: SLA compliance, MTTR, FCR, CSAT, change success rate, incident volume trends.""",
            },
            # IT Product Owner
            {
                "task": "resume_tailor",
                "role": "it_product_owner",
                "name": "IT Product Owner Resume Optimizer",
                "prompt": """You are an expert resume writer specializing in IT Product Owner and Product Management roles. Optimize for Product Owner, Technical Product Manager, or IT Product Manager positions.

PRODUCT OWNERSHIP FOCUS:

1. Product Strategy & Vision:
   - Product roadmap development and execution
   - Product vision and strategy alignment with business goals
   - Market research and competitive analysis
   - User needs assessment and validation
   - Product-market fit achievements

2. Stakeholder Management:
   - Executive stakeholder communication
   - Cross-functional team collaboration (engineering, design, sales, support)
   - Customer and user engagement
   - Vendor and partner relationships
   - Expectation management and alignment

3. Agile & Delivery:
   - Scrum/Agile methodology expertise
   - Sprint planning and backlog prioritization
   - User story writing and acceptance criteria
   - Release planning and coordination
   - Velocity and burndown optimization
   - Agile certifications (CSPO, SAFe PO/PM)

4. Requirements & Analysis:
   - Requirements gathering and documentation
   - Business analysis and process mapping
   - User journey mapping and personas
   - Data-driven decision making
   - A/B testing and experimentation

5. Product Success Metrics:
   - User adoption and engagement rates
   - Feature usage analytics
   - Customer satisfaction (NPS, CSAT)
   - Time to market improvements
   - ROI and business value delivered
   - Retention and churn metrics

6. Technical Acumen:
   - Understanding of technical architecture
   - API and integration knowledge
   - Cloud platforms and SaaS products
   - Security and compliance requirements
   - Technical debt management

7. Business Impact:
   - Revenue impact of product features
   - Cost reduction through automation
   - Efficiency gains and productivity improvements
   - Market share or competitive advantages gained
   - Customer retention improvements

INPUT:
Master Resume: {master_resume}
Job Description: {job_description}
Target Company: {company_name}

OUTPUT: Optimized resume balancing product strategy, technical knowledge, and business outcomes.

KEY SKILLS: Product roadmap, backlog management, stakeholder communication, Agile/Scrum, data analysis.
METRICS TO HIGHLIGHT: User adoption %, NPS scores, feature delivery velocity, business value delivered, ROI.""",
            },
            # Head of Engineering
            {
                "task": "resume_tailor",
                "role": "head_engineering",
                "name": "Head of Engineering Resume Optimizer",
                "prompt": """You are an expert resume writer specializing in senior engineering leadership roles. Optimize for Head of Engineering, VP of Engineering, or Engineering Director positions.

ENGINEERING LEADERSHIP FOCUS:

1. Engineering Organization:
   - Team size and structure (backend, frontend, mobile, QA, DevOps)
   - Organizational design and scaling
   - Engineering levels and career ladders
   - Hiring and talent acquisition strategy
   - Retention and employee satisfaction

2. Engineering Culture & Excellence:
   - Engineering culture development
   - Code quality standards and practices
   - Technical debt management strategy
   - Innovation programs and hackathons
   - Learning and development initiatives
   - Diversity, equity, and inclusion efforts

3. Delivery & Execution:
   - Product delivery velocity and reliability
   - Sprint planning and agile practices
   - Release frequency and quality
   - On-time delivery rates
   - Feature adoption and success metrics
   - Technical roadmap execution

4. Technical Leadership:
   - Architecture decisions and oversight
   - Technology stack choices and rationale
   - System scalability achievements
   - Performance optimization initiatives
   - Security and reliability improvements
   - Technical debt reduction programs

5. Process & Methodology:
   - Agile/Scrum implementation
   - CI/CD pipeline development
   - Code review practices
   - Testing strategy (unit, integration, E2E)
   - Incident response and postmortems
   - Documentation standards

6. Cross-Functional Collaboration:
   - Product-engineering partnership
   - Design-engineering collaboration
   - Engineering-sales/support alignment
   - Executive communication and reporting
   - Stakeholder expectation management

7. Business Impact:
   - Engineering efficiency improvements
   - Time to market reduction
   - Cost optimization through automation
   - System reliability (uptime, performance)
   - Technical enablement of business growth
   - Revenue-impacting feature delivery

8. Leadership & People:
   - 1-on-1s and performance management
   - Mentorship and coaching
   - Team health and engagement scores
   - Engineering manager development
   - Conflict resolution and team dynamics

INPUT:
Master Resume: {master_resume}
Job Description: {job_description}
Target Company: {company_name}

OUTPUT: Optimized resume emphasizing people leadership, technical excellence, and business impact.

BALANCE: 40% people/culture, 30% technical delivery, 30% business outcomes.
KEY METRICS: Team size, delivery velocity, uptime %, time to market, employee retention, engagement scores.""",
            },
            # Generic Fallback
            {
                "task": "resume_tailor",
                "role": None,
                "name": "General Professional Resume Optimizer",
                "prompt": """You are an expert resume writer optimizing for any professional role. Tailor this resume to the specific job description.

UNIVERSAL GUIDELINES:
1. Achievement Focus: Every bullet demonstrates impact
2. Quantification: Use numbers, percentages, scales
3. Action Verbs: Led, Developed, Achieved, Optimized
4. Relevance: Prioritize experience matching job
5. ATS Optimization: Include keywords naturally
6. Professional Tone: Executive-level confidence

INPUT:
Master Resume: {master_resume}
Job Description: {job_description}

OUTPUT: Optimized resume as JSON.
MAINTAIN: Factual accuracy, original dates, verifiable claims.""",
            },
        ]

        for prompt_data in prompts:
            await conn.execute(
                text(
                    """
                INSERT INTO prompt_templates (
                    user_id, task_type, role_type, name, prompt_text,
                    is_system_prompt, version, is_active
                )
                VALUES (
                    :user_id, :task_type, :role_type, :name, :prompt_text,
                    FALSE, 1, TRUE
                )
                ON CONFLICT DO NOTHING;
            """
                ),
                {
                    "user_id": user_id,
                    "task_type": prompt_data["task"],
                    "role_type": prompt_data["role"],
                    "name": prompt_data["name"],
                    "prompt_text": prompt_data["prompt"],
                },
            )

        print(f"✅ Created {len(prompts)} default prompt templates")

        # Create sample job posting
        await conn.execute(
            text(
                """
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
        """
            ),
            {"user_id": user_id},
        )

        print("✅ Created sample job posting")

    print("✅ Database seeded successfully")


async def verify_schema(engine):
    """Verify schema was created correctly."""
    print("🔍 Verifying schema...")

    async with engine.begin() as conn:
        # Check if key tables exist
        result = await conn.execute(
            text(
                """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """
            )
        )

        tables = [row[0] for row in result.fetchall()]

        expected_tables = [
            "users",
            "master_resumes",
            "work_experiences",
            "education",
            "skills",
            "certifications",
            "job_postings",
            "resume_versions",
            "prompt_templates",
            "applications",
            "cover_letters",
            "credentials",
            "email_threads",
            "interview_events",
            "analytics_snapshots",
        ]

        missing = set(expected_tables) - set(tables)

        if missing:
            print(f"⚠️  Missing tables: {missing}")
        else:
            print(f"✅ All {len(tables)} tables created successfully")

        # Check extensions
        result = await conn.execute(
            text(
                """
            SELECT extname FROM pg_extension
            WHERE extname IN ('uuid-ossp', 'pgcrypto', 'pg_trgm');
        """
            )
        )

        extensions = [row[0] for row in result.fetchall()]
        print(f"✅ Extensions enabled: {', '.join(extensions)}")


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Initialize Personal AI Job Assistant database")
    parser.add_argument("--drop", action="store_true", help="Drop existing schema before creating")
    parser.add_argument("--seed", action="store_true", help="Seed database with default data")
    parser.add_argument(
        "--verify-only", action="store_true", help="Only verify schema, don't create"
    )
    parser.add_argument("--database-url", default=DATABASE_URL, help="Database connection URL")

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
