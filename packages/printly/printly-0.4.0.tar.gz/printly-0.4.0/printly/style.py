"""Defines styling-related functions: `style()`, `unstyle()`"""

import re
from typing import Iterator, Optional, Tuple
from .types import Color, FontStyle
from .validate import validate_color, validate_font_style
from .const import COMBINATOR, COLORS_RGB_MAP, FONT_STYLE_CODES, HEX_PREFIX, RGB_DELIMITER, RESET


def get_rgb_values(color: Color) -> Tuple[int, ...]:
    """Gets the RGB values of a color."""
    color = validate_color(color)
    if color.startswith(HEX_PREFIX):
        return tuple(int(color[1:][i : i + 2], base=16) for i in range(0, 6, 2))
    if RGB_DELIMITER in color:
        return tuple(map(int, color.split(RGB_DELIMITER)))
    return COLORS_RGB_MAP[color]


def get_font_style_codes(font_style: FontStyle) -> Iterator[int]:
    """Gets the code number of a font style."""
    yield from (FONT_STYLE_CODES[validate_font_style(f)] for f in font_style.split(COMBINATOR))


def style(
    text: str,
    fg: Optional[Color] = None,
    bg: Optional[Color] = None,
    fs: Optional[FontStyle] = None,
) -> str:
    """
    Applies foreground color, background color, and font style to text.

    Args:
        text (str): The text to be styled.
        fg (Color | None): Foreground color for the text. Defaults to `None`.
        bg (Color | None): Background color for the text. Defaults to `None`.
        fs (FontStyle | None): Font style(s) for the text. Defaults to `None`.

    Returns:
        str: Styled text.
    """
    if fg or bg or fs:
        fg_code = f"\033[38;2;{';'.join(map(str, get_rgb_values(fg)))}m" if fg else ""
        bg_code = f"\033[48;2;{';'.join(map(str, get_rgb_values(bg)))}m" if bg else ""
        fs_code = "".join((f"\033[{c}m" for c in get_font_style_codes(fs))) if fs else ""
        styles = fg_code + bg_code + fs_code
        styled_text = styles + text.replace(RESET, f"{RESET}{styles}")
        styled_text = styled_text.replace("\n", f"{RESET}\n{styles}")
        return styled_text + (RESET if not styled_text.endswith(RESET) else "")
    return text


def unstyle(text: str) -> str:
    """Removes printly styles from styled text."""
    return re.sub(
        "(\033\\[(0|1|3|4|8|9|21|53)m|\033\\[(38|48);2;(\\d{,3};){2}\\d{,3}m)", "", f"{text}"
    )
