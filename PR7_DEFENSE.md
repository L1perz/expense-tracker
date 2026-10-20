# ПР7: где показать каждый из 25 пунктов оценивания

Памятка к таблице 7.6 из присланного задания. Все примеры относятся к варианту 14 —
системе учёта расходов: **пользователь, счёт, категория, операция**.

Для каждого пункта ниже указаны конкретный код, действие для демонстрации и короткий
ответ преподавателю. Ссылки на код закреплены на версии `8955b3f`, поэтому номера
строк не изменятся при дальнейшей доработке проекта. Локально открывай тот же файл
и переходи на указанную строку; в VS Code это можно сделать через `Ctrl+G`.

## Подготовка перед защитой

Команды выполняются из папки с `manage.py`. Если база ещё не подготовлена:

```powershell
.\.venv\Scripts\python.exe -m db.import_json
```

Если команда сообщает, что база уже содержит данные, повторный импорт не нужен.
Для демонстрации создания таблиц используй отдельную базу `data/defense.sqlite`,
как описано в пунктах 3 и 5. Рабочую базу удалять или перезаписывать не требуется.

Запусти сайт и оставь это окно PowerShell открытым:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Адрес сайта: <http://127.0.0.1:8000/>. Во втором окне открой Python-консоль Django:

```powershell
.\.venv\Scripts\python.exe manage.py shell
```

В ней один раз выполни этот код. `show()` — вспомогательная функция только для
демонстрации SELECT; добавлять её в исходники проекта не нужно.

```python
from django.conf import settings
from db.database import connection
from db import repository as data

def show(sql, parameters=()):
    with connection(settings.EXPENSE_DB_PATH) as conn:
        rows = conn.execute(sql, parameters).fetchall()
    for row in rows:
        print(dict(row))
```

В интерактивной консоли после определения функции нажми Enter на пустой строке.
Python-блоки ниже выполняются в этой консоли, PowerShell-блоки — в обычном терминале.
Для выхода из Python используй `exit()`.

Все ожидаемые числа ниже приведены для исходных демонстрационных данных:
3 пользователя, 4 счёта, 5 категорий, 9 операций. Если менял данные, результат может
отличаться; сначала сверяй его со своей базой. **В SQL суммы указаны в копейках,
в формах сайта — в рублях.**

## Быстрый указатель

