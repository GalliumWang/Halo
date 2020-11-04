from django import template
from core.models import Bookmark, FollowList

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Bookmark.objects.filter(user=user)
        if qs.exists():
            return qs[0].items.count()
    return 0


@register.filter
def follow_item_count(user):
    if user.is_authenticated:
        qs = FollowList.objects.filter(user=user)
        if qs.exists():
            return qs[0].items.count()
    return 0
