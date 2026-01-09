"""
ARENA - Enumeration Classes
Defines all enum types used in the tournament management system
"""

from enum import Enum


class UserRole(Enum):
    """User roles in the system"""
    OPERATOR = "Operator"
    LEAGUE_OWNER = "League Owner"
    PLAYER = "Player"
    SPECTATOR = "Spectator"
    ADVERTISER = "Advertiser"


class TournamentStatus(Enum):
    """Tournament lifecycle statuses"""
    ANNOUNCED = "Announced"
    OPEN_FOR_REGISTRATION = "Open for Registration"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    ARCHIVED = "Archived"


class MatchStatus(Enum):
    """Match statuses"""
    SCHEDULED = "Scheduled"
    LIVE = "Live"
    COMPLETED = "Completed"
