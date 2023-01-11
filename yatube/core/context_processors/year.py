from django.utils import timezone


def year(request):
    """Добавляет переменную с текущим годом."""
    dt_now = timezone.now().year
    return {'year': dt_now}
