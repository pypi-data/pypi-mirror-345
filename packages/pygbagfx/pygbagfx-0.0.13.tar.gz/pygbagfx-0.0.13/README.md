# pygbagfx

Python wrapper for the GBA graphics tool from
https://github.com/pret/pokeemerald

This is used in [Archipelago cross-game multiworld randomizer](https://github.com/ArchipelagoMW/Archipelago).

## Import from package

* Install from PyPI via `pip install pygbagfx`
* Or download a [release](https://github.com/RhenaudTheLukark/pygbagfx/releases) and `pip install` it
* Or clone, build and install a wheel from source using
  ```
  git clone https://github.com/RhenaudTheLukark/pygbagfx --recurse-submodules
  python3 -m build --wheel
  pip install dist/*.whl
  ```

## Import from source

* Clone with submodules using
  ```
  git clone https://github.com/RhenaudTheLukark/pygbagfx --recurse-submodules
  ```
* Simply import the cloned repo, it will auto-compile or run through cppyy.
  Either a C compiler or [cppyy](https://pypi.org/project/cppyy/) is required.

## API

```python
main(input: Path, output: Path)  # transforms a resource into another
```