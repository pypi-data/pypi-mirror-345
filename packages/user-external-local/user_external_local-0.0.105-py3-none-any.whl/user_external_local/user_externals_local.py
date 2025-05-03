from database_mysql_local.connector import Connector
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
USER_EXTERNAL_TABLE_NAME = "user_external_table"
USER_EXTERNAL_VIEW_NAME = "user_external_view"
USER_EXTERNAL_ID_COLUMN_NAME = "user_external_id"

logger = Logger.create_logger(object=object_init)

# TODO Can we use this view to get the password_clear_text in new method called get_password_clear_text_by_system_id_and_profile_id()?
#        SELECT * FROM user_external_pii.user_external_pii_general_view;


class UserExternalsLocal(GenericCRUD, metaclass=MetaLogger, object=object_init):
    def __init__(self, is_test_data: bool = False):
        super().__init__(
            default_schema_name=USER_EXTERNAL_SCHEMA_NAME,
            default_table_name=USER_EXTERNAL_TABLE_NAME,
            default_view_table_name=USER_EXTERNAL_VIEW_NAME,
            default_column_name=USER_EXTERNAL_ID_COLUMN_NAME,
            is_test_data=is_test_data,
        )

    # TODO When creating a new user-external should add url to the person_url (otherwise profile_url).
    def insert_or_update_user_external_access_token(
        self,
        *,
        system_id: int,
        username: str,
        access_token: str,
        profile_id: int,
        expiry=None,
        refresh_token: str = None,
    ) -> None:
        object_start = {  # noqa
            "username": username,
            "main.profile_id": profile_id,
            "system_id": system_id,
            "access_token": access_token,
            "expiry": expiry,
            "refresh_token": refresh_token,
        }
        logger.start(object=object_start)
        # TODO current_access_token =
        current_token = self.get_access_token(
            system_id=system_id, username=username, profile_id=profile_id
        )
        if current_token is not None:
            self.delete_access_token(
                system_id=system_id, username=username, profile_id=profile_id
            )

        # TODO: move to generic crud class to be able to see the logs

        try:
            connection = Connector.connect("user_external")
            if expiry is None:
                expiry = ""
            if refresh_token is None:
                refresh_token = ""
            # old query
            query_insert_external = (
                "INSERT INTO user_external_table (system_id,username,access_token,expiry,refresh_token)"
                " VALUES (%s,%s,%s,%s,%s)"
            )
            values = (system_id, username, access_token, expiry, refresh_token)
            cursor = connection.cursor()
            cursor.execute(query_insert_external, values)
            user_external_id_new = cursor.lastrowid()
            values = (user_external_id_new, profile_id)
            connection.commit()
        except Exception as e:
            logger.error(
                log_message="Error inserting user_external",
                object={
                    "query_insert_external": query_insert_external,
                    "values": values,
                    "error": str(e),
                },
            )
            raise e
        try:
            connection = Connector.connect("user_external")

            # new query
            query_insert_external_token = (
                "INSERT INTO token__user_external_table (user_external_id,name,access_token,expiry,refresh_token)"
                " VALUES (%s,%s,%s,%s,%s)"
            )
            values_token = (
                user_external_id_new,
                username,
                access_token,
                expiry,
                refresh_token,
            )

            cursor.execute(query_insert_external_token, values_token)
            connection.commit()
        except IntegrityError as e:
            logger.error(
                log_message="IntegrityError",
                object={
                    "query_insert_external_token": query_insert_external_token,
                    "values_token": values_token,
                    "error": str(e),
                },
            )
            update_query = (
                "UPDATE token__user_external_table SET access_token = %s, expiry = %s, refresh_token = %s"
                " WHERE user_external_id = %s AND name = %s"
            )
            update_values = (
                access_token,
                expiry,
                refresh_token,
                user_external_id_new,
                username,
            )
            cursor.execute(update_query, update_values)
            logger.info(
                log_message="IntegrityError - updated",
                object={
                    "update_query": update_query,
                    "update_values": update_values,
                },
            )
            connection.commit()
        except Exception as e:
            logger.error(
                log_message="Error inserting token__user_external",
                object={
                    "query_insert_external_token": query_insert_external_token,
                    "values_token": values_token,
                    "error": str(e),
                },
            )
            raise e

        try:
            connection_profile = Connector.connect("profile_user_external")
            query_insert_profile_user_external = "INSERT INTO profile_user_external_table (user_external_id,profile_id) VALUES (%s,%s)"
            cursor = connection_profile.cursor()
            cursor.execute(query_insert_profile_user_external, values)
            object_info = {
                "username": username,
                "system_id": system_id,
                "profile_id": profile_id,
                "access_token": access_token,
            }
            logger.info("external user inserted", object=object_info)
            connection_profile.commit()
        except Exception as e:
            logger.error(
                log_message="Error inserting profile_user_external",
                object={
                    "query_insert_profile_user_external": query_insert_profile_user_external,
                    "values": values,
                    "error": str(e),
                },
            )
            raise e

    def get_access_token_by_username_and_system_id(
        self, *, username: str, system_id: int
    ) -> str:
        access_token = None
        object_start = {"username": username, "system_id": system_id}  # noqa
        # TODO Can we connect one time in the constructor?
        # TODO Shall we move to Generic Crud?

        try:
            connection = Connector.connect("user_external")
            # TODO: move to generic crud
            query_get = "SELECT access_token FROM user_external.user_external_view WHERE username=%s AND system_id=%s"
            cursor = connection.cursor()
            cursor.execute(query_get, (username, system_id))
            access_token = cursor.fetchone()
        except Exception as e:
            logger.error(
                log_message="Error getting access_token",
                object={
                    "query_get": query_get,
                    "username": username,
                    "system_id": system_id,
                    "error": str(e),
                },
            )
            raise e

        return access_token

    # TODO Shall we default the profile_id to profile_id from User Context?
    # TODO Why we have two methods which looks very similar?
    def get_access_token(
        self, *, system_id: int, username: str, profile_id: int
    ) -> str:
        access_token = None
        object_start = {  # noqa
            "username": username,
            "profile_id": profile_id,
            "system_id": system_id,
        }

        try:
            connection = Connector.connect("user_external")
            # TODO Either as profile_user_external (preferable) or pue
            query_get = (
                "SELECT access_token FROM user_external.user_external_view as eu join "
                "profile_user_external.profile_user_external_table as eup on eu.user_external_id=eup.user_external_id WHERE"
                " eu.username=%s AND eu.system_id=%s And eup.profile_id=%s AND eu.end_timestamp IS NULL"
                " ORDER BY eu.updated_timestamp DESC LIMIT 1"
            )
            cursor = connection.cursor()
            cursor.execute(query_get, (username, system_id, profile_id))
            access_token = cursor.fetchone()
        except Exception as e:
            logger.error(
                log_message="Error getting access_token",
                object={
                    "query_get": query_get,
                    "username": username,
                    "system_id": system_id,
                    "profile_id": profile_id,
                    "error": str(e),
                },
            )
            raise e

        return access_token

    # TODO username -> username_str
    def update_user_external_access_token(
        self,
        *,
        system_id: int,
        username: str,
        profile_id: int,
        access_token,
        expiry=None,
        refresh_token: str = None,
    ) -> None:
        object_start = {  # noqa
            "username": username,
            "system_id": system_id,
            "profile_id": profile_id,
            "access_token": access_token,
        }

        try:
            connection = Connector.connect("user_external")
            update_query = (
                "UPDATE user_external.user_external_table AS eu JOIN profile_user_external.profile_user_external_table AS eup"
                " ON eu.user_external_id = eup.user_external_id SET eu.access_token = %s WHERE eu.username = %s AND"
                " eu.system_id = %s AND eup.profile_id = %s;"
            )
            values = (access_token, username, system_id, profile_id)
            cursor = connection.cursor()
            cursor.execute(update_query, values)
            object_info = {
                "username": username,
                "system_id": system_id,
                "profile_id": profile_id,
                "access_token": access_token,
            }
            logger.info("external user updated", object=object_info)
            connection.commit()
        except Exception as e:
            logger.error(
                log_message="Error updating access_token",
                object={
                    "update_query": update_query,
                    "values": values,
                    "error": str(e),
                },
            )
            raise e

    def delete_access_token(self, *, system_id: int, username: str, profile_id: int):
        object_start = {  # noqa
            "username": username,
            "system_id": system_id,
            "profile_id": profile_id,
        }

        try:
            connection = Connector.connect("user_external")
            cursor = connection.cursor()
            update_query = (
                "UPDATE user_external.user_external_table AS eu JOIN profile_user_external.profile_user_external_table AS eup"
                " ON eu.user_external_id = eup.user_external_id SET eu.end_timestamp = now() WHERE eu.username = %s AND"
                " eu.system_id = %s AND eup.profile_id = %s;"
            )
            values = (username, system_id, profile_id)
            cursor.execute(update_query, values)
            object_info = {
                "username": username,
                "system_id": system_id,
                "profile_id": profile_id,
            }
            logger.info("external user updated", object=object_info)
            connection.commit()
        except Exception as e:
            logger.error(
                log_message="Error deleting access_token",
                object={
                    "update_query": update_query,
                    "values": values,
                    "error": str(e),
                },
            )
            raise e

    def get_auth_details_by_system_id_and_profile_id(
        self, *, system_id: int, profile_id: int
    ) -> tuple:
        object_start = {"system_id": system_id, "profile_id": profile_id}  # noqa
        logger.warning(
            log_message="This static method is deprecated, "
            "please use the non static method",
        )

        try:
            connection = Connector.connect("user_external")
            query_get_all = (
                "SELECT eu.user_external_id, access_token,refresh_token,expiry FROM user_external.user_external_view AS eu"
                " JOIN profile_user_external.profile_user_external_table AS eup on eu.user_external_id=eup.user_external_id"
                " WHERE eu.system_id=%s AND eup.profile_id=%s order BY eu.start_timestamp DESC LIMIT 1"
            )
            cursor = connection.cursor()
            cursor.execute(query_get_all, (system_id, profile_id))
            auth_details = cursor.fetchone()
        except Exception as e:
            logger.error(
                log_message="Error getting auth_details",
                object={
                    "query_get_all": query_get_all,
                    "system_id": system_id,
                    "profile_id": profile_id,
                    "error": str(e),
                },
            )
            raise e
        return auth_details

    def get_auth_details(
        self, *, system_id: int, username: str, profile_id: int
    ) -> None:
        auth_details = None
        object_start = {
            "username": username,
            "system_id": system_id,
            "profile_id": profile_id,
        }
        logger.start(object=object_start)

        try:
            connection = Connector.connect("user_external")
            query_get_all = (
                "SELECT access_token,refresh_token,expiry FROM user_external.user_external_view AS eu JOIN"
                " profile_user_external.profile_user_external_view AS eup ON eu.user_external_id=eup.user_external_id WHERE"
                " eu.username=%s AND eu.system_id=%s AND eup.profile_id=%s ORDER BY eu.start_timestamp DESC LIMIT 1"
            )
            cursor = connection.cursor()
            cursor.execute(query_get_all, (username, system_id, profile_id))
            auth_details_list = cursor.fetchall()
            if auth_details_list:
                auth_details = auth_details_list[0]
            else:
                logger.error(
                    log_message="user external not found",
                    object={"auth_details_list": auth_details_list},
                )
        except Exception as e:
            logger.error(
                log_message="Error getting auth_details",
                object={
                    "query_get_all": query_get_all,
                    "username": username,
                    "system_id": system_id,
                    "profile_id": profile_id,
                    "error": str(e),
                },
            )
            raise e

        return auth_details

    def get_credential_storage_id_by_system_id_and_profile_id(
        self, *, system_id: int, profile_id: int
    ):
        credential_storage_id = self.select_one_value_by_where(
            schema_name=USER_EXTERNAL_SCHEMA_NAME,
            view_table_name=USER_EXTERNAL_VIEW_NAME,
            select_clause_value="credential_storage_id",
            where=f"system_id={system_id} AND username={profile_id}",
        )

        return credential_storage_id

    @staticmethod
    def get_recipient_user_dict(where: str) -> dict:
        # Return all the usernames and ids that the recipient has
        user_external_generic_crud = GenericCRUD(default_schema_name="user_external")

        username = user_external_generic_crud.select_multi_value_by_where(
            schema_name="user_external",
            view_table_name="user_external_general_view",
            select_clause_value="username",
            where=where,
        )
        user_external_id = user_external_generic_crud.select_multi_value_by_where(
            schema_name="user_external",
            view_table_name="user_external_general_view",
            select_clause_value="user_external_id",
            where=where,
        )
        telephone_number = user_external_generic_crud.select_multi_value_by_where(
            schema_name="user_external",
            view_table_name="user_external_general_view",
            select_clause_value="phone.full_number_normalized",
            where=where,
        )

        user_dict = {
            "username": list(username),
            "user_external_id": list(user_external_id),
            "phone.full_number_normalized": list(telephone_number),
        }
        return user_dict
