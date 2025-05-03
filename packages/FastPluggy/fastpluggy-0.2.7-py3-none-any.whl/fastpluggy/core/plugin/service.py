from loguru import logger
from sqlalchemy.orm import Session

from fastpluggy.core.database import get_db
from fastpluggy.core.flash import FlashMessage
from fastpluggy.core.plugin import repository


class PluginService:

    @staticmethod
    def enable_plugin(plugin_name: str, fast_pluggy: "FastPluggy"):
        """
        Enables a plugin and refreshes the plugins.
        """
        db_session: Session = next(get_db())
        try:

            # 1) persist status change
            repository.update_plugin_status(db=db_session, plugin_name=plugin_name, status=True)
            # 2) do any side effects (reload, events, flash)
            fast_pluggy.load_app()

            logger.info(f"Plugin '{plugin_name}' enabled.")

            return FlashMessage(message=f"Plugin '{plugin_name}' enabled.", category='success')

        except Exception as e:
            logger.error(f"Error enabling plugin '{plugin_name}': {e}")
            db_session.rollback()
            return FlashMessage(message=f"Error enabling plugin '{plugin_name}': {e}", category='error')
        finally:
            db_session.close()

    @staticmethod
    def disable_plugin(plugin_name: str, fast_pluggy: "FastPluggy"):
        """
        Disable a plugin and refreshes the plugins.
        """
        db_session: Session = next(get_db())
        try:

            # 1) persist status change
            repository.update_plugin_status(db=db_session, plugin_name=plugin_name, status=False)
            # 2) do any side effects (reload, events, flash)
            fast_pluggy.load_app()

            logger.info(f"Plugin '{plugin_name}' disabled.")

            return FlashMessage(message=f"Plugin '{plugin_name}' disabled.", category='success')

        except Exception as e:
            logger.error(f"Error disabling plugin '{plugin_name}': {e}")
            db_session.rollback()
            return FlashMessage(message=f"Error disabling plugin '{plugin_name}': {e}", category='error')
        finally:
            db_session.close()


