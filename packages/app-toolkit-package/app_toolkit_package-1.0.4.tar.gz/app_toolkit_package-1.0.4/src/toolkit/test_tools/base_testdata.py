import uuid
from functools import partial

from ..auth.services.password import hash_password
from ..types_app import Any, TypeFieldsDict, TypeFieldsListNone, TypeModel

__all__ = [
    "Data",
    "UserData",
]


class Data:
    """
    Attributes:
        model: TypeModel - Model class
        create_data: dict[str, Any] - all not-nullable (required) fields with valid values
        update_data: dict[str, Any] = {} - arbitrary fields with valid values
        default_data: dict[str, Any] = {} - all default fields (besides `id`) with default values
        pk_fields: list[str] = [] - all primary key fields (besides `id`)
        unique_fields: list[str] = [] - all unique fields (besides `id`)
        indexed_fields: list[str] = [] - all indexed fields
        nullable_fields: list[str] = [] - all nullable fields
    """

    @staticmethod
    def get_val_or_sub(value: Any | None, substitution: Any):
        # used here and in base_test_model.py
        return value or substitution

    def add_id(self, *, as_uuid: bool = True, **data) -> dict[str, Any]:
        # used here and in base_test_crud.py
        return {"id": self.uuid if as_uuid else str(self.uuid), **data}

    def get_test_obj(self):
        return self.model(**self.add_id(**self.create_data))

    def __init__(
        self,
        *,
        model: TypeModel,
        create_data: TypeFieldsDict,
        update_data: TypeFieldsDict | None = None,
        default_data: TypeFieldsDict | None = None,
        pk_fields: TypeFieldsListNone = None,
        unique_fields: TypeFieldsListNone = None,
        indexed_fields: TypeFieldsListNone = None,
        nullable_fields: TypeFieldsListNone = None,
    ) -> None:
        # Manually set data =========================================
        self.model = model
        self.create_data = create_data
        self.update_data = self.get_val_or_sub(update_data, create_data)
        self.default_data = self.get_val_or_sub(default_data, {})
        self.pk_fields = self.get_val_or_sub(pk_fields, []) + ["id"]
        self.unique_fields = self.get_val_or_sub(unique_fields, [])
        self.indexed_fields = self.get_val_or_sub(indexed_fields, [])
        self.nullable_fields = self.get_val_or_sub(nullable_fields, [])
        self.uuid = uuid.uuid4()
        # Calculated data ===========================================
        _expected_create = {
            **{}.fromkeys(self.nullable_fields),
            **self.default_data,
            **self.create_data,
        }
        _expected_update = {
            **_expected_create,
            **self.update_data,
        }

        # Model
        self.dump_initial = {
            # **{c.name: None for c in self.model.__table__.c},
            **{}.fromkeys(c.name for c in self.model.__table__.c),
            **self.create_data,
        }

        # CRUD - create_data and update_data will be manipulated with
        # add_id in the base_test_crud.py
        # self.get_test_obj = lambda *args, **kwargs: self.model(
        #     **self.add_id(**self.create_data)
        # )
        self.expected_create = self.add_id(**_expected_create)  # type: ignore [arg-type]
        self.expected_update = self.add_id(**_expected_update)  # type: ignore [arg-type]

        # API/Bot
        jsonify = partial(self.add_id, as_uuid=False)
        self.create_data_json = jsonify(**self.create_data)
        self.update_data_json = jsonify(**self.update_data)
        self.expected_response_json_create = jsonify(**_expected_create)
        self.expected_response_json_update = jsonify(**_expected_update)


class UserData(Data):
    def __init__(
        self,
        *,
        model: TypeModel,
        create_data: TypeFieldsDict,
        update_data: TypeFieldsDict | None = None,
        default_data: TypeFieldsDict | None = None,
        pk_fields: TypeFieldsListNone = None,
        unique_fields: TypeFieldsListNone = None,
        indexed_fields: TypeFieldsListNone = None,
        nullable_fields: TypeFieldsListNone = None,
    ):
        self.password = create_data["password"]
        create_data["password"] = hash_password(self.password)
        super().__init__(
            model=model,
            create_data=create_data,
            update_data=update_data,
            default_data=default_data,
            pk_fields=pk_fields,
            unique_fields=unique_fields,
            indexed_fields=indexed_fields,
            nullable_fields=nullable_fields,
        )
        self.expected_response_json_create.pop("password")
        self.expected_response_json_update.pop("password")

    def get_login_data(self):
        return {
            "username": self.create_data["email"],
            "password": self.password,
        }

    def get_expected_me_data(self):
        return dict(
            id=str(self.uuid),
            email=self.create_data["email"],
            full_name=(
                f"{self.create_data.get('first_name')} "
                f"{self.create_data.get('last_name')}"
            ),
        )
