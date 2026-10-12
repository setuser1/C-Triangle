# 🤝 Contributing to C△ and The Hypotenuse Compiler

<p align="center">
  <img src="assets/logo.png" alt="C△ Logo" width="120"/>
</p>

Thank you for your interest in contributing! 🎉 Whether you're fixing bugs, adding features, improving docs, or adding error personality messages — all contributions are welcome.

---

## 🔀 Workflow

1. 🍴 Fork the repository or create a branch from `main`
2. 🔨 Make your changes on a feature branch (e.g. `fix/my-bug`, `feat/new-feature`)
3. ✅ Make sure all tests pass: `make test` - **DO SOME SELF-TESTING BEYOND THE PROVIDED FILES**
4. 📝 Open a **Pull Request** targeting `main` - **MAKE SURE TO ADD TEST RESULTS**
5. 👀 Request review from a maintainer
6. 🎉 Merge after approval!

> ⚠️ `main` is a **protected branch** — direct pushes are not allowed. Always use a PR.

---

## 🌿 Branch Naming

| Prefix      | Purpose                          |
| ----------- | -------------------------------- |
| `fix-issue`     | Bug fixes 🐛                 |
| `feat-feat`     | New features ✨              |
| `refactor-code` | Code restructuring 🔧        |
| `docs-document` | Documentation updates 📝     |
| `assets-asset`  | Images, logos, media 🖼️      |
| `test-check`    | Tests and test infrastructure 🧪 |
| `patch-patch`     | Hotfixes and patches 🩹      |

---

## 🧪 Tests

```bash
make test
```

Tests live in the `test/` directory. Add a test for any bug you fix or feature you add. 🧰

---

## ✍️ Code Style

- Follow PEP-8
- Code like Yoda from Star Wars
- Keep everything safe and tidy
- Comment your code

---

## 📦 Project Structure

```
📁 The-Hypotenuse-Compiler/
├── 📂 src/          ← compiler source (lexer, parser, structurer, main)
├── 📂 docs/         ← language and compiler documentation
├── 📂 test/         ← test files
├── 📂 plstd/        ← plus standard library
├── 📂 assets/       ← logo and media
├── 📄 makefile      ← build and test targets
└── 📄 README.MD     ← project overview
```

---

## 💬 Questions?

Open an **issue** on GitHub and tag it with `question`. We're happy to help! 🙌
