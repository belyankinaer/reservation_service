# reservation_service
Callback API для Управления Резервированием Товаров

Для генерации отчета о покрытии тестами:
pytest -v --cov=app --cov-report=html tests/ 

Для запуска контейнера:
docker build . --file Dockerfile - запуск контейнера
