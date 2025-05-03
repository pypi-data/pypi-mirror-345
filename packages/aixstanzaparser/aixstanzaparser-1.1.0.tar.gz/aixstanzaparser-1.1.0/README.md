# aixstanzaparser

aixstanzaparser Python 3.x module. Subclasses
configparser.ConfigParser to support parsing and writing AIX stanza
files.

## Usage ##

Here's an example of using `AIXStanzaParser` to parse lvupdate.data
and update it to set `llvupdate.llu` to `yes`.

``` python
import aixstanzaparser

# Create parser instance
config = aixstanzaparser.AIXStanzaParser()

# Read and parse lvupdate.date
config.read("lvupdate.data")

# Update llvupdate.llu to yes
if 'llvupdate' not in config.sections():
    config['llvupdate'] = {}
config['llvupdate']['llu'] = "yes"

# write updated lvupdate.data
with open("lvupdate.data", "w") as configfile:
    config.write(configfile)
```


## Limitations ##

Comments are lost when AIXStanzaParser parses a file. So reading,
parsing, updating and writing an AIX stanza file with AIXStanzaParser
will lose any existing comments.
