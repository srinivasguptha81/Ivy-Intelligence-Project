from django.apps import AppConfig


class OpportunitiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.opportunities'
    verbose_name = 'Opportunities'

    def ready(self):
        """Train classifier on startup if model doesn't exist."""
        from pathlib import Path
        model_path = Path(__file__).resolve().parent / 'domain_classifier.pkl'
        if not model_path.exists():
            try:
                from apps.opportunities.classifier import train_model
                train_model()
            except Exception:
                pass  # Don't crash startup if training fails
