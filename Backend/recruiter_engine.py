# recruiter_engine.py

from pathlib import Path
from functools import lru_cache
import json
import re
from typing import Dict, Set


# =====================================================
# CONFIG
# =====================================================
PROFILE_WEIGHT = 0.20
JD_WEIGHT = 0.80

BASE_DIR = Path(__file__).resolve().parent

POSSIBLE_DATA_FILES = [
    BASE_DIR / "scored_candidates.json",
    BASE_DIR.parent / "scored_candidates.json",
    BASE_DIR.parent / "data" / "scored_candidates.json",
    BASE_DIR.parent / "dataset" / "scored_candidates.json",
]


# =====================================================
# MASTER SKILLS
# =====================================================

MASTER_SKILLS = {

    # Programming
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",

    # Frontend
    "react",
    "reactjs",
    "react.js",
    "angular",
    "vue",
    "html",
    "css",
    "bootstrap",
    "tailwind",
    "nextjs",
    "next.js",

    # Backend
    "nodejs",
    "node.js",
    "express",
    "fastapi",
    "django",
    "flask",
    "spring",
    "spring boot",

    # Database
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",

    # AI / ML
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "statistics",
    "data science",
    "nlp",
    "computer vision",

    # LLM / GenAI
    "llm",
    "llms",
    "generative ai",
    "prompt engineering",
    "fine-tuning llms",

    # Retrieval / Search
    "retrieval",
    "rag",
    "ranking",
    "search",
    "semantic search",
    "vector database",
    "vector db",
    "recommendation systems",
    "faiss",
    "pinecone",
    "weaviate",
    "langchain",
    "haystack",
    "opensearch",
    "sentence transformers",

    # Computer Vision
    "opencv",
    "yolo",

    # Experimentation
    "weights & biases",

    # Cloud / DevOps
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",

    # Data
    "pandas",
    "numpy",
    "spark",

    # Leadership
    "leadership",
    "management",
    "manager",
    "team lead",
    "mentor",
    # LLM / GenAI
    "prompt engineering",
    "fine-tuning llms",
    "llm",
    "generative ai",

    # Retrieval
    "opensearch",
    "sentence transformers",

    # NLP / CV
    "opencv",
    "yolo",

    # Experimentation
    "weights & biases",
}
# =====================================================
# SKILL NORMALIZATION
# =====================================================

ALIASES = {
    "reactjs": "react",
    "react.js": "react",
    "nextjs": "next.js",
    "nodejs": "node.js",
    "llms": "llm",
    "vector db": "vector database",
}


# =====================================================
# SEMANTIC SKILL MAP
# =====================================================

SEMANTIC_MAP = {

    "machine learning": {
        "tensorflow",
        "pytorch",
        "scikit-learn",
        "deep learning",
        "ai",
    },

    "statistics": {
        "machine learning",
        "data science",
        "pandas",
        "numpy",
    },

    "rag": {
        "langchain",
        "faiss",
        "pinecone",
        "weaviate",
        "haystack",
    },

    "frontend": {
        "react",
        "javascript",
        "html",
        "css",
    },
}
# =====================================================
# LOAD CANDIDATES
# =====================================================

@lru_cache(maxsize=1)
def load_candidates():

    data_file = None

    for path in POSSIBLE_DATA_FILES:
        if path.exists():
            data_file = path
            break

    if data_file is None:

        searched = "\n".join(
            str(p)
            for p in POSSIBLE_DATA_FILES
        )

        raise FileNotFoundError(
            "Could not locate "
            "scored_candidates.json\n\n"
            f"Searched:\n{searched}"
        )

    print(
        f"\nLoaded candidate file:\n"
        f"{data_file}"
    )

    with open(
        data_file,
        "r",
        encoding="utf-8"
    ) as f:

        candidates = json.load(f)

    if not isinstance(candidates, list):
        raise ValueError(
            "scored_candidates.json "
            "must contain a list"
        )

    print(
        f"Loaded "
        f"{len(candidates)} "
        f"candidates"
    )

    return candidates


# =====================================================
# JD PARSER
# =====================================================
def extract_jd_requirements(
    job_description: str
) -> Set[str]:

    if not job_description:
        return set()

    jd = job_description.lower()

    jd = re.sub(
        r"[^a-z0-9+#.\s]",
        " ",
        jd
    )

    tokens = set(
        jd.split()
    )

    detected = set()

    for skill in MASTER_SKILLS:

        normalized = ALIASES.get(
            skill,
            skill
        )

        if " " in skill:

            if skill in jd:
                detected.add(
                    normalized
                )

        else:

            if skill in tokens:
                detected.add(
                    normalized
                )

    print(
        "\nDetected Skills:",
        sorted(detected)
    )

    return detected


