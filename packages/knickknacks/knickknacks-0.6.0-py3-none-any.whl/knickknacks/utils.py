# Copyright (c) 2025 Nick Stockton
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# -----------------------------------------------------------------------------
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# -----------------------------------------------------------------------------
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Misc utilities."""

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import inspect
import itertools
import shutil
import textwrap
from collections.abc import Sequence
from pydoc import pager
from types import FrameType


def get_function_field(back: int = 0) -> FrameType:
	"""
	Retrieves the stack field for the function which called this function.

	Args:
		back: The number of frames to go back.

	Returns:
		The function stack field.

	Raises:
		AttributeError: Unable to get reference to function.
	"""
	counter = itertools.count()
	frame = inspect.currentframe()
	while frame is not None:  # Note that this will always perform at least 1 loop.
		if next(counter) > back:
			return frame
		frame = frame.f_back
	raise AttributeError("Unable to get reference to function.")


def get_function_name(back: int = 0) -> str:
	"""
	Retrieves the name of the function which called this function.

	Args:
		back: The number of frames to go back.

	Returns:
		The function name, or an empty string if not found.
	"""
	try:
		return get_function_field(back + 1).f_code.co_name
	except AttributeError:
		return ""


def page(lines: Sequence[str]) -> None:
	"""
	Displays lines using the pager if necessary.

	Args:
		lines: The lines to be displayed.
	"""
	# This is necessary in order for lines with embedded new line characters to be properly handled.
	lines = "\n".join(lines).splitlines()
	width, _ = shutil.get_terminal_size()
	# Word wrapping to 1 less than the terminal width is necessary to prevent
	# occasional blank lines in the terminal output.
	text = "\n".join(textwrap.fill(line.strip(), width - 1) for line in lines)
	pager(text)
