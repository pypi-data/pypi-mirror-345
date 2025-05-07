import sqlalchemy

from project.sqladmin_.model_view.common import SimpleMV
from project.sqlalchemy_db_.sqlalchemy_model import ApiKeyDBM


class ApiKeyMV(SimpleMV, model=ApiKeyDBM):
    name = "ApiKey"
    name_plural = "ApiKeys"
    column_list = sqlalchemy.inspect(ApiKeyDBM).columns
    form_columns = [
        ApiKeyDBM.slug,
        ApiKeyDBM.title,
        ApiKeyDBM.value,
        ApiKeyDBM.is_active,
    ]
    column_sortable_list = sqlalchemy.inspect(ApiKeyDBM).columns
    column_default_sort = [
        (ApiKeyDBM.creation_dt, True)
    ]
    column_searchable_list = [
        ApiKeyDBM.id,
        ApiKeyDBM.long_id,
        ApiKeyDBM.slug,
        ApiKeyDBM.value,
    ]
