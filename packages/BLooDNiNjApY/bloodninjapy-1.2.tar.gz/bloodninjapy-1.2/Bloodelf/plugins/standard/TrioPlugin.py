


""" Deprecated trio plugin.
"""

from Bloodelf.plugins.PluginBase import BloodQPluginBase


class BloodQPluginTrio(BloodQPluginBase):
    plugin_name = "trio"
    plugin_desc = "Deprecated, was once required by the 'trio' package"
    plugin_category = "package-support,obsolete"

    @classmethod
    def isDeprecated(cls):
        return True



