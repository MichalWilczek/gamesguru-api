from django.urls import path
from ninja import NinjaAPI

from gamesguru.api import router as main_router


api = NinjaAPI()
api.add_router("", main_router.router)

urlpatterns = [
    path("", api.urls),
]
