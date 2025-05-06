from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from fastpluggy.core.config import FastPluggyConfig
from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_view_builder, get_fastpluggy
from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.repository.app_settings import update_db_settings
from fastpluggy.core.view_builer.components.form import FormView
from fastpluggy.core.view_builer.components.list import ListButtonView

app_settings_router = APIRouter(
    tags=["admin"],
)
from fastpluggy.core.view_builer.components.button import FunctionButtonView


@app_settings_router.api_route("/settings", methods=["GET", "POST"], name="app_settings")
async def app_settings(request: Request, db: Session = Depends(get_db),
                       view_builder=Depends(get_view_builder),
                       fast_pluggy = Depends(get_fastpluggy)):
    from fastpluggy.core.routers.actions import reload_fast_pluggy
    from fastpluggy.core.tools.system import restart_application, restart_application_force


    form_view = FormView(
        title="Application Settings",
        model=FastPluggyConfig,
        data=fast_pluggy.settings,
        submit_label="Save Settings",
    )
    # TODO: show if an authentication method is setup
    items = [
        ListButtonView(
            title="Test/Debug",
            buttons=[
                FunctionButtonView(call=reload_fast_pluggy, label="Reload FastPluggy"),
                FunctionButtonView(
                    call=restart_application,
                    label="Restart App",
                ),
                FunctionButtonView(
                    call=restart_application_force,
                    label="Restart App (force)",
                ),
            ]
        ),
        form_view,
    ]
    if request.method == "POST":
        form_data = await request.form()

        form = form_view.get_form(form_data)
        if form.validate():
            new_params = dict(form_data)

            update_db_settings(current_settings=fast_pluggy.settings, db=db, new_params=new_params)

            fast_pluggy.load_app()

            FlashMessage.add(request, "Settings saved successfully!", "success")

    return view_builder.generate(
        request,
        title='Application Settings',
        items=items
    )
