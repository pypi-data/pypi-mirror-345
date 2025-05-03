"""Type definitions for the markdown translator."""

from dataclasses import dataclass
from enum import Enum
from typing import Awaitable, Callable, Optional


class TranslationStatus(Enum):
    """Status codes for translation progress."""

    PREPARING = "preparing"
    TRANSLATING = "translating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TranslationProgress:
    """Progress information for translation tasks."""

    status: TranslationStatus
    current: int
    total: int
    current_file: Optional[str] = None
    message: Optional[str] = None


ProgressCallback = Callable[[TranslationProgress], Awaitable[None]]
