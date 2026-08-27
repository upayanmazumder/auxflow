"""Phases 11-12: optimisation and build-plan generation.

Four optimisation passes and lowering to a BuildPlan. The safety invariant -- never
emit a plan shorter than the conservative default unless CERTIFIED -- is implemented
here and enforced by a property test. See docs/BUILD-PLANNER.md.
"""
