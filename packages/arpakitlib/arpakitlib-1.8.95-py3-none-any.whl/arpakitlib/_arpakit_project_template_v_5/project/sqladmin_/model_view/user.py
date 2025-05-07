import sqlalchemy

from project.sqladmin_.model_view.common import SimpleMV
from project.sqlalchemy_db_.sqlalchemy_model import UserDBM


class UserMV(SimpleMV, model=UserDBM):
    name = "User"
    name_plural = "Users"
    column_list = [
        UserDBM.id,
        UserDBM.long_id,
        UserDBM.slug,
        UserDBM.creation_dt,
        UserDBM.email,
        UserDBM.username,
        UserDBM.roles,
        UserDBM.is_active,
        UserDBM.password,
        UserDBM.tg_id,
        UserDBM.tg_data,
        UserDBM.tg_bot_last_action_dt,
        UserDBM.extra_data
    ]
    form_columns = [
        UserDBM.slug,
        UserDBM.email,
        UserDBM.username,
        UserDBM.roles,
        UserDBM.is_active,
        UserDBM.password,
        UserDBM.tg_id,
        UserDBM.tg_data,
        UserDBM.tg_bot_last_action_dt,
        UserDBM.extra_data
    ]
    column_sortable_list = sqlalchemy.inspect(UserDBM).columns
    column_default_sort = [
        (UserDBM.creation_dt, True)
    ]
    column_searchable_list = [
        UserDBM.id,
        UserDBM.long_id,
        UserDBM.slug,
        UserDBM.email,
        UserDBM.username,
        UserDBM.password,
        UserDBM.tg_id
    ]
