from django.apps import AppConfig
import logging


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        """Envia as estatisticas iniciais para o MongoDB assim que o app carregar."""
        try:
            from .services.mongo_stats import sync_admin_charts_to_mongo

            sync_admin_charts_to_mongo()
        except Exception:  # pragma: no cover - protecao para arranques
            logging.getLogger(__name__).exception(
                "Falha ao sincronizar estatisticas com MongoDB no arranque"
            )
