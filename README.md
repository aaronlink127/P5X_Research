# P5X Research
## P5XUtils.py
This utility can be used in 2 ways, single-command mode or interactive mode.

Single-command mode is done by invoking the script in the terminal directly, with the game path and args provided directly.
Example: `python P5XUtils.py "D:\Games\P5X" find-asset makoto_thief.prefab`

If opened directly, it will open in interactive mode, which will ask for the game directory, and then you can input commands directly.
The commands are as follows:
```
Commands:
  help - Show this message
  exit - Exit this utility
  find-asset <asset-name> - Prints bundle that contains asset
  find-asset-dep <asset-name> - Prints bundle that contains asset, and any dependencies
  find-bundle-dep <bundle-name> - Prints dependencies of a given bundle
  extract-bundle <bundle-name> <output-dir> - Extracts bundle to directory
  extract-bundle-dep <bundle-name> <output-dir> - Extracts bundle dependency tree to directory
  extract-asset-dep <asset-name> <output-dir> - Extracts asset dependency tree of asset
```