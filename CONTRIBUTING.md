# 🤝 Contributing Guide

Thank you for your interest in contributing to this project! Contributions are welcome and appreciated. This document outlines the process to help you contribute effectively and professionally.

---

## 📌 Table of Contents

* Code of Conduct
* How to Contribute
* Development Setup
* Branching Strategy
* Commit Guidelines
* Pull Request Process
* Reporting Issues
* Feature Requests

---

## 🧭 Code of Conduct

Be respectful and professional in all interactions.

* No harassment or offensive language
* Respect different opinions and approaches
* Provide constructive feedback

---

## 🚀 How to Contribute

You can contribute in several ways:

* Fix bugs
* Improve UI/UX
* Add new features
* Improve documentation
* Optimize performance

---

## ⚙️ Development Setup

1. Fork the repository

2. Clone your fork:

   ```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
   ```

3. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Run the project:

   ```bash
   uvicorn main:app --reload
   ```

---

## 🌿 Branching Strategy

* `main` → Stable production-ready code
* `develop` → Active development (if used)
* Feature branches:

  ```
  feature/your-feature-name
  fix/bug-description
  ```

Example:

```bash
git checkout -b feature/markdown-rendering
```

---

## 📝 Commit Guidelines

Use clear and meaningful commit messages.

### Format:

```
type: short description
```

### Examples:

```
feat: add markdown rendering support
fix: resolve UI rendering issue
refactor: optimize note generation service
docs: update contributing guide
```

---

## 🔄 Pull Request Process

1. Push your branch:

   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a Pull Request (PR)

3. Ensure:

   * Code is clean and readable
   * No unnecessary files are included
   * Proper comments/documentation added

4. PR should include:

   * What changes were made
   * Why they were made
   * Screenshots (if UI changes)

---

## 🐛 Reporting Issues

When reporting bugs, include:

* Clear title
* Steps to reproduce
* Expected behavior
* Actual behavior
* Screenshots/logs (if applicable)

---

## 💡 Feature Requests

For new ideas:

* Explain the problem
* Describe your proposed solution
* Mention alternatives (if any)

---

## ✅ Best Practices

* Follow project structure
* Keep code modular and clean
* Write reusable functions
* Avoid hardcoding values
* Test your changes before submitting

---

## 🙌 Final Note

Your contributions help improve this project and make it better for everyone.
Thank you for taking the time to contribute!

---
