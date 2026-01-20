# Тестирование API

## Запуск тестирования

### 1. Заполнение базы данных тестовыми данными

```bash
python manage.py populate_test_data --users 5 --projects 10 --events 10
```

Параметры:
- `--users` - количество пользователей (по умолчанию: 5)
- `--projects` - количество проектов (по умолчанию: 10)
- `--events` - количество мероприятий (по умолчанию: 10)

### 2. Запуск сервера

```bash
python manage.py runserver
```

### 3. Запуск тестового скрипта

```bash
python test_api.py
```

## Доступные API endpoints

### Projects
- `GET /api/projects/` - Список всех проектов
- `GET /api/projects/{id}/` - Детали проекта
- `POST /api/projects/` - Создание проекта
- `PUT /api/projects/{id}/` - Обновление проекта
- `DELETE /api/projects/{id}/` - Удаление проекта
- `GET /api/projects/recent_or_updated/` - Недавние или обновленные проекты
- `GET /api/projects/search_complex/?q=keyword` - Сложный поиск
- `POST /api/projects/{id}/add_skill/` - Добавить навык к проекту
- `POST /api/projects/{id}/remove_skill/` - Удалить навык из проекта

### Events
- `GET /api/events/` - Список всех мероприятий
- `GET /api/events/{id}/` - Детали мероприятия
- `POST /api/events/` - Создание мероприятия
- `PUT /api/events/{id}/` - Обновление мероприятия
- `DELETE /api/events/{id}/` - Удаление мероприятия
- `GET /api/events/with_achievements/` - Мероприятия с достижениями
- `GET /api/events/recent_participations/` - Недавние участия
- `POST /api/events/{id}/update_result/` - Обновить результат мероприятия

### Categories, Skills, Event Types
- `GET /api/categories/` - Список категорий
- `GET /api/skills/` - Список навыков
- `GET /api/event-types/` - Список типов мероприятий

## Примеры запросов

### Фильтрация
```
GET /api/projects/?category=1
GET /api/projects/?user=1
GET /api/projects/?created_after=2024-01-01
GET /api/events/?has_certificate=true
```

### Поиск
```
GET /api/projects/?search=django
GET /api/events/?search=хакатон
```

### Сортировка
```
GET /api/projects/?ordering=-created_at
GET /api/projects/?ordering=title
```

### Пагинация
```
GET /api/projects/?page=1
GET /api/projects/?page=2
```
