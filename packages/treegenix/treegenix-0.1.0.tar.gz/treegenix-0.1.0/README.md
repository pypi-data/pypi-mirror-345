````markdown
# 🌳 treegrenix

**treegrenix** is a lightweight Python CLI tool to beautifully display the directory structure of your projects or folders — just like the classic `tree` command but written in Python, customizable and clean.

---

## ✨ Features

- 📁 Generate a visual tree structure of any folder
- ❌ Exclude specific files or folders (like `venv`, `__pycache__`, etc.)
- 💻 Simple command-line usage
- 🧼 Ignores hidden files and folders by default
- 🛠️ Open-source and MIT licensed

---

## 🔧 Installation

You can install `treegrenix` directly from [PyPI](https://pypi.org/project/treegrenix/):

```bash
pip install treegrenix
````

---

## 🚀 Usage

After installation, use the CLI tool with the command:

```bash
treegenix [path] [--exclude item1 item2 ...]
```

### 🔹 Examples

#### 1. View the tree of the current directory:

```bash
treegenix
```

#### 2. View the tree of a specific folder:

```bash
treegenix my_project/
```

#### 3. Exclude specific files or folders:

```bash
treegenix . --exclude venv __pycache__
```

This will generate output like:

````bash
```
my_project/
├── app/
│   ├── __init__.py
│   └── main.py
├── README.md
└── requirements.txt
```
````

---

## 💡 Why use treegrenix?

* Great for README file directory listings
* Simple and Pythonic — no external C-based tools required
* Customizable via command-line options

---

## 🛠️ Development

Clone the repo if you'd like to contribute:

```bash
git clone https://github.com/sujal-1245/treegrenix.git
cd treegrenix
python -m treegenix .
```

---

## 🗿 Made by

**Sujal Bhagat**
[GitHub](https://github.com/sujal-1245)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

```

---

MIT License

Copyright (c) 2023 Sujal Bhagat
```
