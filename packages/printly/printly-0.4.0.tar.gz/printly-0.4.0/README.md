# Printly
Printly is a Python library that enhances the built-in print function with direct text styling: foreground color (`fg`), background color (`bg`), and font styles (`fs`).

## Features
- **Colors:**
  - Supports over 140 color names ([from HTML](https://htmlcolorcodes.com/color-names/))
  - Supports all RGB values (e.g., `"128,0,128"`)
  - Supports all HEX color codes (e.g., `"#ff00ff"`)
- **Font Styles:**
  - Supports 7 font styles: `bold`, `italic`, `strikethrough`, `underline`, `overline`, `double-underline`, and `hide`.
  - Supports combining multiple font styles (e.g., `"bold+italic"`)
- **Compatibility:**
  - Supports all standard `print()` parameters: `sep`, `end`, `file`, and `flush`.

## Installation
```bash
pip install printly
```

## Usage

### 1. `print()` Function
An enhanced version of the built-in `print()` function.

#### Example 1 (Recommended)
```python
import printly
printly.print("Hello, world!", fg="red", bg="white", fs="bold")
```
![image](https://github.com/user-attachments/assets/4286033b-3174-4ae9-90e9-15186db6f005)

#### Example 2 (Override Built-in `print()`)
```python
from printly import print
print("I am a hacker!", fg="lime", bg="black", fs="bold+italic")
```
![image](https://github.com/user-attachments/assets/6d677ffc-55cb-4ab1-909d-ab08a8b15040)

### 2. `style()` Function
Apply foreground color, background color, and font style to text.

#### Example
```python
from printly import style
msg = style("I love you! 💓", bg="hotpink", fg="deeppink", fs="bold")
print(msg)
```
![image](https://github.com/user-attachments/assets/3dfb2bac-c355-4334-bf33-34a7794e4006)
