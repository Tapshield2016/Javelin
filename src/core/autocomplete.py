from models import AgencyUser

from ajax_select import register, LookupChannel


@register('users')
class UserLookup(LookupChannel):

    model = AgencyUser

    def get_query(self, q, request):
        return self.model.objects.filter(username__contains=q)

    def format_item_display(self, item):
        return u"<span class='user'>%s</span>" % item.username
