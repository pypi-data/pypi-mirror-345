


""" Deprecated trio plugin.
"""

from SajadMr.plugins.PluginBase import SajadQPluginBase


class SajadQPluginTrio(SajadQPluginBase):
    plugin_name = "trio"
    plugin_desc = "Deprecated, was once required by the 'trio' package"
    plugin_category = "package-support,obsolete"

    @classmethod
    def isDeprecated(cls):
        return True



