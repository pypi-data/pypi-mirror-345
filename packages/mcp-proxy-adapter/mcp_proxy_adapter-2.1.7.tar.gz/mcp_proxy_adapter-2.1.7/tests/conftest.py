import warnings
import pytest

# Отключаем все DeprecationWarning и устаревшие предупреждения для чистоты тестов
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# Для pytest >=7.1 можно использовать mark.filterwarnings
pytestmark = pytest.mark.filterwarnings(
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning"
) 