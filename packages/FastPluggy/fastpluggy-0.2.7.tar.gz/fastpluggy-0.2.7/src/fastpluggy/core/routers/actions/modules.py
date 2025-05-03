from typing import Annotated

from fastapi.responses import RedirectResponse
from loguru import logger
from starlette import status

from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.plugin.service import PluginService
from fastpluggy.core.plugin.installer import PluginInstaller
from fastpluggy.core.tools.inspect_tools import InjectDependency
from fastpluggy.fastpluggy import FastPluggy


def toggle_module_status(plugin_name: str, fast_pluggy: Annotated[FastPluggy, InjectDependency]):
    plugin_manager = fast_pluggy.get_manager()

    current_status = plugin_manager.plugin_states.get(plugin_name, None)
    if current_status is None:
        return FlashMessage(message=f"Plugin '{plugin_name}' not found", category="error")
    if current_status:
        return PluginService.disable_plugin(plugin_name, fast_pluggy=fast_pluggy)
    else:
        return PluginService.enable_plugin(plugin_name, fast_pluggy=fast_pluggy)


def remove_plugin(plugin_name: str, fast_pluggy: Annotated[FastPluggy, InjectDependency]):
    manager = fast_pluggy.get_manager()

    # if not manager.module_directory_exists(plugin_name):
    #    return FlashMessage(message=f"Plugin '{plugin_name}' not found", category="error")

    try:
        manager.remove_plugin(plugin_name)
        return [
            FlashMessage(message=f"Plugin '{plugin_name}' removed successfully", category="success"),
            RedirectResponse(url=fast_pluggy.settings.fp_admin_base_url, status_code=status.HTTP_303_SEE_OTHER)
        ]

    except FileNotFoundError:
        return FlashMessage(message=f"Plugin '{plugin_name}' not found", category="error")
    except Exception as e:
        return FlashMessage(message=f"Error removing plugin: {str(e)}", category="error")


def install_plugin_from_git(
plugin_name : str,
        git_url: str,
        fast_pluggy: Annotated[FastPluggy, InjectDependency]
):
    """
    Installs a plugin from a Git repository.

    :param plugin_name:
    :param fast_pluggy:
    :param git_url: URL of the Git repository.

    """
    manager = fast_pluggy.get_manager()
    installer = PluginInstaller(manager)
    result = installer.install_from_git(plugin_name, git_url)

    return [
        RedirectResponse(url=fast_pluggy.settings.fp_admin_base_url, status_code=status.HTTP_303_SEE_OTHER),
        FlashMessage(result["message"], category="success" if result["status"] == "success" else "error")
    ]


def install_module_requirements(
        module_name: str,
        fast_pluggy: Annotated[FastPluggy, InjectDependency]
):
    """
    Installs the requirements for a specific module.
    """
    logger.debug(f"Installing requirements -  module_name: {module_name}")
    manager = fast_pluggy.get_manager()
    current_module = manager.modules.get(module_name)
    if not current_module:
        return FlashMessage(message=f"Plugin '{module_name}' not found", category="error")

    if current_module.plugin.requirements_exists:
        from fastpluggy.core.tools.install import install_requirements
        success = install_requirements(requirements_file=str(current_module.plugin.requirements_path))
        current_module.requirements_installed = success
        logger.info(f"Installed requirements for module '{current_module.plugin.module_name}'.")

        if success:
            return FlashMessage(
                f"Requirements for {current_module.module_type} '{module_name}' installed successfully!", "success")
        else:
            return FlashMessage(f"Failed to install requirements for {current_module.module_type} '{module_name}'.",
                                "error")
    else:
        return FlashMessage(f"No requirements found for {current_module.module_type} '{module_name}'.", "info")


# def load_domain_module(
#         module_name: str,
#         fast_pluggy: Annotated[FastPluggy, InjectDependency],
# ):
#     manager = fast_pluggy.get_manager()
#     manager.discover_plugins()
#
#     manager.load_module(module_name)
#     manager.execute_all_on_load(module_name)
#
#     # Update the menu using the new method
#     manager.update_menu_entries(fast_pluggy.menu_manager)
#
#     # Refresh templates
#     fast_pluggy.configure_templates()
#
#     return FlashMessage(f"Module '{module_name}' loaded successfully!", "success")
#

def update_plugin_from_git(
        module_name: str,
        fast_pluggy: Annotated[FastPluggy, InjectDependency],
        update_method: str = 'discard',  # Default method is 'none'
):
    """
    Updates a plugin from its Git repository. Allows the user to choose between 'stash' and 'discard' methods.

    :param fast_pluggy:
    :param module_name: The name of the plugin to update.
    :param update_method: The method to handle local changes (either 'none', 'stash' or 'discard').

    :return: FlashMessage
    """
    return_messages = []
    plugin_manager = fast_pluggy.get_manager()
    current_module = plugin_manager.modules.get(module_name)
    if current_module.git_available:
        # plugin_path = os.path.join(fast_pluggy.get_folder_by_module_type(current_module.module_type), module_name)
        installer = PluginInstaller(plugin_manager)

        result = installer.update_from_git(module_name, update_method)

        if result["status"] == "success" and "version" in result:
            # save_or_update_plugin(db=plugin_manager.db_session, plugin_name=plugin_name, version=result["version"])
            plugin_manager.fast_pluggy.load_app()

        return_messages.append(
            FlashMessage(result["message"], category="success" if result["status"] == "success" else "error"))
    else:
        return_messages.append(
            FlashMessage(message=f"Plugin '{module_name}' is not available from Git", category="error"))

    return_messages.append(
        RedirectResponse(url=fast_pluggy.settings.fp_admin_base_url, status_code=status.HTTP_303_SEE_OTHER)
    )
    return return_messages
