import requests
import json

BASE_URL = 'http://127.0.0.1:8000/api'


def print_response(response, title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")


def test_api():
    print("Тестирование API портфолио студентов")
    print("="*60)

    print("\n1. Тестирование Projects API")
    response = requests.get(f'{BASE_URL}/projects/')
    print_response(response, "GET /api/projects/ - Список проектов")

    response = requests.get(f'{BASE_URL}/projects/?search=проект')
    print_response(response, "GET /api/projects/?search=проект - Поиск проектов")

    response = requests.get(f'{BASE_URL}/projects/recent_or_updated/')
    print_response(response, "GET /api/projects/recent_or_updated/ - Недавние проекты")

    response = requests.get(f'{BASE_URL}/projects/search_complex/?q=система')
    print_response(response, "GET /api/projects/search_complex/?q=система - Сложный поиск")

    print("\n2. Тестирование Events API")
    response = requests.get(f'{BASE_URL}/events/')
    print_response(response, "GET /api/events/ - Список мероприятий")

    response = requests.get(f'{BASE_URL}/events/?search=хакатон')
    print_response(response, "GET /api/events/?search=хакатон - Поиск мероприятий")

    response = requests.get(f'{BASE_URL}/events/with_achievements/')
    print_response(response, "GET /api/events/with_achievements/ - Мероприятия с достижениями")

    print("\n3. Тестирование Categories API")
    response = requests.get(f'{BASE_URL}/categories/')
    print_response(response, "GET /api/categories/ - Список категорий")

    print("\n4. Тестирование Skills API")
    response = requests.get(f'{BASE_URL}/skills/')
    print_response(response, "GET /api/skills/ - Список навыков")

    print("\n5. Тестирование Event Types API")
    response = requests.get(f'{BASE_URL}/event-types/')
    print_response(response, "GET /api/event-types/ - Список типов мероприятий")

    print("\n6. Тестирование пагинации")
    response = requests.get(f'{BASE_URL}/projects/?page=1')
    print_response(response, "GET /api/projects/?page=1 - Первая страница")

    print("\n7. Тестирование фильтрации")
    response = requests.get(f'{BASE_URL}/projects/?category=1')
    print_response(response, "GET /api/projects/?category=1 - Фильтр по категории")

    print("\n8. Тестирование сортировки")
    response = requests.get(f'{BASE_URL}/projects/?ordering=-created_at')
    print_response(response, "GET /api/projects/?ordering=-created_at - Сортировка по дате")

    print("\n" + "="*60)
    print("Тестирование завершено!")
    print("="*60)


if __name__ == '__main__':
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\nОшибка: Не удалось подключиться к серверу.")
        print("Убедитесь, что сервер запущен: python manage.py runserver")
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")
