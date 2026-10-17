"""
High level parse handling for C∆ Compiler.
"""

import os
import sys
import error_msgs

from parser import (
    Alloc,
    ArrayAccess,
    ArrayDesignation,
    Assignment,
    Binary,
    Comma,
    Break,
    Call,
    Cast,
    Compound,
    CompoundLiteral,
    Continue,
    Declaration,
    Define,
    DesignatedInit,
    Do,
    ExposeDecl,
    ExprStmt,
    FieldAccess,
    For,
    Free,
    Function,
    Generic,
    Goto,
    If,
    Include,
    InitList,
    Label,
    LibAccess,
    Literal,
    Return,
    SpaceDecl,
    StructDef,
    Switch,
    Typedef,
    TypeExpr,
    Unary,
    UsingDecl,
    Var,
    While,
)

#will be revised to clean out library stuff that are needed in higher.py
class front:
    def __init__(self, ast, source_path=None):
        self.ast = ast
        self.source_path = source_path  # path to source file for plib lookup

        self._is_plib_source = source_path and source_path.endswith(".plib")  # Direct plib compilation
        self._pending_plibs = []  # Store pending plib ASTs for tree-shaking

        self._specific_imports = {}  # item -> (lib_name, namespace)
        self._scoped_var_imports = {}  # imported name -> (owner, symbol, generated name)
        self._current_alias = {}  # lib_name -> alias
        self._alias_to_lib = {}  # Maps alias (e.g., "lib") -> actual lib name (e.g., "mylib")
        self._folder_libs = {}  # Maps folder alias -> list of plib names (e.g., "lib" -> ["plstd/streamer", "plstd/other"])
        self._namespace_imported_libs = set()  # Track libs imported as full namespaces
        self._standard_libs = set()  # Plib filenames loaded from the standard library folder

        self._exposed_libs = set()  # Set of exposed library names
        self._exposed_funcs = {}  # Maps bare_name -> lib_name for exposed functions
        self._space_prefix_map = {}  # Maps space name -> actual prefix (e.g., "math" -> "lib_math")
        self._top_level_lib_functions = {}  # Maps lib_name -> set of top-level function names

        self._used_functions = set()  # Track used function names for tree-shaking

"""
higher.py should only track libraries, mid.py will be the one handling them.
Library tracking will be a separare class from the other stuff.
"""
