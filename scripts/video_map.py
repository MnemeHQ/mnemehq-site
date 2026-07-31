"""slug -> (video_id, is_core) for click-to-load video facades.

VideoObject JSON-LD is maintained only on dedicated video-first demo pages and
is not generated for concept or insight pages.
"""

VIDEO_MAP = {
    # --- Concept/insight pages: facade only; no VideoObject schema ---
    "concepts/architectural-compiler": ("jNXDtxu0_-s", True),
    "concepts/architectural-drift": ("hP8jMyVA6D4", True),
    "concepts/governance-before-generation": ("tO_Z9rqXXfQ", True),
    "concepts/precedence-semantics": ("tktp6ik0Gxk", True),
    "insights/ai-native-engineering-intent-debt": ("nwSBZXolBhA", True),
    "insights/barbara-liskov-python-encapsulation-ai-governance": ("qAKrMdUycb8", True),
    "insights/architectural-governance-across-heterogeneous-ai-coding-agents": ("xtTDcb2JB2c", True),
    "insights/autonomous-code-remediation-requires-architectural-governance": ("DDo0x1lkBNI", True),
    "insights/github-copilot-space-framework": ("Rjlzm0psfB4", True),
    "insights/harness-engineering-still-needs-governance": ("kHDZshGw7M8", True),
    "insights/memory-is-not-governance": ("EDBVYFtkOb4", True),
    "insights/prompt-engineering-is-not-governance": ("kIswxPe7bGc", True),
    "insights/why-claude-md-stops-scaling": ("5QxAbdLg0nw", True),
    "insights/why-code-review-cannot-scale-with-ai-output": ("8sklibjfO6A", True),
    "insights/why-observability-is-not-governance": ("yAwz5SISip8", True),
    "insights/why-rag-fails-for-architectural-governance": ("0kC4OEG-yig", True),
    # --- Additional concept/insight pages: facade only ---
    "insights/rag-is-not-memory": ("4EbbZojgWKs", False),
    "insights/spec-driven-development-still-needs-governance": ("pcL4fD5MyC8", False),
    "insights/why-context-alone-doesnt-prevent-architectural-drift": ("fseagcnHzhU", False),
    "concepts/model-independent-governance": ("W4MG-SQY20o", False),
    "concepts/deterministic-enforcement": ("k5lpI83ONnI", False),
}
