# Карта кода и запросов

| Назначение | Файл |
| --- | --- |
| Модели, связи, ограничения, статусы | `users/models.py`, `categories/models.py`, `accounts/models.py`, `operations/models.py` |
| Списание и возврат в одной транзакции | `Operation.save()`, `Operation.cancel()` |
| Запросы обзора и статистики | `ledger/queries.py` |
| Условия статусов и поиск | `OperationQuerySet` в `operations/models.py` |
| Unicode-поиск SQLite и подключение функции | `ledger/db_functions.py`, `ledger/apps.py` |
| GET-фильтры, дата и сортировка | `operations/forms.py` |
| Список, фильтры, `Paginator` | `operations/views.py` |
| `ModelForm`, рубли, изображения | `ledger/forms.py` |
| GET/POST, создание, изменение, отмена | `ledger/views.py` |
| CSRF, ошибки, подсказки | `ledger/templates/ledger/form.html` |
| Сохранение параметров страниц | `templates/includes/pagination.html` |
| Админка и inline | `users/admin.py`, `categories/admin.py`, `accounts/admin.py`, `operations/admin.py` |
| Общая база поиска админки | `ledger/admin.py` |
| Общие данные шаблонов | `ledger/context_processors.py` |
| Безопасный перенос источников | `ledger/management/commands/import_legacy.py` |
| Схема, преобразование имён и перенос моделей | `ledger/migrations/`, `users/migrations/`, `categories/migrations/`, `accounts/migrations/`, `operations/migrations/` |

## Запросы приложения

Это реальные запросы страниц, форм и моделей, а не отдельные вызовы внутри
одной цепочки. Условия поиска и сортировки берутся из проверенной формы.

1. `User.objects.all()` — справочник пользователей.
2. `Category.objects.all()` — справочник категорий.
3. `get_object_or_404(data.accounts(), slug=slug)` — отдельный счёт.
4. `get_object_or_404(data.operations(), pk=operation_id)` — отдельный расход.
5. `accounts.filter(balance__lte=limit)` — счета по доступному остатку.
6. `operations.filter(date__year=year, date__month=month)` — операции за месяц.
7. `operations.filter(user_id=user_id)` — операции пользователя.
8. `operations.filter(account_id=account_id)` — операции счёта.
9. `operations.filter(category_id=category_id)` — операции категории.
10. `Operation.objects.exclude(status=Status.CANCELLED)` — действующие операции.
11. `Category.objects.filter(name_key=name.casefold()).exclude(pk=current_pk).exists()`
    — поиск повторяющегося названия при создании и редактировании категории.
12. `operations.search(text)` — поиск по описанию, категории, счёту и имени владельца
    через `Q`, `UnicodeCasefold` и `contains`, включая поля связанных моделей.
    Регистр кириллицы сравнивается через `casefold()` с обеих сторон.
13. `operations.order_by(sort, '-pk')` — стабильная сортировка; в `sort` попадают
    только разрешённые значения, в том числе `account__name` и `user__name`.
14. `Account.objects.select_related('user').annotate(user_name=F('user__name'))`
    — счета с именем владельца.
15. `Operation.objects.select_related('user', 'account__user', 'category')`
    — расходы со всеми нужными объектами в одном SQL-запросе.
16. `Account.objects.values_list('id', 'name')` — сокращённый набор для формы.
17. `Operation.objects.completed().aggregate(total=Coalesce(Sum('amount'), 0), ...)`
    — сводка суммы, количества, минимума и максимума.
18. `Category.objects.annotate(total=..., count=...).filter(total__gte=min_total)`
    — статистика категорий с условием на агрегат, включая пустые группы.
19. `User.objects.annotate(total=..., count=...)` — расходы по людям, включая нули.
20. `operations.annotate(month=TruncMonth('date')).values('month').annotate(...)`
    — группировка по месяцам.
21. `aggregate(completed=Count('pk', filter=Q(...)), ...)` — количества по статусам.
22. `Paginator(operations, 5).get_page(page)` — подсчёт и выбор текущей страницы.
23. `operation_rows(operations)` — аннотации `F` связанных названий и slug,
    `Case` для подписи статуса и `values()` только полей таблицы. Используется
    в списке расходов, обзоре и карточке счёта; шаблон получает словари.

Для просмотра SQL: `python manage.py shell`, импортировать `Operation` из
`operations.models` или другие модели из их приложений,
создать QuerySet и вывести `print(queryset.query)`. Чтение связанных объектов можно
проверить в тесте с `CaptureQueriesContext` либо на вкладке SQL Debug Toolbar.

`GeneratedField` находится у `Operation.is_large`: признак суммы от 10 000 рублей
рассчитывается SQLite. После изменения суммы значение проверяется через
`refresh_from_db()`. Миграция `0002` показывает отдельное преобразование существующих
данных до введения нового ограничения.
