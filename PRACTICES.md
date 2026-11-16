# Практические работы 9–11

Вариант 14 — система учёта расходов. Сущности: пользователь, счёт, категория,
операция. Учебные примеры Roomly применяются к финансовой предметной области.

## Модели и ORM

| Требования ПР9 | Реализация |
| --- | --- |
| Продолжение проекта, отдельное приложение каждой сущности | `users`, `categories`, `accounts`, `operations`; сохранены страницы прежних практик |
| Поля, типы, первичные ключи, ограничения | `models.py` каждого приложения, `BigAutoField`, валидаторы, ограничения БД |
| Связи, on_delete, related_name и обратные связи | `Account.user`, `Operation.user/account/category`, `PROTECT`, `accounts`, `operations` |
| Миграции и сохранение существующих данных | Исторические `ledger.0001/0002`, начальные миграции приложений, `ledger.0003`, `MIGRATIONS.md` |
| Получение списков и отдельного объекта, CRUD | Представления приложений, общие обработчики `ledger/views.py`, формы, консоль |
| Фильтры по одному и нескольким условиям, связанным полям, exclude | `OperationQuerySet`, `operations/views.py`, `ledger/queries.py` |
| Строковый поиск и поиск по нескольким полям | `search_text`, четыре настройки `search_fields` админки, `OperationQuerySet.search` |
| Сортировка, связи и сокращённый набор полей | `order_by`, `select_related`, `operation_rows` с `F`, `Case` и `values` |
| Агрегаты, аннотации и группировки | `summary`, `statistics`, `Sum`, `Count`, `Min`, `Max`, `TruncMonth` |
| Пагинация и сохранение GET-параметров | `Paginator`, `templates/includes/pagination.html` |
| Интеграция в шаблоны, неверные параметры, пустые результаты, 404 | Представления и тесты `test_web.py`, `test_list_rows.py` |
| Не менее 15 разных выражений ORM | 23 примера в `CODE_GUIDE.md`; примеры используются в приложении |
| Документация и контрольная точка Git | README и коммит с префиксом `PR9:` |

Сайт и консоль используют одну SQLite через ORM. Прежние `db/`, `models/` и
`sql/` сохраняют совместимость с форматами прошлых практик и используются при
импорте; они не обслуживают текущие страницы вместо ORM.

## Административная панель и запросы

| Требования ПР10 | Реализация |
| --- | --- |
| Регистрация моделей, связанные объекты, поиск, фильтры, сортировка | `admin.py` каждого из четырёх приложений, inline счетов и операций |
| Статусы TextChoices и существующие данные | `Operation.Status`; старые расходы импортируются как оплаченные без повторного списания |
| Менеджер, QuerySet, совместные фильтры, сортировка и страницы | `OperationQuerySet`, `operations/views.py` |
| Исключение отменённых записей, статистика статусов | `active`, `completed`, `cancelled`, `statistics` |
| Slug и get_absolute_url | `Account.slug`, `Account.get_absolute_url`, маршрут `accounts:detail_slug` |
| Контекстный процессор и вычисляемое поле | `ledger/context_processors.py`, `Operation.is_large` через `GeneratedField` |
| Проверка ORM и SQL | `test_orm.py`, `test_list_rows.py`; Debug Toolbar включается через `DJANGO_DEBUG_TOOLBAR=1` |
| check, тесты, документация, Git | Команды из README, коммит с префиксом `PR10:` |

До появления статусов в формате расходов не было булевого `is_cancelled`.
Исторические записи превращаются в `completed` в команде `import_legacy`.
Миграция реальных данных `RunPython` показана в `0002_category_name_key`;
`0003_split_entity_apps` переносит типы моделей и назначенные права.
Несуществующее прежнее поле для демонстрации не вводится.

## Формы

| Требования ПР11 | Реализация |
| --- | --- |
| Form, GET-параметры, is_valid, cleaned_data, корректные ошибки | `OperationFilterForm`, `StatisticsFilterForm`, `AccountFilterForm` |
| ModelForm, Meta.fields, подписи и виджеты | `UserForm`, `CategoryForm`, `AccountForm`, `OperationForm` в приложениях сущностей |
| GET и POST при создании, сохранение, redirect | `ledger/views.py`, собственные маршруты приложений |
| Дата, доступность и исключение редактируемой записи из конфликта | `Operation.clean`, `OperationForm.clean`, учёт прежнего списания при редактировании |
| Ошибки полей и non_field_errors | `ledger/templates/ledger/form.html` |
| Редактирование существующей записи | `instance` в ModelForm, прежний ID сохраняется |
| Отмена с изменением статуса, освобождение ресурса | `Operation.cancel` возвращает деньги один раз, запись остаётся в истории |
| Отсутствующий объект и защита запросов | `get_object_or_404`, CSRF, GET-отмена возвращает 405 |
| Изображения, файлы и настройки MEDIA | `Account.image`, Pillow, `request.FILES`, `multipart/form-data` |
| Документация, проверка сценариев, Git | README, `test_orm.py`, `test_review_regressions.py`, коммит с префиксом `PR11:` |

У расхода проверяются владелец счёта и доступные средства вместо занятости
помещения. Исторические расходы допустимы, будущая дата требует статуса
«Запланирован». Покупки одной суммы в один день разрешены. При редактировании
учитывается уже списанная сумма этой операции, поэтому запись не конфликтует
сама с собой. Собственные CSS-стили форм соответствуют разрешённой в методичке
альтернативе Bootstrap.

## Проверка перед демонстрацией

```bash
python manage.py check
python manage.py showmigrations
python manage.py makemigrations --check --dry-run
python -m pytest -q
python -m flake8
```

Тесты используют временные базы. `tests/test_migrations.py` дополнительно
проверяет обновление существующей схемы, сохранность финансовых записей, прав,
журнала админки, откат и повторное применение миграций.

В браузере можно показать общий список с фильтрами, вторую страницу, карточку
счёта по slug, создание, редактирование и отмену расхода, ошибку остатка и
четыре раздела административной панели. В Django Shell:

```python
from accounts.models import Account
from operations.models import Operation
from ledger.queries import operation_rows, operations

Account.objects.get(pk=1)
Operation.objects.active().filter(account__user_id=1).order_by('-date', '-pk')
list(operation_rows(operations())[:5])
print(operation_rows(operations()).query)
```

Отдельные отчёты и ответы на контрольные вопросы предоставляются вместе с
проектом. Подтверждение выполнения Яндекс Практикума относится к отдельной
части сдачи и в код проекта не включается.
