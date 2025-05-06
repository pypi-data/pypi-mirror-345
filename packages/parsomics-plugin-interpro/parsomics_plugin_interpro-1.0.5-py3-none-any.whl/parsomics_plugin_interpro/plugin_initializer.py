from parsomics_core.plugin_utils import PluginInitializer

from parsomics_plugin_interpro.populate import populate_interpro

initializer = PluginInitializer(
    subject="interpro",
    plugin_name="parsomics-plugin-interpro",
    populate_func=populate_interpro,
)
