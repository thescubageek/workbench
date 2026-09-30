"""Exception hierarchy shared by every linkcrawl subpackage."""


class LinkcrawlError(Exception):
    """Base class for all errors raised deliberately by linkcrawl."""


class ConfigError(LinkcrawlError):
    """A setting has an invalid value or a config file cannot be read."""

    def __init__(self, message, source=None, key=None):
        self.source = source
        self.key = key
        prefix = ""
        if source:
            prefix += f"{source}: "
        if key:
            prefix += f"{key}: "
        super().__init__(prefix + message)


class PluginError(LinkcrawlError):
    """A plugin could not be imported or its setup function failed."""


class ReportError(LinkcrawlError):
    """A reporter name is unknown or a saved results file is malformed."""


class CrawlAborted(LinkcrawlError):
    """The crawl stopped before the frontier was exhausted."""

    def __init__(self, message, results=None):
        super().__init__(message)
        self.results = list(results or [])
