"""Application model - re-exported from job.py for backward compatibility.

Note: The Application and ApplicationStatus classes are now defined in app.models.job
to keep related models together. This file exists only for backward compatibility
with existing imports.
"""

# Re-export from the canonical location
from app.models.job import Application, ApplicationStatus

__all__ = ["Application", "ApplicationStatus"]