| № | Что спрашивают | Что открыть первым |
| --- | --- | --- |
| [1](#p1) | Структура базы | [sql/schema.sql, строки 4–34][schema] |
| [2](#p2) | Таблицы, первичные и внешние ключи | [sql/schema.sql, строки 9–33][schema-keys] |
| [3](#p3) | Создание базы и выполнение схемы | [db/database.py, строки 18–28][connection]; [db/import_json.py, строки 19–20][import-schema] |
| [4](#p4) | Подключение Python к SQLite | [db/database.py, строки 18–33][connection] |
| [5](#p5) | Импорт из JSON | [storage.py, строки 38–63][load-project]; [db/import_json.py, строки 12–45][import] |
| [6](#p6) | Проверка импорта через COUNT | [db/import_json.py, строки 21–22][import-count] |
| [7](#p7) | SELECT и выбор полей | [sql/queries.sql, строки 28–35][q-operations] |
| [8](#p8) | WHERE | [sql/queries.sql, строки 17–21][q-low-balance] |
| [9](#p9) | Отбор по признаку | [sql/queries.sql, строки 44–48][q-conditions] |
| [10](#p10) | JOIN | [sql/queries.sql, строки 30–34][q-operations] |
| [11](#p11) | Несколько условий | [sql/queries.sql, строки 37–49][q-filter] |
| [12](#p12) | COUNT() | [sql/queries.sql, строки 59–67][q-summary] |
| [13](#p13) | GROUP BY | [sql/queries.sql, строки 69–91][q-groups] |
| [14](#p14) | HAVING | [sql/queries.sql, строки 72–78][q-categories] |
| [15](#p15) | Параметры отдельно от SQL | [db/repository.py, строки 21–29][fetch] |
| [16](#p16) | Именованные результаты SQLite | [db/database.py, строка 27][row-factory]; [db/repository.py, строки 24–29][fetch] |
| [17](#p17) | Список объектов на сайте | [operations/views.py, строки 9–17][operation-list] |
| [18](#p18) | Отфильтрованный список на сайте | [accounts/views.py, строки 9–15][account-list] |
| [19](#p19) | Связанные данные на странице | [operations/views.py, строки 20–24][operation-detail-view] |
| [20](#p20) | Поиск по вводу пользователя | [operations/forms.py, строки 10–40][operation-form] |
| [21](#p21) | Статистика на сайте | [operations/views.py, строки 27–33][statistics-view] |
| [22](#p22) | Имена переменных в контексте и шаблоне | [operations/views.py, строка 14][operation-list]; [шаблон таблицы, строка 2][operation-table] |
| [23](#p23) | Пустой результат | [шаблон таблицы, строка 2, тег empty][operation-table] |
| [24](#p24) | Ошибка SQL и её исправление | [sql/queries.sql, строки 30–34][q-operations] |
| [25](#p25) | Полный путь запроса | [expense_tracker/urls.py, строка 6][root-urls] → [operations/urls.py, строка 7][operation-urls] |

<a id="p1"></a>
## 1. Проектирование структуры базы данных

**Где показать:** [sql/schema.sql:4–34][schema].

**Что показать:** четыре `CREATE TABLE`. В `users` хранятся пользователи,
в `accounts` — их счета с остатками, в `categories` — назначения расходов,
в `operations` — суммы, даты, описания и ссылки на остальные сущности.

**Короткий ответ:** один пользователь может иметь несколько счетов и операций.
Каждый счёт принадлежит одному пользователю. Каждая операция относится к одному
счёту, пользователю и категории. Поля `user_id`, `account_id`, `category_id`
связывают записи между таблицами. Типы `INTEGER` и `TEXT` видны рядом с полями;
даты хранятся строками `YYYY-MM-DD`, деньги — целыми копейками.

<a id="p2"></a>
## 2. Создание таблиц и связей

**Где показать:** [sql/schema.sql:9–33][schema-keys]. Найди `PRIMARY KEY`,
`REFERENCES`, `UNIQUE (id, user_id)` и `FOREIGN KEY (account_id, user_id)`.
Включение проверки внешних ключей — [db/database.py:28][row-factory].

**Демонстрация:** открой [JOIN операции][q-operations]: значения ID связывают
операцию с названиями счёта, категории и именем пользователя. Проверку запрета
нарушенных связей можно показать тестом [test_database_constraints][constraint-test].
Из обычного PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_database.py -k database_constraints
```

**Короткий ответ:** первичный ключ однозначно определяет запись. Внешний ключ
запрещает ссылаться на отсутствующую запись. Составная связь счёта и пользователя
дополнительно запрещает записать расход от имени владельца чужого счёта.
Тест выполняется во временной базе и не изменяет рабочие данные.

<a id="p3"></a>
## 3. Создание базы данных и выполнение схемы

**Где показать:** [db/database.py:18–28][connection]: каталог, URI файла,
`mode=rwc`, `sqlite3.connect()`. Выполнение SQL-схемы —
[db/import_json.py:19–20][import-schema], `conn.executescript(...)`.

**Демонстрация:** в Python-консоли Django выполни код для отдельного файла:

```python
from pathlib import Path

with connection(Path("data/defense.sqlite"), readonly=False) as conn:
    conn.executescript(Path("sql/schema.sql").read_text(encoding="utf-8"))
```

Выполни тот же блок повторно. Ошибки существующих таблиц не будет.

**Короткий ответ:** `mode=rwc` разрешает создать файл и читать/записывать его.
`executescript()` выполняет все команды схемы. `CREATE TABLE IF NOT EXISTS` и
`CREATE INDEX IF NOT EXISTS` делают повторное выполнение этой схемы безопасным
для существующих таблиц и записей. Это не заменяет миграции, если состав полей
в будущем изменится. При обычном чтении сайт использует `mode=ro` и не создаёт
пустую базу по ошибочному пути.

<a id="p4"></a>
## 4. Подключение к базе данных

**Где показать:** [db/database.py:18–33][connection], затем
[expense_tracker/settings.py:44–45][db-setting] и
[db/repository.py:21–24][fetch].

**Демонстрация:** в Python-консоли Django:

```python
print(settings.EXPENSE_DB_PATH.resolve())
show("PRAGMA database_list")
show("SELECT id, name FROM users ORDER BY id")
```

**Короткий ответ:** `sqlite3.connect()` открывает конкретный файл базы. Сайт
передаёт путь из `settings.EXPENSE_DB_PATH`; `PRAGMA database_list` показывает
фактически открытый файл в поле `file`. Эти пути должны совпасть.
Контекстный менеджер закрывает соединение в `finally`.

<a id="p5"></a>
## 5. Импорт данных из JSON

**Где показать:** [storage.py:38–63][load-project] — восстановление объектов и
проверки связей; [db/import_json.py:12–45][import] — схема, транзакция и вставки.
Особенно строки 29–43 с `executemany()` и `to_dict()`.

**Демонстрация:** после создания пустой демонстрационной базы из пункта 3
в обычном PowerShell выполни:

```powershell
.\.venv\Scripts\python.exe -m db.import_json --database data/defense.sqlite
```

Если этот демонстрационный файл уже содержит импортированные записи, программа
сообщит об этом и сохранит их. Для показа самого процесса используй новый файл,
например `data/defense-2.sqlite`, вместо перезаписи рабочей базы.

**Короткий ответ:** JSON превращается в объекты, проверяются ID и ссылки,
`to_dict()` подготавливает значения для параметров SQL. Сначала вставляются
пользователи, затем счета и категории, последними — операции. Иначе внешние ключи
операций могли бы ссылаться на ещё не созданные записи. Все вставки идут в одной
транзакции. Исторические расходы не списываются повторно: импортируются текущие
остатки и сохранённые операции.

<a id="p6"></a>
## 6. Проверка результатов импорта

**Где показать:** [db/import_json.py:21–22][import-count] — `SELECT COUNT(*)`.
Для сравнения с JSON выполни в Python-консоли:

```python
import json

for table in ("users", "accounts", "categories", "operations"):
    source = settings.DATA_DIR / f"{table}.json"
    expected = len(json.loads(source.read_text(encoding="utf-8")))
    with connection(settings.EXPENSE_DB_PATH) as conn:
        actual = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(table, "JSON:", expected, "SQLite:", actual, "совпало:", expected == actual)
```

**Ожидается:** `users 3`, `accounts 4`, `categories 5`, `operations 9`; все сравнения
дают `True`. Имена таблиц здесь берутся из фиксированного списка в коде.

**Короткий ответ:** несовпадение количества может означать неполный импорт,
другую базу или изменение JSON после импорта. Совпадение количества — первая
проверка, но не доказательство совпадения каждого значения. Дополнительно можно
сравнить отдельные записи и выполнить `show("PRAGMA foreign_key_check")`:
пустой результат означает отсутствие обнаруженных нарушений внешних ключей.

<a id="p7"></a>
## 7. Выборка данных с помощью SELECT

**Где показать:** [sql/queries.sql:28–35][q-operations], запрос `operations`.
`o.*` выбирает все поля операции; `AS user_name`, `account_name`, `category_name`
дают названия дополнительным полям результата.

**Демонстрация изменения полей:** выполни два отдельных запроса в Python-консоли:

```python
show("SELECT id, amount FROM operations ORDER BY id LIMIT 2")
show("SELECT id, date, amount, description FROM operations ORDER BY id LIMIT 2")
```

**Короткий ответ:** строки относятся к тем же операциям, но во втором результате
есть ещё дата и описание. Шаблон может использовать только те поля, которые
переданы ему из результата. Поэтому удаление `description` из запроса сайта
потребовало бы согласовать отображение. Для демонстрации достаточно отдельных
SELECT в консоли; рабочий запрос сайта менять не требуется.

<a id="p8"></a>
## 8. Фильтрация данных с помощью WHERE

**Где показать:** [sql/queries.sql:17–21][q-low-balance], запрос
`low_balance_accounts`, условие `a.balance <= :max_balance`.
Вызов — [db/repository.py:40–43][get-accounts].

**Демонстрация:** открой `/accounts/?max_balance=8000` — останутся «Наличные»
с остатком 7500 рублей. Поменяй порог на `50000` — добавятся «Основная карта»
и «Зарплатная карта»; «Накопления» с остатком 120000 рублей не попадут.

**Короткий ответ:** `WHERE` оставляет только строки, удовлетворяющие условию.
В форме значение вводится в рублях, а в SQL передаётся в копейках: `8000`
превращается в `800000`. Преобразование начинается в
[accounts/forms.py:12–14][account-form].

<a id="p9"></a>
## 9. Фильтрация записей по состоянию или признаку

**Где показать:** [sql/queries.sql:44–48][q-conditions], условие
`o.category_id = :category_id`; поле формы — [operations/forms.py:30–31][operation-form].

**Демонстрация:** `/operations/?category_id=3` показывает расходы категории «Дом»:
«Коммунальные услуги» и «Интернет». Замени `category_id=3` на `category_id=2`:
будут только транспортные расходы — «Поездка на метро», «Проездной», «Автобус».

**Короткий ответ:** признак отбора в этом проекте — принадлежность операции
к категории. Операции с другой категорией исключаются. У операций этой версии
нет статуса отмены, поэтому для своего варианта показываю реально существующий
признак вместо статусов бронирования из примера Roomly.

<a id="p10"></a>
## 10. Объединение таблиц с помощью JOIN

**Где показать:** [sql/queries.sql:30–34][q-operations]. Три соединения:
`users.id = operations.user_id`, `accounts.id = operations.account_id`,
`categories.id = operations.category_id`.

**Демонстрация:** открой `/operations/1/`. На одной странице видны операция
«Продукты на неделю», пользователь Лев, счёт «Основная карта», категория «Продукты»
и сумма 2450.50 руб. Запрос для этой карточки —
[sql/queries.sql:51–57][q-operation].

**Короткий ответ:** операция хранит ID связанных записей. JOIN позволяет получить
их имена и названия одним запросом. Результат содержит поля `user_name`,
`account_name`, `category_name`, которые выводятся в шаблоне.

<a id="p11"></a>
## 11. Отбор данных по нескольким условиям

**Где показать:** [sql/queries.sql:37–49][q-filter], блок `WHERE` с `AND`;
передачу словаря параметров — [db/repository.py:59–65][get-operations].

**Демонстрация:** открой
`/operations/?month=2026-10&user_id=2&category_id=3` — одна операция
«Коммунальные услуги». Поменяй `category_id=3` на `category_id=1` — останется
«Покупка продуктов». При `month=2026-09&user_id=2&category_id=3` записей не будет.

**Короткий ответ:** `AND` требует выполнения всех заданных ограничений.
Конструкция `:user_id IS NULL OR ...` отключает фильтр пользователя, если он
не выбран. Аналогично пустая строка месяца означает отсутствие ограничения месяца.

<a id="p12"></a>
## 12. Подсчёт записей с помощью COUNT()

**Где показать:** [sql/queries.sql:59–67][q-summary], запросы `expense_summary`
и `balance_summary`. В группах — [sql/queries.sql:72][q-categories], `COUNT(o.id)`.

**Демонстрация:** в Python-консоли:

```python
print(data.get_summary("2026-09")["count"])
print(data.get_summary("2000-01")["count"])
```

Первое значение — `2`, второе — `0`.

**Короткий ответ:** `COUNT(*)` считает строки выборки. Без подходящих операций
он возвращает ноль. `SUM()` при отсутствии строк возвращает NULL, поэтому в коде
используется `COALESCE(SUM(amount), 0)`. При LEFT JOIN нужен `COUNT(o.id)`,
чтобы категория без операций получила ноль, а не единицу от строки категории.

<a id="p13"></a>
## 13. Группировка данных с помощью GROUP BY

**Где показать:** [sql/queries.sql:69–91][q-groups]: группы по категориям,
пользователям и месяцам. Для категорий — `GROUP BY c.id, c.name`.

**Демонстрация:** открой `/operations/statistics/`. В категориях «Дом» получит
2 операции на 4849.00 руб., «Продукты» — 3 операции на 4755.50 руб.
Внизу данные сгруппированы по месяцам: октябрь — 7 операций, сентябрь — 2.

**Короткий ответ:** GROUP BY собирает записи с одинаковым ключом в группы.
`COUNT()` и `SUM()` вычисляются отдельно для каждой группы. LEFT JOIN сохраняет
категории и пользователей без расходов, например «Здоровье» и Михаила.

<a id="p14"></a>
## 14. Фильтрация групп с помощью HAVING

**Где показать:** [sql/queries.sql:72–78][q-categories], строка
`HAVING COALESCE(SUM(o.amount), 0) >= :min_total`.
Сумму формы преобразует [operations/forms.py:43–51][statistics-form].

**Демонстрация:** `/operations/statistics/?month=2026-10&min_total=1000` —
останутся «Дом» и «Продукты». Порог `4000` оставит только «Дом».

**Короткий ответ:** WHERE отбирает отдельные строки до группировки.
HAVING отбирает уже посчитанные группы: здесь сравнивается сумма расходов
категории с порогом. Порог влияет только на список категорий; общая сумма,
пользователи и динамика считаются по правилам, подписанным на странице.

<a id="p15"></a>
## 15. Параметризованные SQL-запросы

**Где показать:** `:month`, `:user_id`, `:category_id` в [SQL-фильтре][q-filter],
словарь значений в [db/repository.py:62–65][get-operations], затем
[db/repository.py:24][fetch]: `conn.execute(QUERIES[name], parameters or {})`.

**Демонстрация:** выполни в Python-консоли:

```python
show("SELECT id, description FROM operations WHERE user_id = :user_id", {"user_id": 2})
print(data.get_operations(query="' OR 1=1 --"))
```

Первый запрос выберет расходы Анны. Второй вернёт пустой список на демоданных:
введённая строка рассматривается как фрагмент описания, а не команда SQL.

**Короткий ответ:** текст SQL и пользовательские значения передаются раздельно.
Подстановка пользовательского ввода через f-строку могла бы изменить структуру
SQL и создать SQL-инъекцию. В импорте f-строки используются только для названий
таблиц из фиксированного списка, а значения записей передаются параметрами.

<a id="p16"></a>
## 16. Получение и обработка результатов SQL

**Где показать:** [db/database.py:27][row-factory],
`conn.row_factory = sqlite3.Row`; [db/repository.py:24–29][fetch],
`fetchall()` и `[dict(row) for row in rows]`.

**Демонстрация:** в Python-консоли:

```python
with connection(settings.EXPENSE_DB_PATH) as conn:
    row = conn.execute("SELECT id, name FROM users WHERE id = ?", (1,)).fetchone()
    print(row["name"])
    print(dict(row))
```

Результат — имя `Лев` и словарь с `id` и `name`.

**Короткий ответ:** `sqlite3.Row` разрешает обращаться к столбцу по имени,
например `row["name"]`, а не запоминать его позицию. Репозиторий преобразует строки
в словари для контекста Django. Функция [dated()][dated] также переводит строку
даты из SQL в `datetime.date`, чтобы работал фильтр даты в шаблоне.

<a id="p17"></a>
## 17. Отображение списка объектов

**Где показать:** [operations/views.py:9–17][operation-list], вызов
`data.get_operations()` и ключ `"operations"`; [шаблон списка][operation-list-template]
подключает [таблицу операций][operation-table]. В таблице найди
`{% for operation in operations %}`.

**Демонстрация:** `/operations/` показывает 9 расходов, начиная с последних.
В репозитории используется [запрос operations][q-operations], который получает
данные из SQLite, а не из JSON.

**Короткий ответ:** view получает список словарей от SQL-слоя и передаёт его
в контексте под именем `operations`. Цикл шаблона создаёт строку таблицы
для каждого элемента. `render()` возвращает сформированный HTML-ответ.

<a id="p18"></a>
## 18. Отображение отфильтрованных записей

**Где показать:** [accounts/views.py:9–15][account-list] →
[db/repository.py:40–43][get-accounts] → [SQL с WHERE][q-low-balance].

**Демонстрация:** `/accounts/?max_balance=8000` показывает только «Наличные».
После сброса фильтра `/accounts/` снова показывает четыре счёта.

**Короткий ответ:** форма проверяет порог, репозиторий подставляет его отдельным
параметром в SQL, и только выбранные базой записи попадают в контекст `accounts`.
Шаблон не скрывает лишние счета самостоятельно: их уже нет в результате SQL.

<a id="p19"></a>
## 19. Отображение связанных данных

**Где показать:** [sql/queries.sql:51–57][q-operation] →
[db/repository.py:68–72][get-operation] →
[operations/views.py:20–24][operation-detail-view] →
[operations/templates/operations/detail.html:2][operation-detail-template].

**Демонстрация:** `/operations/1/`. Найди в шаблоне
`{{ operation.user_name }}`, `{{ operation.account_name }}`,
`{{ operation.category_name }}` и ссылку на счёт через `{% url %}`.

**Короткий ответ:** JOIN добавляет названия связанных сущностей к полям операции.
View передаёт одну запись в `operation`. Шаблон показывает сведения четырёх
таблиц в одной карточке, а не отдельные числовые ID без пояснений.

<a id="p20"></a>
## 20. Реализация поиска по пользовательским параметрам

**Где показать:** [шаблон формы, строки 2–4][filter-template] — `method="get"`;
[operations/forms.py:10–40][operation-form] — поля и проверки;
[operations/views.py:10–12][operation-list] — `request.GET`, `is_valid()`,
`cleaned_data`; [db/repository.py:59–65][get-operations] — SQL-параметры.

**Демонстрация:** на `/operations/` выбери месяц «октябрь 2026», пользователя
Анна, категорию «Дом» и нажми «Применить». В адресе появятся GET-параметры,
в списке останутся «Коммунальные услуги».

**Короткий ответ:** браузер передаёт значения в строке запроса. Django-форма
проверяет месяц и допустимые значения справочников; очищенные данные получает
репозиторий. SQL выполняется с этими параметрами. Неверный месяц или недопустимый
ID дают HTTP 400 с сообщением формы, а не ошибку базы. Поиск фрагмента описания
в этой реализации учитывает регистр.

<a id="p21"></a>
## 21. Отображение статистических данных

**Где показать:** [operations/views.py:27–33][statistics-view] →
[db/repository.py:75–87][statistics-data] →
[SQL агрегатов и группировок][q-groups] →
[operations/templates/operations/statistics.html:9–20][statistics-template].

**Демонстрация:** `/operations/statistics/?month=2026-09`.
Сумма за сентябрь — 1160.00 руб., количество — 2, максимальная трата —
980.00 руб., минимальная — 180.00 руб. Ниже — распределение по категориям
и пользователям, затем динамика всей истории по месяцам.

**Короткий ответ:** SQL считает агрегаты и группы. `get_statistics()` собирает
их в словарь с ключами `summary`, `categories`, `users`, `months`. View передаёт
эти ключи шаблону, который выводит значения и полосы диаграммы. Строки исходных
операций для этой статистики не суммируются в HTML-шаблоне.

<a id="p22"></a>
## 22. Передача результатов в шаблон

**Где показать:** [operations/views.py:13–16][operation-list],
`"operations": operations`, и [таблицу, строка 2][operation-table],
`{% for operation in operations %}`.

**Как продемонстрировать исправление:** сначала в Python-консоли проверь, что SQL
действительно возвращает данные: `print(len(data.get_operations()))` — на демоданных
получится `9`. Сравни два варианта ключа контекста:

```python
# Ошибка: шаблон ожидает operations, а ему передали другое имя.
context = {"items": data.get_operations()}

# Исправление: ключ совпадает с именем в цикле шаблона.
context = {"operations": data.get_operations()}
```

Если преподаватель просит показать именно на странице, временно замени только
ключ `"operations"` на `"items"` в view списка, обнови `/operations/`, затем
обязательно верни `"operations"` и обнови снова. Файл сохраняй после каждой правки.
Не меняй одновременно SQL и шаблон: так будет видно, в чём причина.

**Короткий ответ:** имя переменной в контексте должно совпадать с именем,
к которому обращается шаблон. При несовпадении SQL может работать правильно,
но цикл шаблона не найдёт список. Существующий блок `{% empty %}` покажет
сообщение об отсутствии операций. Исправление — согласовать имена.

<a id="p23"></a>
## 23. Обработка пустых результатов

**Где показать:** [db/repository.py:24–29][fetch] — получение списка строк;
[таблица операций, строка 2][operation-table] —
`{% empty %}` и «Операций не найдено». Для агрегатов —
[sql/queries.sql:61–63][q-summary].

**Демонстрация:** `/operations/?month=2000-01` — страница открывается нормально,
пишет «Операций не найдено», общая сумма равна 0.00 руб.

**Короткий ответ:** пустая выборка — корректный запрос, вернувший ноль строк;
`fetchall()` даёт пустой список. При ошибке имени поля или SQL-синтаксиса возникает
исключение. Это разные ситуации. Отсутствующая конкретная операция, например
`/operations/999/`, возвращает 404, а пустой список по фильтру — 200.

<a id="p24"></a>
## 24. Диагностика ошибок SQL-запросов

**Где показать:** [sql/queries.sql:30–34][q-operations] — правильные имена полей
и условия JOIN; выполнение запроса и обработка ошибок —
[db/repository.py:24–28][fetch].

**Пример неверного имени поля:** в Python-консоли выполни отдельный запрос:

```python
show("SELECT id, ammount FROM operations LIMIT 1")
```

Получится `sqlite3.OperationalError: no such column: ammount`.
Исправление — настоящее имя `amount`, указанное в схеме:

```python
show("SELECT id, amount FROM operations LIMIT 1")
```

**Пример логической ошибки JOIN:** запрос выполнится, но выберет неверные категории:

```python
show("SELECT o.id, c.name FROM operations o JOIN categories c ON c.id = o.account_id WHERE o.id = 2")
show("SELECT o.id, c.name FROM operations o JOIN categories c ON c.id = o.category_id WHERE o.id = 2")
```

В первом случае операция №2 ошибочно получает «Продукты», во втором — правильную
категорию «Транспорт». Открой `/operations/2/` и сравни с исправленным результатом.
Эти отдельные SELECT не изменяют данные и не портят рабочие запросы сайта.

**Короткий ответ:** ошибку синтаксиса или имени поля видно по исключению. Логическая
ошибка может вернуть правдоподобные, но неверные значения; её проверяют по схеме,
условиям соединения и известной записи. JOIN категории должен сравнивать
`categories.id` именно с `operations.category_id`, а не с `account_id`.

<a id="p25"></a>
## 25. Сквозная обработка запроса в Django

**Демонстрационный адрес:**
`/operations/?month=2026-10&user_id=2&category_id=3`.

Проследи этот путь, открывая файлы по порядку:

1. [expense_tracker/urls.py:6][root-urls]: префикс `operations/` передаётся
   в `include("operations.urls")`.
2. [operations/urls.py:7][operation-urls]: пустой остаток пути вызывает
   `views.operation_list`; GET-параметры не участвуют в сопоставлении пути.
3. [operations/views.py:10–12][operation-list]: `request.GET` попадает в форму,
   затем проверяется через `is_valid()`.
4. [operations/forms.py:10–40][operation-form]: проверяются месяц и выбранные
   значения; в `cleaned_data` попадают месяц-строка и числовые ID.
5. [db/repository.py:59–65][get-operations]: выбирается `filtered_operations`,
   формируется словарь параметров.
6. [db/repository.py:21–29][fetch] и [db/database.py:25–28][row-factory]:
   открывается нужный SQLite-файл, включается `sqlite3.Row`, выполняется запрос
   с параметрами, результат превращается в список словарей.
7. [sql/queries.sql:37–49][q-filter]: JOIN добавляет названия, WHERE отбирает
   месяц, пользователя и категорию, ORDER BY задаёт порядок.
8. [db/repository.py:53–56][dated]: дата превращается в `datetime.date`.
9. [operations/views.py:13–17][operation-list]: список передаётся в контекст
   под именем `operations`, вызывается `render()`.
10. [Шаблон списка][operation-list-template] подключает [таблицу][operation-table];
    цикл выводит «Коммунальные услуги», связанные названия, дату и сумму.

**Короткий ответ:** проверять нужно последовательно: адрес и маршрут → значения
GET → ошибки формы → путь к базе → SQL и параметры → строки результата → ключи
контекста → обращения в шаблоне. Так можно найти этап, на котором потерялись
или изменились данные, вместо одновременной правки всего проекта.

## Перед самой демонстрацией

Оставь открытыми редактор с этой памяткой, `sql/queries.sql`, `db/repository.py`,
`operations/views.py` и браузер с сайтом. На каждый вопрос достаточно показать
указанное место, одно действие и дать короткое объяснение. Если временно менял
код в пункте 22, верни исходный ключ `operations`.

Для проверки проекта после своих правок:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m flake8
git diff
```

<!-- Ссылки закреплены на проверенной версии кода до добавления этой памятки. -->
[schema]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/sql/schema.sql#L4-L34
[schema-keys]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/sql/schema.sql#L9-L33
[connection]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/db/database.py#L18-L33
[row-factory]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/db/database.py#L25-L28
[db-setting]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/expense_tracker/settings.py#L44-L45
[import-schema]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/db/import_json.py#L19-L20
[import]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/db/import_json.py#L12-L45
[import-count]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/db/import_json.py#L21-L22
[load-project]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/storage.py#L38-L63
[q-operations]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/sql/queries.sql#L28-L35
[q-low-balance]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/sql/queries.sql#L17-L21
[q-conditions]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/sql/queries.sql#L44-L48
[q-filter]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/sql/queries.sql#L37-L49
[q-operation]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/sql/queries.sql#L51-L57
[q-summary]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/sql/queries.sql#L59-L67
[q-groups]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/sql/queries.sql#L69-L91
[q-categories]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/sql/queries.sql#L72-L78
[fetch]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/db/repository.py#L21-L29
[get-accounts]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/db/repository.py#L40-L43
[get-operations]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/db/repository.py#L59-L65
[get-operation]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/db/repository.py#L68-L72
[dated]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/db/repository.py#L53-L56
[statistics-data]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/db/repository.py#L75-L87
[operation-list]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/operations/views.py#L9-L17
[operation-detail-view]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/operations/views.py#L20-L24
[statistics-view]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/operations/views.py#L27-L33
[operation-form]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/operations/forms.py#L10-L40
[statistics-form]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/operations/forms.py#L43-L51
[account-list]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/accounts/views.py#L9-L15
[account-form]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/accounts/forms.py#L12-L14
[filter-template]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/templates/includes/filter_form.html#L2-L4
[operation-list-template]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/operations/templates/operations/list.html#L1-L2
[operation-table]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/operations/templates/operations/includes/table.html#L1-L2
[operation-detail-template]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/operations/templates/operations/detail.html#L1-L2
[statistics-template]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/operations/templates/operations/statistics.html#L9-L20
[constraint-test]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/tests/test_database.py#L56-L68
[root-urls]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/expense_tracker/urls.py#L3-L7
[operation-urls]: https://github.com/L1perz/expense-tracker/blob/8955b3fc5d048a602cffb6ddf45b29961a9cabb5/operations/urls.py#L5-L9
