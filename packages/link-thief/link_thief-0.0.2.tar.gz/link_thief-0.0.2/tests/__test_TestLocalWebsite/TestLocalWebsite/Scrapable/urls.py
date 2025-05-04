from .views import LinkScraperView 
from django.urls import path, include

urlpatterns = [
    path('1/', LinkScraperView.as_view(template_name="Scrapable/main.html"), name="main"),
    path('2/', LinkScraperView.as_view(template_name="Scrapable/main-2.html"), name="main-2"),
    path('3/', LinkScraperView.as_view(template_name="Scrapable/main-3.html"), name="main-3"),
    path('4/', LinkScraperView.as_view(template_name="Scrapable/main-4.html"), name="main-4"),
    path('5/', LinkScraperView.as_view(template_name="Scrapable/main-5.html"), name="main-5"),
    path('6/', LinkScraperView.as_view(template_name="Scrapable/main-6.html"), name="main-6"),
]
