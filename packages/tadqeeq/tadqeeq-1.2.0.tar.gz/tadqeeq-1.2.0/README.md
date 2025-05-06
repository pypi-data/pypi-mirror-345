# Tadqeeq – Image Annotator Tool

An interactive image annotation tool built with **PyQt5**, designed for efficient labeling of **segmentation masks** and **bounding boxes**.

> Developed by **Mohamed Behery** @ RTR Software Development - An "Orbits" Subsidiary
> 📅 April 30, 2025
> 🪪 Licensed under the MIT License

---

## 🚀 Features

- ✅ **Minimalist Interactive Design**
- 🖌️ **Scroll through label classes / Adjust pen size** with the mouse wheel
- 🎨 **Supports segmentation masks (.png)** and **bounding boxes (.txt)**
- 🧠 **Dynamic label color generation** (HSV-based)
- 💬 **Floating labels** showing hovered and selected classes
- 💾 **Auto-save** and **manual save** (Ctrl+S)
- 🧽 **Flood-fill segmentation**
- 🚫 **Middle-click erase mode** and **double-click to clear all**

---

## 📦 Installation

### Option 1: Install via pip

```bash
pip install tadqeeq
```

### Option 2: Run from source

```bash
git clone https://github.com/orbits-it/tadqeeq.git
cd tadqeeq
pip install -r requirements.txt
```

---

## 🛠️ Usage

### Import in your code:

```python
from tadqeeq import ImageAnnotator
```

### Run demo from command line (if installed via pip):

```bash
tadqeeq path/to/image.jpg path/to/annotations[.png|.txt]
```

> **Note:**
> If the annotations file is PNG one, the tool uses **segmentation masks** with class-labeled pixels on a white background.  
> If it's a `.txt` file, it uses **YOLO-style bounding boxes** formatted as:  
>> `label_index x_offset y_offset width height`

---

## 🧭 Controls

| Action                  | Mouse/Key |
|-------------------------|-----------|
| Draw / Fill segment     | Left-click / double-click |
| Erase (one object)      | Right-click + Left-click |
| Toggle erase mode       | Right-click |
| Clear all               | Double right-click |
| Scroll through labels / Adjust pen size   | Mouse wheel |
| Save annotations        | Ctrl+S |
| Show label on hover     | Hover cursor |

---

## 📁 Project Structure

```plaintext
root/
├── tadqeeq/
|   ├── __init__.py         # Entry point for importing
|   ├── widgets.py          # Contains ImageAnnotator class
|   ├── utils.py            # Helper methods (flood fill, bounding box logic)
|   ├── cli.py              # Optional CLI entry point
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
└── requirements.txt
```

---

## 🧑‍💻 Contributing

[Repository](https://github.com/orbits-it/tadqeeq.git)

Pull requests are welcome!  
If you add features (e.g. COCO export, brush tools, batch processing), please document them in the README.

---

## 📄 License

This project is licensed under the **MIT License**.  
See [LICENSE](./LICENSE) for the full license text.

---

## 💡 Acknowledgements

🎉 Built for computer vision practitioners needing fast, mouse-based labeling with clean overlays and autosave logic.

🌟 Special thanks to **PyQt5** for providing the powerful and flexible GUI toolkit that made the development of this interactive image annotator possible.

---

## 🔗 Related Resources

- [PyQt5 Docs](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [NumPy](https://numpy.org/)
- [scikit-image](https://scikit-image.org/)
- [SciPy](https://scipy.org/)
