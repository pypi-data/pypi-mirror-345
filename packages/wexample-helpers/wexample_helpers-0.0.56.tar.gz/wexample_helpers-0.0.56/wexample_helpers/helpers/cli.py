from typing import Union


def cli_make_clickable_path(path: str, short_title: Union[bool, str] = False) -> str:
    from pathlib import Path

    if isinstance(short_title, str):
        display_text = short_title
    elif short_title:
        display_text = Path(path).name
    else:
        display_text = path

    # \033]8;;file://{path}\033\\  : Link start
    # \033]8;;\033\\              : Link end
    return f"\033]8;;file://{path}\033\\{display_text}\033]8;;\033\\"
