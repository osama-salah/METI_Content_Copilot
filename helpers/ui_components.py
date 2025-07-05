"""
UI components for the RoboGarden Instructor Copilot.
This module imports and exports all the tab components.
"""

# Import all tab components from their respective modules
from ui.course_architect import course_architect_tab
from ui.content_reviewer import content_reviewer_tab
from ui.future_proofing import future_proofing_tab
from ui.quiz_creator import quiz_creator_tab
from ui.full_course_generator import full_course_generator_tab

# Export all tab functions for backward compatibility
__all__ = [
    'course_architect_tab',
    'content_reviewer_tab',
    'future_proofing_tab',
    'quiz_creator_tab',
    'full_course_generator_tab'
]
