from django.urls import include, path

from core.urls import get_path
from contract.views import (
    APP_LABEL,
    SettingsContractListView,
    ContractCloseView,
    EmployeeListView, EmployeeChangeView,
    ProjectsView,
    # FilterContractView,
    ValueChangeView,
    ArchiveListView, ArchiveChangeView, ArchiveHistoryView,
)


urlpatterns = [
    # path('filter/', FilterContractView.as_view(), name='filter'),
    path('valuechange/', ValueChangeView.as_view()),
    # path('pdf/', PDFView.as_view(), name='pdf'),

    path('', ProjectsView.as_view(), name='home'),
    path('', include(get_path(APP_LABEL))),

    path('contract/', include([

        # path('', ContractListView.as_view(), name='main_contract_list'),
        path('<slug:slug>/close/', ContractCloseView.as_view(),
             name='contract_close'),
    ])),

    path('account/contract_list_change/', SettingsContractListView.as_view(),
         name="contract_list_change"),

    path('archive/contract/<slug:slug>/', include([
        path('', ArchiveListView.as_view(), name='archive_contract_list'),
        path('view', ArchiveChangeView.as_view(),
             name='archive_contract_change'),
        path('history', ArchiveHistoryView.as_view(),
             name='archive_contract_history'),
    ])),

    path('employee/<slug:slug>/', include([
        path('', EmployeeListView.as_view(), name='employee_list'),
        path('change', EmployeeChangeView.as_view(), name='employee_change'),
    ])),
]

