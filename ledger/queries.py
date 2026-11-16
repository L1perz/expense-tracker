"""Запросы обзора, поиска и статистики."""

from django.db.models import Count, F, Max, Min, Q, Sum
from django.db.models.functions import Coalesce, TruncMonth

from accounts.models import Account
from categories.models import Category
from operations.models import Operation
from users.models import User


def accounts():
    return Account.objects.select_related("user").annotate(user_name=F("user__name"))


def operations():
    return Operation.objects.with_details().annotate(
        user_name=F("user__name"),
        account_name=F("account__name"),
        category_name=F("category__name"),
    )


def period(queryset, month):
    if month:
        year, number = map(int, month.split("-"))
        return queryset.filter(date__year=year, date__month=number)
    return queryset


def summary(month=""):
    result = period(Operation.objects.completed(), month).aggregate(
        total=Coalesce(Sum("amount"), 0),
        count=Count("pk"),
        maximum=Coalesce(Max("amount"), 0),
        minimum=Coalesce(Min("amount"), 0),
    )
    result["balance"] = Account.objects.aggregate(value=Coalesce(Sum("balance"), 0))[
        "value"
    ]
    return result


def statistics(month="", min_total=0):
    condition = Q(operations__status=Operation.Status.COMPLETED)
    if month:
        year, number = map(int, month.split("-"))
        condition &= Q(operations__date__year=year, operations__date__month=number)

    def totals(queryset):
        return queryset.annotate(
            total=Coalesce(Sum("operations__amount", filter=condition), 0),
            count=Count("operations", filter=condition),
        )

    monthly = (
        Operation.objects.completed()
        .order_by()
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"), count=Count("pk"))
        .order_by("month")
    )
    statuses = period(Operation.objects.all(), month).aggregate(
        completed=Count("pk", filter=Q(status=Operation.Status.COMPLETED)),
        pending=Count("pk", filter=Q(status=Operation.Status.PENDING)),
        cancelled=Count("pk", filter=Q(status=Operation.Status.CANCELLED)),
    )
    return {
        "categories": totals(Category.objects.all()).filter(total__gte=min_total),
        "users": totals(User.objects.all()),
        "months": [{**row, "month": row["month"].strftime("%Y-%m")} for row in monthly],
        "summary": summary(month),
        "statuses": statuses,
    }
