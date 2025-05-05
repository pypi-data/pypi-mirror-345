# Toolify

A Python library that provides helper functions and tools for colored terminal output, Arabic text processing, logging, file handling, plotting, and GPU detection.

## Installation

Install `Toolify` from PyPI:

```bash
pip install toolify
```

### Requirements
- Python >= 3.8
- Dependencies:
  - `python-bidi==0.6.6`
  - `arabic_reshaper==3.0.0`
  - `matplotlib>=3.5.0` (optional, for plotting)
  - `torch>=1.10.0` (optional, for GPU detection)


## Usage

Import and use the functions from the `toolify.tools` module:

```python
from toolify.tools import print_colored_text, print_arabic_text, print_package_info

# Print colored text
print_colored_text("Hello, World!", color="green", emoji="star")

# Print Arabic text
print_arabic_text("مرحبا بالعالم", color="blue", emoji="heart")

# Print package information
print_package_info()
```

## Functions

| Function | Description |
|----------|-------------|
| `print_colored_text` | Prints text in a specified color with an optional emoji. |
| `print_arabic_text` | Prints Arabic text with proper reshaping and bidirectional display. |
| `setup_logger` | Configures a logger for logging messages to a file. |
| `save_text_list` | Saves a list of text arrays to a file. |
| `save_text` | Saves a single text string to a file. |
| `line_plotter` | Saves a line plot for multiple data lists. |
| `strip_tashkeel` | Removes Arabic diacritics and specific characters from text. |
| `get_available_gpus` | Prints information about available CUDA GPUs. |
| `print_package_info` | Prints information about the package and its functions. |

## Example: Plotting Data

```python
from toolify.tools import line_plotter

data = [[1, 2, 3], [4, 5, 6]]
line_plotter(
    data_list=data,
    save_name="plot.png",
    legend_list=["Line 1", "Line 2"],
    x_label="X Axis",
    y_label="Y Axis",
    title="Sample Plot"
)
```
<!-- 
## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/amrabdelsamea/toolify). -->

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.