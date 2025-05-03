 # 📁 directoryFinder_mac

`directoryFinder_mac` is a simple Python library that helps developers **search for files or folders path by name** using fuzzy matching logic inside specific directories (like Desktop, Documents, Downloads, etc.) on macOS.

It is especially useful in **voice-assisted developer tools** where interacting with the file system through speech is required.

---

## 🔧 Installation

```bash
pip install directoryFinder_mac
```

# 🚀Example Usage

```bash
from directoryFinder_mac import find_file_in_dirs

results = find_file_in_dirs("file_name", ["Desktop", "Documents"], cutoff=0.7)
print(results)
```
# Output
```bash
['/Users/yourname/Desktop/file_name', '/Users/yourname/Documents/file_name']
```



---
# ⚙️Parameters
`find_file_in_dirs(file_name, folder_names, cutoff=0.7)` 
* file_name (str, required):
The name of the file or folder you're searching for. Matching is case-insensitive and fuzzy.

* folder_names (list, required):
List of directories relative to the home directory to search in. Example: ["Desktop", "Downloads"] for mac.

* cutoff (float, optional):
Fuzzy matching threshold between 0 and 1. Default is 0.7. Higher means stricter matching.

---
### 🔍 **How It Works – Fuzzy Matching Logic**

Often while using **speech recognition**, minor misinterpretations can occur. For example:

- You say: `recognition dot pi`  
- Actual file: `recognition.py`

These types of small inconsistencies (like “dot pi” instead of “.py”) are common due to voice transcription errors or human inaccuracies.

To address this, `directoryFinder_mac` uses **fuzzy matching** behind the scenes. Fuzzy matching doesn’t require an exact match — instead, it finds the **closest possible match** to your spoken or typed input using a similarity score.

You can also control the **tolerance level** using the `cutoff` parameter:

- `cutoff=1.0` → Only exact matches
- `cutoff=0.7` → Allows more relaxed matches (default)

---

`Note`: If there are mutiple folders or files with same name then you need to check my library `directorySelector` for handling it.