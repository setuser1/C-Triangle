# i++ Standard Library (plstd)

<p align="center">
  <img src="../assets/logo.png" alt="i++ Logo" width="120"/>
</p>

**plstd** is the i++ standard library. It is implemented in i++ itself, with `asm` blocks only where syscalls or low-level primitives are needed.

> Unlike C/C++ headers (`.h` / `.hpp`), plstd libraries are written in i++ and can use all i++ features: `dynam` arrays, `typed struct` inheritance, custom types, etc. Libraries share the same language as user code — no separate preprocessor, header syntax, or implementation file needed. A `.ih` is complete and self-contained.

---

## Importing plstd

```c
// Import standard library files by filename
using <printd>;
using <string>;

// Import specific function
using printd from <printd>;

// Explicit access - function@lib syntax
printd@lib("value: %d\n", 42);
```

> The compiler auto-imports what you use — manual imports are optional style.

---

## Output Functions

### `printd(value)` — Type-aware Print

Prints any value, auto-detecting its type.

```c
printd(42);           // prints: 42
printd("hello");    // prints: hello
printd(3.14);        // prints: 3.14
printd('A');         // prints: A
```

---

### `printfs(format, ...)` — Formatted / f-string Print

Supports `{expr}` f-string interpolation and `%`-style format specifiers.

```c
string name = "world";
int x = 42;

printfs("Hello, {name}!\n");       // Hello, world!
printfs("x = %d\n", x);           // x = 42
printfs("{x} squared = {x*x}\n"); // 42 squared = 1764
```

---

## plstd Implementation

- Written entirely in base **i++** + `asm` blocks for syscalls
- Located in `PLIBS/` folder (e.g., `PLIBS/printd.ih`)
- System path: `/usr/lib/PLIBS/`
- User libraries: `~/.local/lib/PLIBS/`

> The `PLIBS/` directory holds all `.ih` library files. User libraries go in `~/.local/lib/PLIBS/`, system libraries in `/usr/lib/PLIBS/`.
