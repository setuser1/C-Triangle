# i++ Language Reference

<p align="center">
  <img src="../assets/logo.png" alt="i++ Logo" width="180"/>
</p>

Welcome to the official documentation for the **i++ (i++)** programming language and the **Hypotenuse Compiler**.

---

## Quick Start

```bash
# Install dependencies
make install

# Compile a i++ source file
python3 src/main.py hello.ix

# Debug: view tokens and scope graph
python3 src/main.py -t hello.ix

# Print structure graph
python3 src/main.py -p hello.ix
```

---

## Documents

| File                               | Description                                                      |
| ---------------------------------- | ---------------------------------------------------------------- |
| [keywords.md](keywords.md)         | Full keyword and operator reference                              |
| [syntax.md](syntax.md)             | Complete syntax guide with examples                              |
| [types.md](types.md)               | Type system — primitives, auto, string, dynam, tuple, typed structs |
| [memory.md](memory.md)             | Memory model — allocate, free, autoremove, robbery               |
| [assembly.md](assembly.md)         | Inline assembly — asm blocks, syntax targets, rules              |
| [stdlib.md](stdlib.md)             | Standard library (iodine) — printd, printfs, len, error handling  |
| [compiler.md](compiler.md)         | Compiler architecture, pipeline stages, and CLI reference        |
| [errors.md](errors.md)             | Error reference — all compiler and runtime errors                |

---

## About i++

i++ is a systems programming language that extends C11 with modern features while maintaining 100% C11 compatibility (minus a small deprecated list). It compiles to C and assembly, using GCC and NASM to produce native Linux ELF x86_64 binaries.

i++ is designed around three principles:

- **Explicit over implicit** — nothing happens without you knowing about it
- **Simple over clever** — clean syntax that stays close to C's spirit
- **Extensible over fixed** — the language can grow itself through libraries

The compiler is called **The Hypotenuse Compiler**. Detailed documentation is available at:
<https://hypotenuse.mintlify.app>

The compiler source is available at:
<https://github.com/setuser1/The-Hypotenuse-Compiler>
