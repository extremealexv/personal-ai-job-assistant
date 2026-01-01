"""Cover letter model - re-exported from job.py for backward compatibility.

Note: The CoverLetter class is now defined in app.models.job
to keep related models together. This file exists only for backward compatibility
with existing imports.
"""

# Re-export from the canonical location
from app.models.job import CoverLetter

__all__ = ["CoverLetter"]
