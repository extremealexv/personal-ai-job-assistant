#!/usr/bin/env python3
"""
Script to set up the test database.

This script creates the test database and applies the schema.
Run this before executing pytest for the first time.

Usage:
    python scripts/setup_test_db.py [--drop]
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.models.base import Base


async def setup_test_database(drop_existing: bool = False) -> None:
    """Set up the test database."""
    # Extract database name from URL
    database_async_url = str(settings.database_url).replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    
    # Parse database name
    try:
        base_url, db_name = database_async_url.rsplit("/", 1)
    except ValueError:
        print("❌ Error: Could not parse database URL")
        sys.exit(1)
    
    test_db_name = f"{db_name}_test"
    test_database_url = f"{base_url}/{test_db_name}"
    
    print(f"🔧 Setting up test database: {test_db_name}")
    
    # Connect to postgres database to create test database
    postgres_url = f"{base_url}/postgres"
    engine = create_async_engine(postgres_url, isolation_level="AUTOCOMMIT")
    
    try:
        async with engine.begin() as conn:
            # Check if database exists
            result = await conn.execute(
                text(
                    "SELECT 1 FROM pg_database WHERE datname = :db_name"
                ),
                {"db_name": test_db_name}
            )
            db_exists = result.scalar() is not None
            
            if db_exists:
                if drop_existing:
                    print(f"🗑️  Dropping existing database: {test_db_name}")
                    # Terminate existing connections
                    await conn.execute(
                        text(
                            "SELECT pg_terminate_backend(pg_stat_activity.pid) "
                            "FROM pg_stat_activity "
                            "WHERE pg_stat_activity.datname = :db_name "
                            "AND pid <> pg_backend_pid()"
                        ),
                        {"db_name": test_db_name}
                    )
                    await conn.execute(text(f'DROP DATABASE "{test_db_name}"'))
                    print(f"✅ Dropped database: {test_db_name}")
                else:
                    print(f"ℹ️  Database already exists: {test_db_name}")
                    print("   Use --drop to recreate it")
                    await engine.dispose()
                    return
            
            # Create database
            print(f"📦 Creating database: {test_db_name}")
            await conn.execute(text(f'CREATE DATABASE "{test_db_name}"'))
            print(f"✅ Created database: {test_db_name}")
    
    finally:
        await engine.dispose()
    
    # Connect to test database and create tables
    print(f"📋 Creating tables in {test_db_name}...")
    test_engine = create_async_engine(
        test_database_url,
        echo=False,
        pool_pre_ping=True
    )
    
    try:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Verify tables were created
        async with test_engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = 'public'"
                )
            )
            table_count = result.scalar()
            print(f"✅ Created {table_count} tables")
        
        print(f"🎉 Test database setup complete!")
        print(f"\nYou can now run tests with: pytest")
    
    finally:
        await test_engine.dispose()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Set up the test database for pytest"
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop existing test database if it exists"
    )
    
    args = parser.parse_args()
    
    try:
        asyncio.run(setup_test_database(drop_existing=args.drop))
    except Exception as e:
        print(f"\n❌ Error setting up test database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
