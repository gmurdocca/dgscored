from django.views.generic.base import RedirectView
from django.conf.urls import include, url
from rest_framework import routers
from django.contrib import admin
import dgs.views


admin.autodiscover()


router = routers.DefaultRouter()
router.register(r'api/player', dgs.views.PlayerViewSet)
router.register(r'api/contestant', dgs.views.ContestantViewSet)
router.register(r'api/hole', dgs.views.HoleViewSet)
router.register(r'api/layout', dgs.views.LayoutViewSet)
router.register(r'api/course', dgs.views.CourseViewSet)
router.register(r'api/score', dgs.views.ScoreViewSet)
router.register(r'api/card', dgs.views.CardViewSet)
router.register(r'api/award', dgs.views.AwardViewSet)
router.register(r'api/event', dgs.views.EventViewSet)
router.register(r'api/league', dgs.views.LeagueViewSet)


urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(permanent=False, url='/static/favicon.ico')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', dgs.views.home, name='home'),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/$', router.get_api_root_view()),
    url(r'^api/docs/', include('rest_framework_swagger.urls')),
    url(r'^', include(router.urls)),
]


