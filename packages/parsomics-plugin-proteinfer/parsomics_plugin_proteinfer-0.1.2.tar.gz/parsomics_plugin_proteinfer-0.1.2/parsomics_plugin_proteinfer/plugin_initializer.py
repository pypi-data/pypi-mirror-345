from parsomics_core.plugin_utils import PluginInitializer

from parsomics_plugin_proteinfer.populate import populate_proteinfer

initializer = PluginInitializer(
    subject="proteinfer",
    plugin_name="parsomics-plugin-proteinfer",
    populate_func=populate_proteinfer,
)
