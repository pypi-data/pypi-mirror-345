# pymunge

Munge tool for Star Wars Battlefront 2004.


## Install

```
python -m pip install swbf-pymunge
```

PyPi Mirror: [https://pypi.org/project/swbf-pymunge/](https://pypi.org/project/swbf-pymunge/)


## Usage

### Build a folder with mod files (at least one .req file required)
```
pymunge -s ./your_files
```

### Build a single ODF file
```
pymunge -s your_file.odf odfmunge
```

### Build a folder of ODF files
```
pymunge -s ./your_files odfmunge
```


See also `-h` for an up-to-date listing of all arguments.


### Flags
| Short Flag | Long Flag | Arguments | Description |
| :--- | :--- | :--- | :--- |
| `-p` | `--platform` | `pc , ps2 , xbox` | Platform to build for. |
| `-s` | `--source` | `<Path to mod files>` | Looks for .req files and their dependencies. |
| `-t` | `--target` | `<Path to write results>` | Munged files are written to this directory. |
| `-v` | `--version` | - | Print the current version. |


### Developer Flags
| Short Flag | Long Flag | Arguments | Description |
| :--- | :--- | :--- | :--- |
| `-l` | `--log-level` | `debug , info , warning, error , critical` | Adjusts logger output accordingly. |


## Documentation

[pymunge docs](https://styinx.github.io/pymunge/)


### Build local Documentation from sources

```
python .\source\pymunge\make.py docs --autogen --build
```

