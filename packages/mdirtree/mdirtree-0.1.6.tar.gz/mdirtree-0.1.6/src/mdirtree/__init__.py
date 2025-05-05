"""
mdirtree - Generate directory structures from ASCII art or Markdown files.
"""

from .generator import DirectoryStructureGenerator, generate_from_ascii
from .cli import main

__version__ = "0.1.15"
__all__ = ["DirectoryStructureGenerator", "generate_from_ascii", "main"]