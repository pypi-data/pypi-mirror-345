from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps import views as sitemaps_views
from django.views.generic.base import TemplateView
from Scrapable.sitemap import StaticSitemap1, StaticSitemap2

sitemaps = {
    "static1": StaticSitemap1,
    "static2": StaticSitemap2,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('scrapable/', include('Scrapable.urls')),
    path(
        "sitemap.xml",
        sitemaps_views.index,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.index",
    ),
    path(
        "sitemap-<section>.xml",
        sitemaps_views.sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # robots.txt path below
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
]
