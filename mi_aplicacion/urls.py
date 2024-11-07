# blyinpredd/urls.py
from django.urls import path
from .views import index_view, login_view, register_view, recuperar,reporte,logout_view,save_recomendaciones_view, restablecer

urlpatterns = [
    path('', index_view, name='index'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('recuperar/', recuperar, name='Recuperar'),
    path('reporte/', reporte, name='Reporte'),
    path('logout/', logout_view, name='logout'),
    path('guardar_recomendaciones/', save_recomendaciones_view, name='guardar_recomendaciones'),
    path('restablecer/<uuid:token>/', restablecer, name='Restablecer'),
    
    # path('latest/', latest_record_view, name='latest_record'),
    # path('blog/', blog_view, name='blog'), 
]