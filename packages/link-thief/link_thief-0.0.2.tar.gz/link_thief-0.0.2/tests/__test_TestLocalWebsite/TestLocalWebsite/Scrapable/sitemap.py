from django.urls import reverse
from django.contrib.sitemaps import Sitemap


class StaticSitemap1(Sitemap):

    def items(self):
        return ["main", "main-2", "main-3"]

    def location(self, item):
        return reverse(item)

class StaticSitemap2(Sitemap):

    def items(self):
        return ["main-4", "main-5", "main-6", "main-2"]

    def location(self, item):
        return reverse(item)