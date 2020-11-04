from django.contrib import admin

from .models import *


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user'
                    ]
    list_display_links = [
        'user'
    ]
    list_filter = []
    search_fields = [
        'user__username'
    ]
    #actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(Item)
admin.site.register(BookmarkItem)
admin.site.register(Bookmark, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
admin.site.register(Comments)
admin.site.register(PeopleItem)
admin.site.register(FollowItem)
admin.site.register(FollowList)
admin.site.register(MoviePeopleRelationship)
