"""Phases 7-10: static analysis.

Content-quantity taint propagation, iterative Tarjan SCC, stable-pass fixpoint on
the condensation, four-state classifier. Must not import auxflow.ast: anything an
analysis needs belongs in the IR. See docs/STATIC-ANALYSIS.md.
"""
