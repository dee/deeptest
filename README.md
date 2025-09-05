# python-skeleton
А minimal base structure for my future python projects

# goals

This project structure is created for dual purposes:
- convenient work with Sublime Text
- minumum overhead

It looks more like a directory structure for C program. 
Source code assumed to be in _src_ subdirectory, while _tests_ is a place for unit tests, 
respectively.

# parts

_Sublime build system_

Build into a project file _*.sublime-project_

Consists of three parts: 
- run current file with python;
- run current test file with python;
- run tests for a whole project.

Tests will import main project sources in "src". There is a 
conftest.py, which modifies sys.path to make imports work, when I run a single test
from its directory:

```python
# tests/conftest.py
import os
import sys


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

```

# dependencies

Requirements file is split to requirements.txt and requirements-dev.txt, 
first one for a runtime dependencies, second is for development (that's where pytest 
is).

# fazit

Such layout makes development process easier by letting me run unit tests in-place,
and also lacks unnecessary nested folders (like src/myapp) along with nested packages. 