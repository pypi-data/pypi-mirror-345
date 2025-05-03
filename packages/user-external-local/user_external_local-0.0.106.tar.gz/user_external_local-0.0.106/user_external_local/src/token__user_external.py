# from database_mysql_local.connector import Connector
from database_mysql_local.generic_crud import GenericCRUD
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.LoggerLocal import Logger
from logger_local.MetaLogger import MetaLogger
from mysql.connector.errors import IntegrityError

USER_EXTERNAL_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 115
USER_EXTERNAL_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = "user_external_local_python"
DEVELOPER_EMAIL = "idan.a@circ.zone"
object_init = {
    "component_id": USER_EXTERNAL_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    "component_name": USER_EXTERNAL_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    "component_category": LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": DEVELOPER_EMAIL,
}

USER_EXTERNAL_SCHEMA_NAME = "user_external"
TOKEN_USER_EXTERNAL_TABLE_NAME = "token__user_external_table"
TOKEN_USER_EXTERNAL_VIEW_NAME = "token__user_external_view"
TOKEN_USER_EXTERNAL_ID_COLUMN_NAME = "token__user_external_id"

logger = Logger.create_logger(object=object_init)


class TokenUserExternals(GenericCRUD, metaclass=MetaLogger, object=object_init):
    def __init__(self, is_test_data: bool = False):
        super().__init__(
            default_schema_name=USER_EXTERNAL_SCHEMA_NAME,
            default_table_name=TOKEN_USER_EXTERNAL_TABLE_NAME,
            default_view_table_name=TOKEN_USER_EXTERNAL_VIEW_NAME,
            default_column_name=TOKEN_USER_EXTERNAL_ID_COLUMN_NAME,
            is_test_data=is_test_data,
        )

    def insert_or_update_user_external_access_token(
        self,
        *,
        user_external_id: int,
        name: str,
        profile_id: int,
        access_token: str,
        expiry=None,
        refresh_token: str = None,
    ) -> None:
        """
        Inserts or updates a token for a user external record
        """
        object_start = {
            "user_external_id": user_external_id,
            "name": name,
            "access_token": access_token,
            "expiry": expiry,
            "refresh_token": refresh_token,
        }
        logger.start(object=object_start)

        # Check if token already exists
        current_token = self.get_access_token(
            user_external_id=user_external_id, name=name
        )

        # Prepare data dictionary
        data_dict = {
            "user_external_id": user_external_id,
            "name": name,
            "access_token": access_token,
            "expiry": expiry if expiry is not None else "",
            "refresh_token": refresh_token if refresh_token is not None else "",
        }

        if current_token is not None:
            # Update existing token
            self.update_access_token(
                user_external_id=user_external_id,
                name=name,
                access_token=access_token,
                expiry=expiry,
                refresh_token=refresh_token,
            )
            logger.info("Token updated", object=data_dict)
        else:
            # Insert new token
            try:
                self.insert(
                    schema_name=USER_EXTERNAL_SCHEMA_NAME,
                    table_name=TOKEN_USER_EXTERNAL_TABLE_NAME,
                    data_dict=data_dict,
                )
                logger.info("Token inserted", object=data_dict)
            except IntegrityError as e:
                logger.error(
                    log_message="IntegrityError",
                    object={
                        "data_dict": data_dict,
                        "error": str(e),
                    },
                )
                self.update_access_token(
                    user_external_id=user_external_id,
                    name=name,
                    access_token=access_token,
                    expiry=expiry,
                    refresh_token=refresh_token,
                )
                logger.info("Token updated after IntegrityError", object=data_dict)
            except Exception as e:
                logger.error(
                    log_message="Error inserting token",
                    object={
                        "data_dict": data_dict,
                        "error": str(e),
                    },
                )
                raise e

            try:
                data_dict_profile = {
                    "user_external_id": user_external_id,
                    "profile_id": profile_id,
                }
                self.insert(
                    schema_name="profile_user_external",
                    table_name="profile_user_external_table",
                    data_dict=data_dict_profile,
                )
                logger.info(
                    "Token inserted into profile_user_external", object=data_dict
                )
            except Exception as e:
                logger.error(
                    log_message="Error inserting token into profile_user_external",
                    object={
                        "data_dict": data_dict,
                        "error": str(e),
                    },
                )
                raise e

    def get_access_token(self, *, user_external_id: int, name: str) -> str:
        """
        Gets the access token for a specific user external record and name
        """
        object_start = {"user_external_id": user_external_id, "name": name}
        logger.start(object=object_start)

        access_token = self.select_one_value_by_where(
            schema_name=USER_EXTERNAL_SCHEMA_NAME,
            view_table_name=TOKEN_USER_EXTERNAL_VIEW_NAME,
            select_clause_value="access_token",
            where="user_external_id=%s AND name=%s AND end_timestamp IS NULL",
            params=(user_external_id, name),
            order_by="updated_timestamp DESC",
        )

        return access_token

    def update_access_token(
        self,
        *,
        user_external_id: int,
        name: str,
        access_token: str,
        expiry=None,
        refresh_token: str = None,
    ) -> None:
        """
        Updates an existing access token
        """
        object_start = {
            "user_external_id": user_external_id,
            "name": name,
            "access_token": access_token,
        }
        logger.start(object=object_start)

        data_dict = {"access_token": access_token}

        if expiry is not None:
            data_dict["expiry"] = expiry

        if refresh_token is not None:
            data_dict["refresh_token"] = refresh_token

        try:
            self.update_by_where(
                schema_name=USER_EXTERNAL_SCHEMA_NAME,
                table_name=TOKEN_USER_EXTERNAL_TABLE_NAME,
                where="user_external_id=%s AND name=%s AND end_timestamp IS NULL",
                params=(user_external_id, name),
                data_dict=data_dict,
            )
            logger.info("Token updated", object=object_start)
        except Exception as e:
            logger.error(
                log_message="Error updating token",
                object={
                    "user_external_id": user_external_id,
                    "name": name,
                    "data_dict": data_dict,
                    "error": str(e),
                },
            )
            raise e

    def delete_access_token(self, *, user_external_id: int, name: str) -> None:
        """
        Marks a token as deleted by setting end_timestamp to current time
        """
        object_start = {
            "user_external_id": user_external_id,
            "name": name,
        }
        logger.start(object=object_start)

        try:
            self.delete_by_where(
                schema_name=USER_EXTERNAL_SCHEMA_NAME,
                table_name=TOKEN_USER_EXTERNAL_TABLE_NAME,
                where="user_external_id=%s AND name=%s AND end_timestamp IS NULL",
                params=(user_external_id, name),
            )
            logger.info("Token deleted", object=object_start)
        except Exception as e:
            logger.error(
                log_message="Error deleting token",
                object={
                    "user_external_id": user_external_id,
                    "name": name,
                    "error": str(e),
                },
            )
            raise e

    def get_auth_details(self, *, user_external_id: int, name: str) -> tuple:
        """
        Gets authentication details including access_token, refresh_token, and expiry
        """
        object_start = {
            "user_external_id": user_external_id,
            "name": name,
        }
        logger.start(object=object_start)

        try:
            result = self.select_one_tuple_by_where(
                schema_name=USER_EXTERNAL_SCHEMA_NAME,
                view_table_name=TOKEN_USER_EXTERNAL_VIEW_NAME,
                select_clause_value="access_token, refresh_token, expiry",
                where="user_external_id=%s AND name=%s AND end_timestamp IS NULL",
                params=(user_external_id, name),
                order_by="updated_timestamp DESC",
            )

            if not result:
                logger.error(log_message="Token not found", object=object_start)
                return None

            return result
        except Exception as e:
            logger.error(
                log_message="Error getting auth details",
                object={
                    "user_external_id": user_external_id,
                    "name": name,
                    "error": str(e),
                },
            )
            raise e

    def get_token_by_user_external_id(self, *, user_external_id: int) -> dict:
        """
        Gets all tokens for a specific user external ID
        """
        object_start = {"user_external_id": user_external_id}
        logger.start(object=object_start)

        try:
            tokens = self.select_multi_dict_by_where(
                schema_name=USER_EXTERNAL_SCHEMA_NAME,
                view_table_name=TOKEN_USER_EXTERNAL_VIEW_NAME,
                select_clause_value="*",
                where="user_external_id=%s AND end_timestamp IS NULL",
                params=(user_external_id,),
                order_by="updated_timestamp DESC",
            )

            return tokens
        except Exception as e:
            logger.error(
                log_message="Error getting tokens by user_external_id",
                object={
                    "user_external_id": user_external_id,
                    "error": str(e),
                },
            )
            raise e
