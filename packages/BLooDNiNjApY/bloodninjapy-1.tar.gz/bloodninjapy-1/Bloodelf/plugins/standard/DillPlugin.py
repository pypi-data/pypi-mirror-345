


""" Standard plug-in to make dill module work for compiled stuff.

"""

from Bloodelf.Options import shallMakeModule
from Bloodelf.plugins.PluginBase import BloodQPluginBase


class BloodQPluginDillWorkarounds(BloodQPluginBase):
    """This is to make dill module work with compiled methods."""

    plugin_name = "dill-compat"
    plugin_desc = "Required for 'dill' package compatibility."
    plugin_category = "package-support"

    @staticmethod
    def isAlwaysEnabled():
        return False

    def createPostModuleLoadCode(self, module):
        full_name = module.getFullName()

        if full_name == "dill" and not shallMakeModule():
            return (
                self.getPluginDataFileContents("dill-postLoad.py"),
                """\
Extending "dill" for compiled types to be pickle-able as well.""",
            )

        if shallMakeModule() and module.isTopModule():
            return (
                """\
import sys
sys.modules[__compiled__.main]._create_compiled_function%(version)s = \
    sys.modules["%(module_name)s-preLoad"]._create_compiled_function%(version)s
sys.modules[__compiled__.main]._create_compiled_function%(version)s.__module__ = \
    __compiled__.main
"""
                % {"module_name": full_name, "version": "2" if str is bytes else "3"},
                """
Extending "dill" for compiled types to be pickle-able as well.""",
            )

    def createPreModuleLoadCode(self, module):
        if shallMakeModule() and module.isTopModule():
            return (
                self.getPluginDataFileContents("dill-postLoad.py"),
                """\
Extending "dill" for compiled types to be pickle-able as well.""",
            )

    @staticmethod
    def getPreprocessorSymbols():
        return {"_BloodSx_PLUGIN_DILL_ENABLED": "1"}

    def getExtraCodeFiles(self):
        return {"DillPlugin.c": self.getPluginDataFileContents("DillPlugin.c")}



