#     Copyright 2025, Jorj McKie, mailto:<jorj.x.mckie@outlook.de> find license text at end of file


""" Details see below in class definition.
"""

from Bloodelf.plugins.PluginBase import BloodQPluginBase


class BloodQPluginNumpy(BloodQPluginBase):
    """This plugin is now not doing anything anymore."""

    plugin_name = "numpy"  # BloodQ knows us by this name
    plugin_desc = "Deprecated, was once required by the numpy package"
    plugin_category = "package-support,obsolete"

    @classmethod
    def isDeprecated(cls):
        return True



