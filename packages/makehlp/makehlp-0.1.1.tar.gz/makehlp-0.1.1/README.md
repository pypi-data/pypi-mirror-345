# makehlp (make help)

Always-available script to analyze any unknown makefile and print out an inferred usage/help message explaining the available targets.

Many versions of this concept exist.. but this one is mine.

## Usage

```
usage: makehlp [-h] [--file MAKEFILE] [--inject] [target]

Process a Makefile and display help information

positional arguments:
  target                Print the full recipe (code) of a specific target

options:
  -h, --help            show this help message and exit
  --file, --makefile, -f MAKEFILE
                        Path to the Makefile (defaults to "Makefile" or "makefile" in current
                        directory)
  --inject              Inject a `help` target into the Makefile that calls makehelp (entirely
                        optional)
```
