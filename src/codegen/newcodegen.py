import os
import sys
from typing import Optional

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

TYPE_MAP = {
    "string": "char*",
    "int": "int",
    "float": "float",
    "double": "double",
    "char": "char",
    "void": "void",
    "short": "short",
    "long": "long",
    "signed": "signed",
    "unsigned": "unsigned",
}

DEFAULT_DYNAM_CAPACITY = 4

class CodeGen:
    def __init__(self, ast, structor, layouts=None, source_path=None, target_arch=None):
        self.ast = ast
        self.structor = structor
        self.layouts = layouts or {}
        self.source_path = source_path  # path to source file for plib lookup
        self.target_arch = target_arch
        self._lines = []
        self._indent = 0
        self._specific_imports = {}  # item -> (lib_name, namespace)
        self._scoped_var_imports = {}  # imported name -> (owner, symbol, generated name)
        self._scoped_var_globals = []
        self._emitted_scoped_var_globals = set()
        self._current_function_name = None
        self._current_alias = {}  # lib_name -> alias
        self._generating_plib = False  # Flag to bypass checks when generating plib code
        self._current_lib_name = None  # Current library name for function prefixing
        self._exposed_libs = set()  # Set of exposed library names
        self._collected_includes = set()
        # Track generated dynam helper functions and structs to avoid duplicates
        self._generated_dynam_structs = set()  # Track generated struct types
        self._generated_dynam_funcs = set()  # Track generated helper functions
        self._helper_lines = []  # Store dynam helper functions
        self._dynam_declarations = {}  # Track dynam/string declarations by name -> type
        self._len_int_generated = False  # Track if len_int helper has been generated
        self._ctri_string_helpers_generated = (
            False  # Track if internal string helpers have been generated
        )
        self._ctri_allocator_helpers_generated = (
            False  # Track if internal allocator helpers have been generated
        )
        self._current_space = None  # Current space name when generating inside a space
        self._space_local_functions = set()  # Functions defined in current space
        self._space_prefix_map = {}  # Maps space name -> actual prefix (e.g., "math" -> "lib_math")
        self._alias_to_lib = {}  # Maps alias (e.g., "lib") -> actual lib name (e.g., "mylib")
        self._top_level_lib_functions = {}  # Maps lib_name -> set of top-level function names
        self._exposed_funcs = {}  # Maps bare_name -> lib_name for exposed functions
        self._folder_libs = {}  # Maps folder alias -> list of plib names (e.g., "lib" -> ["iodine/streamer", "iodine/other"])
        self._namespace_imported_libs = set()  # Track libs imported as full namespaces
        self._standard_libs = set()  # Plib filenames loaded from the standard library folder
        self._used_functions = set()  # Track used function names for tree-shaking
        self._pending_plibs = []  # Store pending plib ASTs for tree-shaking
        self._global_dynam_inits = []  # Track global dynam initialization code for main()
        self._plib_global_inits = []  # Track global dynam inits for plib init function
        self._plib_init_funcs = []  # Track plib init function names to auto-call
        self._imported_plib_inits = []  # Track init funcs from imported plibs
        self._plib_inits_called = (
            False  # Track if plib inits have been called in main()
        )
        self._in_global_scope = True  # Track if we're at global scope
        self._dynam_inits_inserted = (
            False  # Track if global dynam inits have been inserted
        )
        self._is_plib_source = source_path and source_path.endswith(
            ".plib"
        )  # Direct plib compilation
        self._asm_blocks = []  # Store asm blocks for later .asm file generation
        # Struct field type tracking: struct_name -> {field_name: field_type}
        self._struct_field_types = {}
        # Variable -> struct type mapping: var_name -> struct_type_name
        self._var_struct_types = {}

    def _ensure_ctri_allocator_helpers(self):
        if self._ctri_allocator_helpers_generated:
            return
        self._ctri_allocator_helpers_generated = True
        self._helper_lines.append("")
        self._helper_lines.append("#define __CTRI_HEAP_SIZE 4194304")
        self._helper_lines.append("#ifdef __aarch64__\n#define __CTRI_HEADER_SIZE 16\n#else\n#define __CTRI_HEADER_SIZE 12\n#endif\n") #test
        self._helper_lines.append("void* __ctri_malloc(int size);")
        self._helper_lines.append("void __ctri_free(void* ptr);")
        self._helper_lines.append("void* __ctri_realloc(void* ptr, int new_size);")
        self._helper_lines.append("static char __ctri_heap[__CTRI_HEAP_SIZE];")
        self._helper_lines.append("")
        self._helper_lines.append("void* __ctri_malloc(int size) {")
        self._helper_lines.append("    int pos = 0;")
        self._helper_lines.append("    size = (size + 7) & ~7;")
        self._helper_lines.append("    if (size <= 0) return (void*)0;")
        self._helper_lines.append("    while (pos < __CTRI_HEAP_SIZE) {")
        self._helper_lines.append(
            "        int* block_size = (int*)(__ctri_heap + pos);"
        )
        self._helper_lines.append(
            "        int* block_free = (int*)(__ctri_heap + pos + sizeof(int));"
        )
        self._helper_lines.append(
            "        int* block_next = (int*)(__ctri_heap + pos + 2 * sizeof(int));"
        )
        self._helper_lines.append("        if (*block_size == 0) {")
        self._helper_lines.append("            *block_size = size;")
        self._helper_lines.append("            *block_free = 0;")
        self._helper_lines.append("            *block_next = 0;")
        self._helper_lines.append(
            "            return (void*)(__ctri_heap + pos + __CTRI_HEADER_SIZE);"
        )
        self._helper_lines.append("        }")
        self._helper_lines.append("        if (*block_free && *block_size >= size) {")
        self._helper_lines.append("            int remaining = *block_size - size;")
        self._helper_lines.append(
            "            if (remaining > (int)(__CTRI_HEADER_SIZE)) {"
        )
        self._helper_lines.append(
            "                int next_pos = pos + __CTRI_HEADER_SIZE + size;"
        )
        self._helper_lines.append(
            "                *(int*)(__ctri_heap + next_pos) = remaining - __CTRI_HEADER_SIZE;"
        )
        self._helper_lines.append(
            "                *(int*)(__ctri_heap + next_pos + sizeof(int)) = 1;"
        )
        self._helper_lines.append(
            "                *(int*)(__ctri_heap + next_pos + 2 * sizeof(int)) = 0;"
        )
        self._helper_lines.append("                *block_next = next_pos;")
        self._helper_lines.append("            }")
        self._helper_lines.append("            *block_free = 0;")
        self._helper_lines.append("            *block_size = size;")
        self._helper_lines.append(
            "            return (void*)(__ctri_heap + pos + __CTRI_HEADER_SIZE);"
        )
        self._helper_lines.append("        }")
        self._helper_lines.append("        if (*block_next == 0) {")
        self._helper_lines.append(
            "            int new_pos = pos + __CTRI_HEADER_SIZE + *block_size;"
        )
        self._helper_lines.append(
            "            if (new_pos + __CTRI_HEADER_SIZE + size > __CTRI_HEAP_SIZE)"
        )
        self._helper_lines.append("                return (void*)0;")
        self._helper_lines.append("            *(int*)(__ctri_heap + new_pos) = size;")
        self._helper_lines.append(
            "            *(int*)(__ctri_heap + new_pos + sizeof(int)) = 0;"
        )
        self._helper_lines.append(
            "            *(int*)(__ctri_heap + new_pos + 2 * sizeof(int)) = 0;"
        )
        self._helper_lines.append("            *block_next = new_pos;")
        self._helper_lines.append(
            "            return (void*)(__ctri_heap + new_pos + __CTRI_HEADER_SIZE);"
        )
        self._helper_lines.append("        }")
        self._helper_lines.append("        pos = *block_next;")
        self._helper_lines.append("    }")
        self._helper_lines.append("    return (void*)0;")
        self._helper_lines.append("}")
        self._helper_lines.append("")
        self._helper_lines.append("void __ctri_free(void* ptr) {")
        self._helper_lines.append("    if (!ptr) return;")
        self._helper_lines.append(
            "    int pos = (int)((char*)ptr - __ctri_heap) - __CTRI_HEADER_SIZE;"
        )
        self._helper_lines.append("    if (pos < 0 || pos >= __CTRI_HEAP_SIZE) return;")
        self._helper_lines.append("    *(int*)(__ctri_heap + pos + sizeof(int)) = 1;")
        self._helper_lines.append(
            "    int* next = (int*)(__ctri_heap + pos + 2 * sizeof(int));"
        )
        self._helper_lines.append("    while (*next != 0) {")
        self._helper_lines.append(
            "        int next_free = *(int*)(__ctri_heap + *next + sizeof(int));"
        )
        self._helper_lines.append("        if (!next_free) break;")
        self._helper_lines.append(
            "        int total = *(int*)(__ctri_heap + pos) + __CTRI_HEADER_SIZE + *(int*)(__ctri_heap + *next);"
        )
        self._helper_lines.append("        *(int*)(__ctri_heap + pos) = total;")
        self._helper_lines.append(
            "        *next = *(int*)(__ctri_heap + *next + 2 * sizeof(int));"
        )
        self._helper_lines.append("    }")
        self._helper_lines.append("}")
        self._helper_lines.append("")
        self._helper_lines.append("void* __ctri_realloc(void* ptr, int new_size) {")
        self._helper_lines.append("    if (!ptr) return __ctri_malloc(new_size);")
        self._helper_lines.append(
            "    int pos = (int)((char*)ptr - __ctri_heap) - __CTRI_HEADER_SIZE;"
        )
        self._helper_lines.append(
            "    if (pos < 0 || pos >= __CTRI_HEAP_SIZE) return (void*)0;"
        )
        self._helper_lines.append("    int old_size = *(int*)(__ctri_heap + pos);")
        self._helper_lines.append("    new_size = (new_size + 7) & ~7;")
        self._helper_lines.append("    if (new_size <= old_size) return ptr;")
        self._helper_lines.append(
            "    int* next = (int*)(__ctri_heap + pos + 2 * sizeof(int));"
        )
        self._helper_lines.append("    if (*next != 0) {")
        self._helper_lines.append(
            "        int next_free = *(int*)(__ctri_heap + *next + sizeof(int));"
        )
        self._helper_lines.append("        if (next_free) {")
        self._helper_lines.append(
            "            int next_size = *(int*)(__ctri_heap + *next);"
        )
        self._helper_lines.append(
            "            int combined = old_size + __CTRI_HEADER_SIZE + next_size;"
        )
        self._helper_lines.append("            if (combined >= new_size) {")
        self._helper_lines.append(
            "                int remaining = combined - new_size;"
        )
        self._helper_lines.append(
            "                *(int*)(__ctri_heap + pos) = new_size;"
        )
        self._helper_lines.append(
            "                if (remaining > (int)(__CTRI_HEADER_SIZE)) {"
        )
        self._helper_lines.append(
            "                    int next_pos = pos + __CTRI_HEADER_SIZE + new_size;"
        )
        self._helper_lines.append(
            "                    *(int*)(__ctri_heap + next_pos) = remaining - __CTRI_HEADER_SIZE;"
        )
        self._helper_lines.append(
            "                    *(int*)(__ctri_heap + next_pos + sizeof(int)) = 1;"
        )
        self._helper_lines.append(
            "                    *(int*)(__ctri_heap + next_pos + 2 * sizeof(int)) = 0;"
        )
        self._helper_lines.append("                    *next = next_pos;")
        self._helper_lines.append("                } else {")
        self._helper_lines.append(
            "                    *next = *(int*)(__ctri_heap + *next + 2 * sizeof(int));"
        )
        self._helper_lines.append("                }")
        self._helper_lines.append("                return ptr;")
        self._helper_lines.append("            }")
        self._helper_lines.append("        }")
        self._helper_lines.append("    }")
        self._helper_lines.append("    void* new_ptr = __ctri_malloc(new_size);")
        self._helper_lines.append("    if (new_ptr == ptr) return ptr;")
        self._helper_lines.append("    if (new_ptr) {")
        self._helper_lines.append("        char* src = (char*)ptr;")
        self._helper_lines.append("        char* dst = (char*)new_ptr;")
        self._helper_lines.append("        int i;")
        self._helper_lines.append(
            "        for (i = 0; i < old_size; i++) dst[i] = src[i];"
        )
        self._helper_lines.append("    }")
        self._helper_lines.append("    __ctri_free(ptr);")
        self._helper_lines.append("    return new_ptr;")
        self._helper_lines.append("}")
        self._helper_lines.append("")

    def _ensure_ctri_string_helpers(self):
        if self._ctri_string_helpers_generated:
            return
        self._ctri_string_helpers_generated = True
        self._ensure_ctri_allocator_helpers()
        self._helper_lines.append("")
        self._helper_lines.append("int __ctri_strlen(char* s) {")
        self._helper_lines.append("    char* p = s;")
        self._helper_lines.append("    while (*p) p++;")
        self._helper_lines.append("    return (int)(p - s);")
        self._helper_lines.append("}")
        self._helper_lines.append("")
        self._helper_lines.append("char* __ctri_strcpy(char* dest, char* src) {")
        self._helper_lines.append("    char* d = dest;")
        self._helper_lines.append("    while ((*d++ = *src++));")
        self._helper_lines.append("    return dest;")
        self._helper_lines.append("}")
        self._helper_lines.append("")
        self._helper_lines.append("char* __ctri_strcat(char* dest, char* src) {")
        self._helper_lines.append("    char* d = dest;")
        self._helper_lines.append("    while (*d) d++;")
        self._helper_lines.append("    while ((*d++ = *src++));")
        self._helper_lines.append("    return dest;")
        self._helper_lines.append("}")
        self._helper_lines.append("")
        self._helper_lines.append("int __ctri_strcmp(char* a, char* b) {")
        self._helper_lines.append("    while (*a && *a == *b) { a++; b++; }")
        self._helper_lines.append("    return (unsigned char)*a - (unsigned char)*b;")
        self._helper_lines.append("}")
        self._helper_lines.append("")
        self._helper_lines.append("char* __ctri_strdup(char* s) {")
        self._helper_lines.append("    int len = __ctri_strlen(s);")
        self._helper_lines.append("    char* d = __ctri_malloc(len + 1);")
        self._helper_lines.append("    if (d) __ctri_strcpy(d, s);")
        self._helper_lines.append("    return d;")
        self._helper_lines.append("}")
        self._helper_lines.append("")