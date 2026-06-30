# models.py

from pydantic import BaseModel, Field
from typing import List


# =====================================
# REQUEST
# =====================================

class CandidateRequest(BaseModel):

    job_description: str = Field(
        ...,
        min_length=1
    )

    top_k: int = Field(
        default=10,
        ge=1,
        le=100
    )


# =====================================
# CANDIDATE RESPONSE
# =====================================

class CandidateResponse(BaseModel):

    candidate_id: str = ""

    current_title: str = ""

    years_experience: float = 0

    industry: str = ""

    location: str = ""

    skill_names: List[str] = []

    profile_score: float = 0

    jd_score: float = 0

    final_score: float = 0

    matched_skills: List[str] = []

    missing_skills: List[str] = []

    explanation: str = ""


# =====================================
# API RESPONSE
# =====================================

class RankingResponse(BaseModel):

    success: bool

    count: int

    top_candidates: List[CandidateResponse]