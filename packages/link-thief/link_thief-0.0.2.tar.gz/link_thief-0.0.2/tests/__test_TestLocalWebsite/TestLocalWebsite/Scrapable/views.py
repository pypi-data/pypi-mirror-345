from django.shortcuts import render
from django.views.generic import TemplateView


class LinkScraperView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(LinkScraperView, self).get_context_data(**kwargs)
        return context
    
    def post(self, request, *args, **kwargs):
        context = super(LinkScraperView, self).get_context_data(**kwargs)
        return render(request, self.template_name, context=context)
