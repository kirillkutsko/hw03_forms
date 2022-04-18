from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    NOW_YEAR = datetime.now().year
    return {
        'year': NOW_YEAR,
    }
