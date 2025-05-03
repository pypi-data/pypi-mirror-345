from configparser import ConfigParser
import re


class AIXStanzaParser(ConfigParser):
    """
    Parse AIX stanza files. Modifies ConfigParser to handle unique
    characteristics of AIX stanza files.
    """

    def __init__(self, *args, **kwargs):

        try:
            # Grab parameters unique to AIXStanzaParser
            self._sectionBegin = kwargs.pop("sectionBegin", "")
            self._sectionEnd = kwargs.pop("sectionBegin", ":")
            self._keyValuePrefix = kwargs.pop("keyValuePrefix", "\t")

            # If delimiters is specified, use it, otherwise fill in with the
            # default appropriate for AIX stanza files.
            if "delimiters" not in kwargs:
                kwargs["delimiters"] = "="

        except KeyError:
            pass

        super().__init__(*args, **kwargs)
        self.SECTCRE = re.compile(
            r"""
        """
            + self._sectionBegin
            + r"(?P<header>[^"
            + self._sectionEnd
            + r"]*)"
            + self._sectionEnd
            + r"""
                                          """,
            re.VERBOSE,
        )

    #
    # Override _write_section() method. This presumes that
    # RawConfigParser.write() calls self._write_section(). If that changes
    # we'll want to override() the write() method instead.d We want to
    # - preserve stanza style
    # - add white space (_keyValuePrefix) before key-value pairs
    #
    def _write_section(self, fp, section_name, section_items, delimiter):
        """Write a single section to the specified `fp'."""
        fp.write(f"{self._sectionBegin}{section_name}{self._sectionEnd}\n")
        for key, value in section_items:
            value = self._interpolation.before_write(self, section_name, key, value)
            if value is not None or not self._allow_no_value:
                value = delimiter + str(value).replace("\n", "\n\t")
            else:
                value = ""
            fp.write(f"{self._keyValuePrefix}{key}{value}\n")
        fp.write("\n")
