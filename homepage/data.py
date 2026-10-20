"""ПР6: адаптер JSON-объектов для контекста шаблонов."""

from django.conf import settings

from storage import load_project


def get_users():
    return [user.to_dict() for user in load_project(settings.DATA_DIR)[0]]


def get_categories():
    return [item.to_dict() for item in load_project(settings.DATA_DIR)[2]]


def get_accounts():
    return [dict(item.to_dict(), user_name=item.user.name)
            for item in load_project(settings.DATA_DIR)[1]]


def get_operations():
    return [dict(item.to_dict(), date=item.date, user_name=item.user.name,
                 account_name=item.account.name, category_name=item.category.name)
            for item in sorted(load_project(settings.DATA_DIR)[3],
                               key=lambda item: (item.date, item.id), reverse=True)]
