# paven

# Installation

```bash
pip install paven
```

# Configuration

```toml
[tool.paven]
root = "paven"
destination = "paven/_vendor/"
requirements = "paven/_vendor/vendor.txt"
namespace = "paven._vendor"

[tool.paven.transformations]
drop = ["*.dist-info", "*.egg-info"] # should not be required
```

# Usage

```bash
cd /path/to/your/project
python -m paven
```

To switch back to the non-vendored versions:
```bash
python -m paven --revert
```
