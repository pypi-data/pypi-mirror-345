# parsomics-registry

A plugin registry for parsomics.

## How to update this repository

### Versioning

The `plugins.json` file uses semantic versioning. The major version should be increased when breaking changes are introduced, the minor version should be increased when new features are implemented, and the patch version should be increased when issues are fixed. Here is a rundown of each of those mean for this project:

Breaking changes:

- Adding fields in the plugin metadata
- Removing fields in the plugin metadata
- Renaming fields in the plugin metadata

Features:

- Adding new plugins to `plugins.json`

Fixes:

- Fixing typos in `plugins.json`

### Hashing

After making changes to the `plugins.json` file, run:

```bash
python hash.py
```

This will update the `plugins.json.hash` file, which contains a hash of the `plugins.json` file. The changes to both files should be included in the same commit.

### Signing

Every commit to this repository must be signed with a GPG key.

## License

Each plugin is licensed under their own terms. Check out their packages at the Python Package Index (PyPI) for more information on each of them. This repository itself is licensed under the terms of the GPLv3.
