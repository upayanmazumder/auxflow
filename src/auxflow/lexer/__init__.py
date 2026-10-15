"""Phase 2: lexical analysis.

Category-code tokenizer (codes 0-15), comment and verbatim handling.
Modules: catcode, tokens, scanner. See docs/COMPILER-PIPELINE.md section 1.
"""

from __future__ import annotations

from auxflow.lexer.catcode import CATEGORY_TABLE, CatCode, catcode_of
from auxflow.lexer.scanner import tokenize
from auxflow.lexer.tokens import Token

__all__ = ["CATEGORY_TABLE", "CatCode", "Token", "catcode_of", "tokenize"]
