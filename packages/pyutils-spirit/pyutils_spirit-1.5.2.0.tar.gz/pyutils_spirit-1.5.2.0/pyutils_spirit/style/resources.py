# @Coding: UTF-8
# @Time: 2024/9/22 0:27
# @Author: xieyang_ls
# @Filename: resources.py
from time import sleep

from pyutils_spirit.style.color import RESET


class Resources:
    __spirit_banner = """
     ░█████████              ░███              ░█████         ░███████████
    ░███░░░░░███             ░░░               ░░███          ░█░░░███░░░█
    ░███    ░░░   ░███████  ░████  ░████████    ░███          ░   ░███  ░
    ░░█████████  ░░███░░███ ░░███  ░░███░░███   ░███              ░███
     ░░░░░░░░███  ░███ ░███  ░███   ░███ ░░░    ░███              ░███
     ███    ░███  ░███ ░███  ░███   ░███        ░███              ░███
    ░░█████████   ░███████  ░█████ ░█████      ░█████ ░█████████ ░█████
                  ░███
                  ░███
                 ░█████
    :: SpirI_T Utils ::                                           (v1.1.0)
                                                     
    """

    __websocket_banner = """
    ░█████  ░███  ░█████         ░█████      ░█████████                      ░█████                 ░█████
    ░░███   ░███  ░░███          ░░███       ███░░░░░███                     ░░███                  ░░███
     ░███   ░███   ░███  ░██████  ░███████  ░███    ░░░   ░██████   ░██████   ░███░█████  ░██████  ░███████
     ░███   ░███   ░███ ░███░░███ ░███░░███ ░░█████████  ░███░░███ ░███░░███  ░███░░███  ░███░░███ ░░░███░
     ░░███  █████  ███  ░███████  ░███ ░███  ░░░░░░░░███ ░███ ░███ ░███ ░░░   ░██████░   ░███████    ░███
      ░░░█████░█████░   ░███░░░   ░███ ░███  ███    ░███ ░███ ░███ ░███  ███  ░███░░███  ░███░░░     ░███ ███
        ░░███ ░░███     ░░██████  ████████  ░░█████████  ░░██████  ░░██████   ████ █████ ░░██████    ░░█████
    :: WebSocket Server ::                                                                           (v1.1.1)
         
    """

    @classmethod
    def set_spirit_banner(cls, spirit_banner):
        cls.__spirit_banner = spirit_banner

    @classmethod
    def set_websocket_banner(cls, websocket_banner):
        cls.__websocket_banner = websocket_banner

    @classmethod
    def draw_spirit_banner(cls, timeout: float = 0.1, color: str = RESET):
        for text_line in cls.__spirit_banner.splitlines():
            print(f"{color}{text_line}{RESET}")
            sleep(timeout)

    @classmethod
    def draw_websocket_banner(cls, timeout: float = 0.1, color: str = RESET):
        for text_line in cls.__websocket_banner.splitlines():
            print(f"{color}{text_line}{RESET}")
            sleep(timeout)


set_spirit_banner = Resources.set_spirit_banner

set_websocket_banner = Resources.set_websocket_banner

draw_spirit_banner = Resources.draw_spirit_banner

draw_websocket_banner = Resources.draw_websocket_banner
