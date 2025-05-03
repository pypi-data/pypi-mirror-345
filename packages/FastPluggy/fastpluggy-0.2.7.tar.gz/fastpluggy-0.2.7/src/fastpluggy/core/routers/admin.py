import httpx
from fastapi import APIRouter, Depends, Request, Form
from fastapi import status, UploadFile, File
from fastapi.responses import RedirectResponse
from loguru import logger

from fastpluggy.core.base_module_manager import BaseModuleManager
from fastpluggy.core.dependency import get_view_builder, get_fastpluggy, get_module_manager
from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.menu.decorator import menu_entry
from fastpluggy.core.plugin.installer import PluginInstaller
from fastpluggy.core.view_builer.components.button import AutoLinkView, FunctionButtonView
from fastpluggy.core.view_builer.components.custom import CustomTemplateView
from fastpluggy.core.view_builer.components.debug import DebugView
from fastpluggy.core.view_builer.components.list import ListButtonView
from fastpluggy.core.view_builer.components.render_field_tools import RenderFieldTools
from fastpluggy.core.view_builer.components.table import TableView


admin_router = APIRouter(
    tags=["admin"]
)


@menu_entry(label="Manage Plugins", icon="fa-solid fa-screwdriver-wrench", type='admin', position=1,divider_after=True)
@admin_router.get("/plugins", name="list_plugins")
def list_plugins(
        request: Request, plugin_manager: BaseModuleManager = Depends(get_module_manager),
        view_builder=Depends(get_view_builder),
        fast_pluggy = Depends(get_fastpluggy)
):
    from fastpluggy.core.routers.actions import reload_fast_pluggy
    from fastpluggy.core.routers.actions.modules import toggle_module_status
    from fastpluggy.core.routers.actions.modules import update_plugin_from_git

    buttons = [
        AutoLinkView(
            label='<i class="fa fa-gear me-1"></i>App Settings', route_name='app_settings',
        ),
        FunctionButtonView(call=reload_fast_pluggy, label="Reload FastPluggy"),
    ]

    if plugin_manager.is_module_loaded('tasks_worker'):
        try:
            from tasks_worker.tasks.plugin_update import check_for_plugin_updates
            buttons.append(
                FunctionButtonView(label="Check plugin update", call=check_for_plugin_updates, run_as_task=True)
            )
        except Exception:
            logger.exception("No plugins task_worker")

    data = [ item.to_dict() for item in plugin_manager.modules.values()]
    data.sort(key=lambda x: x.get("name", ""))

    data_raw = [ {key : item.to_dict()} for key,item in plugin_manager.modules.items()]

    items = [
        ListButtonView(
            title='Actions',
            buttons=buttons,
        ),
        TableView(
            title='Plugin List',
            fields=["module_menu_icon", 'have_update', 'module_name', 'module_type','version_html', 'status_html'],
            data=data,
            field_callbacks={
                'have_update': lambda value: '<i class="fa-solid fa-arrow-up me-1"></i>' if value else '',
                'module_menu_icon': RenderFieldTools.render_icon,
            },
            headers={
                'module_menu_icon': 'icon',
                'module_type': 'type',
                'version_html': 'version',
                'status_html': 'status',
            },
            links=[
                FunctionButtonView(
                    call=toggle_module_status,
                    label=lambda item: "Disable" if item["enabled"] else "Enable",
                    css_class=lambda item: "btn btn-warning" if item["enabled"] else "btn btn-success",
                    param_inputs={
                        "plugin_name": "<module_name>",  # map function param to item["name"]
                    },
                ),
                AutoLinkView(
                    label='<i class="fa-solid fa-magnifying-glass me-1"></i> View',
                    route_name='get_overview_module',
                    css_class="btn btn-info",
                 #   params={ 'plugin_name': 'module_name'},  # param for url
                    param_inputs={'plugin_name': '<module_name>'}  # param mapping for item
                ),
                AutoLinkView(
                    label='<i class="fa-solid fa-gear"></i> Configure',
                    route_name='get_plugin_settings',
                    css_class=lambda item: "btn btn-info disabled" if item['settings'] is None else "btn btn-info",
                   # params={'plugin_name': 'module_name'},  # param for url
                    param_inputs={'plugin_name': '<module_name>'}  # param mapping for item
                ),
                FunctionButtonView(
                    call=update_plugin_from_git,
                    label="Update Plugin",
                    css_class="btn btn-secondary",
                    #params={'module_name': 'module_name'},
                    #param_mapping={
                    #    "module_name": "module_name",  # map function param to item["name"]
                    #},
                    condition=lambda task: task['git_available'] is True),
            ]
        ),
        CustomTemplateView(
            template_name="admin/install_module.html.j2",
            context={
                "default_plugin_url": fast_pluggy.settings.plugin_list_url,
                "fetch_plugin_url": request.url_for('fetch_plugins'),
            }
        ),
        DebugView(data=data_raw, title="Plugin data", collapsed=True),
    ]
    return view_builder.generate(
        request,
        title="Plugin Administration",
        items=items
    )


@admin_router.post("/install")
def install_plugin(request: Request, file: UploadFile = File(...),
                   fast_pluggy=Depends(get_fastpluggy),
                   plugin_manager: BaseModuleManager = Depends(get_module_manager)):
    """
    Route for installing a new plugin (upload ZIP file)
    """
    installer = PluginInstaller(plugin_manager)
    result = installer.extract_and_install_zip(file)
    plugin_prefix = fast_pluggy.settings.fp_admin_base_url
    FlashMessage.add(request, result["message"], category="success" if result["status"] == "success" else "error")
    return RedirectResponse(url=plugin_prefix, status_code=status.HTTP_303_SEE_OTHER)


@admin_router.post("/plugin/fetch", name="fetch_plugins")
async def fetch_plugins(
        request: Request,
        url: str = Form(...),  # URL to fetch plugins from
        plugin_manager: BaseModuleManager = Depends(get_module_manager),
        view_builder=Depends(get_view_builder),
        fast_pluggy = Depends(get_fastpluggy)
):
    """
    Fetches a list of plugins from a remote URL.

    :param plugin_manager:
    :param view_builder:
    :param request: FastAPI request object.
    :param url: The URL to fetch plugins from.
    """
    from fastpluggy.core.routers.actions.modules import install_plugin_from_git

    try:
        # Fetch plugin list from the given URL
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            plugin_list = response.json()  # Assuming JSON response

        FlashMessage.add(request=request, message="Plugin list fetched successfully", category="success")
    except Exception as e:
        logger.error(f"Failed to fetch plugins: {e}")
        FlashMessage.add(request=request, message="Failed to fetch plugins", category="error")
        plugin_prefix = fast_pluggy.settings.fp_admin_base_url
        return RedirectResponse(url=plugin_prefix, status_code=status.HTTP_303_SEE_OTHER)

    already_installed = plugin_manager.modules.keys()
    clean_data = []
    for item in plugin_list:
        item['installed'] = bool(item['name'] in already_installed)
        clean_data.append(item)

    items = [
        TableView(
            data=clean_data,
            fields=['name', 'installed', 'version', 'description'],
            field_callbacks={'installed': RenderFieldTools.render_boolean},
            links=[
                FunctionButtonView(
                    call=install_plugin_from_git, label="Install Plugin",
                    param_inputs={'plugin_name':'<name>', 'git_url': '<git_url>'},
                ),
            ]
        ),
        ListButtonView(
            buttons=[
                AutoLinkView(label="Back to Plugins", route_name="list_plugins")
            ]
        )
    ]
    return view_builder.generate(
        request,
        title='Available Plugins',
        items=items
    )
