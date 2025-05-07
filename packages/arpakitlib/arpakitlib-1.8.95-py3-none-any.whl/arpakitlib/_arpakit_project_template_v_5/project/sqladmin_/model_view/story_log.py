import sqlalchemy

from project.sqladmin_.model_view.common import SimpleMV
from project.sqlalchemy_db_.sqlalchemy_model import StoryLogDBM


class StoryLogMV(SimpleMV, model=StoryLogDBM):
    name = "StoryLog"
    name_plural = "StoryLogs"
    column_list = sqlalchemy.inspect(StoryLogDBM).columns
    form_columns = [
        StoryLogDBM.slug,
        StoryLogDBM.level,
        StoryLogDBM.type,
        StoryLogDBM.title,
        StoryLogDBM.extra_data
    ]
    column_sortable_list = sqlalchemy.inspect(StoryLogDBM).columns
    column_default_sort = [
        (StoryLogDBM.creation_dt, True)
    ]
    column_searchable_list = [
        StoryLogDBM.id,
        StoryLogDBM.long_id,
        StoryLogDBM.slug,
    ]