# =====================================================
# JD MATCHER
# =====================================================

def calculate_jd_score(
    candidate: Dict,
    requirements: Set[str]
):

    if not requirements:
        return 0.0, [], []

    candidate_skills = {

        str(skill).lower()

        for skill in candidate.get(
            "skill_names",
            []
        )
    }

    matched = set()

    # direct matching
    matched.update(
        candidate_skills.intersection(
            requirements
        )
    )
    # semantic matching
    for req in requirements:

        if req in SEMANTIC_MAP:

            semantic_skills = (
                SEMANTIC_MAP[req]
            )

            if any(
                skill in candidate_skills
                for skill in semantic_skills
            ):
                matched.add(req)

    # python feature
    if (
        candidate.get("has_python")
        and "python" in requirements
    ):
        matched.add("python")

    # ml feature
    ml_terms = {
        "machine learning",
        "deep learning",
        "tensorflow",
        "pytorch",
        "ai",
        "data science",
        "nlp",
    }

    if (
        candidate.get("has_ml")
        and any(
            x in requirements
            for x in ml_terms
        )
    ):
        matched.update(
            requirements.intersection(
                ml_terms
            )
        )

    # retrieval feature
    retrieval_terms = {
        "retrieval",
        "rag",
        "ranking",
        "search",
        "semantic search",
        "vector database",
        "vector db",
        "recommendation systems",
        "faiss",
        "pinecone",
        "weaviate",
        "langchain",
        "haystack",
    }

    if (
        candidate.get(
            "has_retrieval_experience"
        )
        and any(
            x in requirements
            for x in retrieval_terms
        )
    ):
        matched.update(
            requirements.intersection(
                retrieval_terms
            )
        )

    # leadership feature
    leadership_terms = {
        "leadership",
        "management",
        "manager",
        "team lead",
        "mentor",
    }

    if (
        candidate.get(
            "has_leadership"
        )
        and any(
            x in requirements
            for x in leadership_terms
        )
    ):
        matched.update(
            requirements.intersection(
                leadership_terms
            )
        )

    missing = (
        requirements
        - matched
    )

    score = (
        len(matched)
        / len(requirements)
    ) * 100

    return (
        round(score, 2),
        sorted(list(matched)),
        sorted(list(missing)),
    )


# =====================================================
# EXPLAINABILITY
# =====================================================

def generate_explanation(
    matched,
    missing
):

    return (
        f"Matched "
        f"{len(matched)} "
        f"skills. "
        f"Missing "
        f"{len(missing)} "
        f"skills."
    )


# =====================================================
# MAIN ENGINE
# =====================================================

def get_top_candidates(
    job_description: str,
    top_k: int = 10
):

    candidates = load_candidates()

    requirements = (
        extract_jd_requirements(
            job_description
        )
    )

    
    ranked = []

    for candidate in candidates:

        profile_score = float(
            candidate.get(
                "final_score",
                0
            )
        )

        (
            jd_score,
            matched,
            missing,
        ) = calculate_jd_score(
            candidate,
            requirements
        )

        final_score = (

            profile_score
            * PROFILE_WEIGHT

            +

            jd_score
            * JD_WEIGHT
        )

        ranked.append({

            "candidate_id":
                candidate.get(
                    "candidate_id",
                    ""
                ),

            "current_title":
                candidate.get(
                    "current_title",
                    ""
                ),

            "years_experience":
                candidate.get(
                    "years_experience",
                    0
                ),

            "industry":
                candidate.get(
                    "industry",
                    ""
                ),

            "location":
                candidate.get(
                    "location",
                    ""
                ),

            "skill_names":
                candidate.get(
                    "skill_names",
                    []
                ),

            "profile_score":
                round(
                    profile_score,
                    2
                ),

            "jd_score":
                jd_score,

            "final_score":
                round(
                    final_score,
                    2
                ),

            "matched_skills":
                matched,

            "missing_skills":
                missing,

            "explanation":
                generate_explanation(
                    matched,
                    missing
                ),
        })

    ranked.sort(
        key=lambda x:
        x["final_score"],
        reverse=True
    )

    return ranked[:top_k]


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    jd = """
    AI Engineer

    Skills:
    Python
    LangChain
    FAISS
    Pinecone
    RAG
    """

    result = get_top_candidates(
        jd,
        top_k=5
    )

    for r in result:

        print(
            r["candidate_id"],
            r["jd_score"],
            r["final_score"],
            r["matched_skills"]
        )