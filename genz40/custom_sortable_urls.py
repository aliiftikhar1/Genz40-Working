# custom_sortable_urls.py
from django.urls import path
from backend.views import CustomSortableUpdateView

urlpatterns = [
    path('custom_adminsortable2_update/', CustomSortableUpdateView.as_view(), name='adminsortable2_update'),
]
