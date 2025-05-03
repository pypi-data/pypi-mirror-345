# @Coding: UTF-8
# @Time: 2024/9/21 22:56
# @Author: xieyang_ls
# @Filename: __init__.py.py

from pyutils_spirit.style.color import BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET

from pyutils_spirit.style.resources import (set_spirit_banner,
                                            set_websocket_banner,
                                            draw_spirit_banner,
                                            draw_websocket_banner)

__all__ = ["BLACK",
           "RED",
           "GREEN",
           "YELLOW",
           "BLUE",
           "MAGENTA",
           "CYAN",
           "WHITE",
           "RESET",
           "set_spirit_banner",
           "set_websocket_banner",
           "draw_spirit_banner",
           "draw_websocket_banner"]
