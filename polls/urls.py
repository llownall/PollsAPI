from django.urls import path
from rest_framework import routers
from rest_framework.authtoken.views import ObtainAuthToken

from polls import views

router = routers.SimpleRouter()
router.register(r'polls', views.PollViewSet)
router.register(r'questions', views.QuestionViewSet)

urlpatterns = [
    path('obtain-token/', ObtainAuthToken.as_view()),

    path('answers/<int:pk>/', views.AnswerDetail.as_view()),

    path('polls/active/', views.ActivePollList.as_view()),
    path('answer-question/', views.AnswerQuestionView.as_view()),
    path('polls/passed/<int:user_id>', views.UserResultsList.as_view()),
]

urlpatterns += router.urls
