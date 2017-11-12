from __future__ import absolute_import, unicode_literals

from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from wiki import models
from wiki.core.paginator import WikiPaginator


class GlobalHistory(ListView):

    template_name = 'wiki/plugins/globalhistory/globalhistory.html'
    paginator_class = WikiPaginator
    paginate_by = 30
    model = models.ArticleRevision
    context_object_name = 'revisions'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.only_last = kwargs.get('only_last', 0)
        self.filter = request.GET.get('q', '')
        return super(GlobalHistory, self).dispatch(
            request, *args, **kwargs)

    def get_queryset(self):
        qs = self.model.objects.can_read(self.request.user)
        if self.only_last == '1':
            qs = qs.filter(article__current_revision=F('id'))
        if self.filter:
            qs = qs.filter(
                Q(user_message__icontains=self.filter) |
                Q(automatic_log__icontains=self.filter) |
                Q(title__icontains=self.filter) |
                Q(user__username__icontains=self.filter))
        return qs.order_by('-modified')

    def get_context_data(self, **kwargs):
        kwargs['only_last'] = self.only_last
        kwargs['filter'] = self.filter
        return super(GlobalHistory, self).get_context_data(**kwargs)
