from sqladmin import ModelView

from models.user import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.name, User.is_active]
    form_excluded_columns = [User.created_at, User.updated_at, User.chats, User.telegram_id]