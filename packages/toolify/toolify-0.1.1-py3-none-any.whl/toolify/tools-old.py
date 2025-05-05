import re
import time
import logging
from itertools import cycle
import arabic_reshaper
from bidi.algorithm import get_display

HOW_TO_USE_INFO = """
to use this file in any file use the following lines:

import sys
sys.path.append("/home/workspace/a.abdelsamee/workspace/test_help")
from tools import *

you need to install the following:
pip install python-bidi==0.6.6
pip install arabic_reshaper==3.0.0
"""


COLORS_STR = {
    # Foreground
    "white": "\033[37m",
    "red": "\033[31m",
    "green": "\033[32m",
    "blue": "\033[34m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
    "bred": "\033[91m",
    "bgreen": "\033[92m",
    "bblue": "\033[94m",
    "byellow": "\033[93m",
    "bcyan": "\033[96m",
    "bmagenta": "\033[95m",
    "bwhite": "\033[97m",
    "bblack": "\033[90m",
    # Background
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_blue": "\033[44m",
    "bg_yellow": "\033[43m",
    "bg_cyan": "\033[46m",
    "bg_magenta": "\033[45m",
    "bg_white": "\033[47m",
    "bg_black": "\033[40m",
    "bg_bred": "\033[101m",
    "bg_bgreen": "\033[102m",
    "bg_bblue": "\033[104m",
    "bg_byellow": "\033[103m",
    "bg_bcyan": "\033[106m",
    "bg_bmagenta": "\033[105m",
    "bg_bwhite": "\033[107m",
    "bg_bblack": "\033[100m",
}


COLORS = {
    1: "\033[37m",  # white
    2: "\033[31m",  # red
    3: "\033[32m",  # green
    4: "\033[34m",  # blue
    5: "\033[33m",  # yellow
    6: "\033[36m",  # cyan
    7: "\033[35m",  # magenta
    8: "\033[91m",  # bri_red
    9: "\033[92m",  # bri_green
    10: "\033[94m",  # bri_blue
    11: "\033[93m",  # bri_yellow
    12: "\033[96m",  # bri_cyan
    13: "\033[95m",  # bri_magenta
    14: "\033[97m",  # bri_white
    15: "\033[90m",  # bri_black
}

EMOS = {
    "launch": "🚀",
    "check": "✅",
    "cross": "❌",
    "warn1": "⚠️",
    "warn2": "⛔️",
    "warn3": "🛑",
    "ok": "🆗",
    "done": "✔️",
    "arrow": "⏩",
    "retry": "🔄",
    "fix": "🛠️",
    "lock": "🔒",
    "unlock": "🔓",
    "settings": "⚙️",
    "star": "⭐️",
    "heart": "❤️",
    "fire": "🔥",
    "error": "💥",
    "clock": "🕒",
}

RESET_COLOR = "\033[0m"
DEFAULT_COLOR = "\033[37m"


# print colored text
def pct(text, c=1, emo=""):
    color = COLORS.get(c) or COLORS_STR.get(c)
    emo = EMOS.get(emo)
    if not color:
        color = DEFAULT_COLOR
    if not emo:
        emo = ""
    # bg_color = COLORS.get(bc, "")
    # return f"{color}{bg_color}{text}{COLORS['reset']}"
    print(f"{emo}{color}{text}{RESET_COLOR}")


# print arabic text
def pat(text, c=1, emo=""):
    reshaped_text = arabic_reshaper.reshape(text)
    displayed_text = get_display(reshaped_text)
    pct(displayed_text, c, emo)


# setup a logger for logs
def setup_logger(log_file="log.log", format_type=""):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger

    file_handler = logging.FileHandler(log_file)

    if format_type == "simple":
        formatter = logging.Formatter("%(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    
    file_handler.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(file_handler)
    return logger


def save_text_list(file_name, text_list, mode="w"):
    with open(file_name, mode) as file:
        for array in text_list:
            file.write(" ".join(map(str, array)) + "\n")


def save_text(file_name, text, mode="w"):
    with open(file_name, mode) as file:
        file.write(text + "\n")


def line_plotter(data_list, save_name, legend_list=[], x_values=[], x_label="", y_label="", title="", size=(10, 6)):
    """
    saves a line plot for each list in data_list
    
    Args:
        data_list (list of lists): List of data lists to plot.
        save_name (str): File path to save the plot.
        legend_list (list, optional): List of legend labels for each data list.
            If None, uses default labels ("Line 1", "Line 2", ...).
            If empty ([]), no legend is displayed.
        x_label (str): Label for the x-axis (default: "").
        y_label (str): Label for the y-axis (default: "").
        title (str): Title of the plot (default: "").
        size (tuple): Figure size as (width, height) (default: (10, 6)).
    
    Raises:
        ValueError: 
        1. data_list is empty.
        2. legend_list length doesn't match data_list (when non-empty).
        3. data lists have different sizes.
    """
    
    import matplotlib.pyplot as plt

    if not data_list:
        raise ValueError("data_list cannot be empty")
    if legend_list:
        if len(data_list) != len(legend_list):
            raise ValueError("Length of data_list must match length of legend_list")

    data_lengths = {len(data) for data in data_list}
    if len(data_lengths) > 1:
        raise ValueError("All lists in data_list must have the same size")

    plt.figure(figsize=size)
    if not x_values:
        x_values = range(len(data_list[0]))

    # iterators that endlessly cycles
    colors = cycle(["blue", "red", "green", "purple", "orange", "cyan", "magenta"])
    markers = cycle(["o", "s", "^", "D", "v", "<", ">"])
    linestyles = cycle(["-", "--", ":", "-."])

    for data, color, marker, linestyle in zip(data_list, colors, markers, linestyles):
        if legend_list:
            legend = legend_list.pop(0)
            plt.plot(x_values,data,marker=marker,linestyle=linestyle,color=color,label=legend,)
        else:
            plt.plot(x_values, data, marker=marker, linestyle=linestyle, color=color)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    if legend_list:
        plt.legend()

    plt.grid(True, linestyle="--", alpha=0.7)
    plt.savefig(save_name, dpi=300, bbox_inches="tight")
    plt.close()


def sheel_tashkeel(text):
    arabic_diacritics = re.compile(r'[\u0617-\u061A\u064B-\u0652\u0670]')
    return re.sub(arabic_diacritics, '', text.replace('>','').replace('<','').replace('^','').replace('؞',''))


def get_available_gpus():
    import torch

    if torch.cuda.is_available():
        print(f"Available GPUs: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    else:
        print("No GPUs detected (CUDA not available)")

# tashkeel removal + mothltha emala tatweel


if __name__ == "__main__":
    text = "This is a file to help in testing and debugging"
    pct(text, c=5)
