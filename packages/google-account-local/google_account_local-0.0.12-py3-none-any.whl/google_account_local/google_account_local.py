import hashlib
import json
import os
import time

# import webbrowser

from database_mysql_local.generic_crud import GenericCRUD
from google.auth import exceptions
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from logger_local.MetaLogger import MetaLogger
from python_sdk_remote.utilities import our_get_env

from user_external_local.user_externals_local import UserExternalsLocal
from user_external_local.token__user_external import TokenUserExternals

from .google_account_local_constants import GoogleAccountLocalConstants

SLEEP_TIME = 5
TIMEOUT = 50

USER_EXTERNAL_SCHEMA_NAME = "user_external"
USER_EXTERNAL_TABLE_NAME = "user_external_table"
USER_EXTERNAL_VIEW_NAME = "user_external_view"
USER_EXTERNAL_DEFAULT_COLUMN_NAME = "user_external_id"

# Static token details
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/contacts",
    "openid",
]  # Both scopes must be allowed within the project!


class GoogleAccountLocal(
    GenericCRUD,
    metaclass=MetaLogger,
    object=GoogleAccountLocalConstants.LoggerSetupConstants.GOOGLE_ACCOUNT_LOCAL_CODE_LOGGER_OBJECT,
):
    """
    Manages OAuth 2.0 authentication with Google services.

    This class handles the full authentication flow with Google, including:
    - Initial authorization and token acquisition
    - Token storage and management in database
    - Token refresh when credentials expire
    - User verification against expected email
    """

    def __init__(self, is_test_data: bool = False) -> None:
        """
        Initialize the GoogleAccountLocal instance.

        Sets up database connections, loads environment variables, and initializes
        the necessary properties for Google OAuth authentication.

        Args:
            is_test_data (bool, optional): Flag indicating if test data should be used.
                Defaults to False.
        """
        GenericCRUD.__init__(
            self,
            default_schema_name=USER_EXTERNAL_SCHEMA_NAME,
            default_table_name=USER_EXTERNAL_TABLE_NAME,
            default_view_table_name=USER_EXTERNAL_VIEW_NAME,
            default_column_name=USER_EXTERNAL_DEFAULT_COLUMN_NAME,
            is_test_data=is_test_data,
        )

        self.user_externals_local = UserExternalsLocal()
        self.token__user_external = TokenUserExternals()

        self.service = None
        self.creds = None
        self.user_email = our_get_env(
            "GOOGLE_USER_EXTERNAL_USERNAME", raise_if_empty=False, raise_if_not_found=False, default=None
        )
        self.google_client_id = our_get_env("GOOGLE_CLIENT_ID", raise_if_empty=True)
        self.google_client_secret = our_get_env(
            "GOOGLE_CLIENT_SECRET", raise_if_empty=True
        )
        # self.google_port_for_authentication = int(our_get_env("GOOGLE_PORT_FOR_AUTHENTICATION", raise_if_empty=True))
        self.google_redirect_uris = our_get_env(
            "GOOGLE_REDIRECT_URIS", raise_if_empty=True
        )
        self.google_auth_uri = our_get_env("GOOGLE_AUTH_URI", raise_if_empty=True)
        self.google_token_uri = our_get_env("GOOGLE_TOKEN_URI", raise_if_empty=True)

    def authenticate(self, email: str):
        """
        Authenticate with Google services using OAuth 2.0.

        This method updates the credentials for the Google account associated with the provided email address.
        - for the user_external_table it updates the access_token, refresh_token, and expiry.
        if the user already exists. inserts a new record otherwise.
        - for the token_user_external_table it it always inserts a new record.

        Args:
            email (str): The email address to authenticate with Google.
                This email is used to lookup profile information and
                is verified against the authenticated Google account.

        Raises:
            Exception: If the authenticated email doesn't match the expected email,
                      if no access token is found, or if profile lookup fails.
        """
        user_external_id = None
        profile_id = self.select_one_value_by_column_and_value(
            schema_name="profile",
            view_table_name="profile_view",
            select_clause_value="profile_id",
            column_value=email,
            column_name="profile.main_email_address",
        )
        # If there are no (valid) credentials available, let the user log in.
        if (
            not self.creds or not self.creds.valid
        ):  # TODO: move this to a separate method
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # If self.creds is None but you have a refresh token
                select_result_dict = self.select_one_dict_by_where(
                    schema_name="user_external",
                    view_table_name="user_external_view",
                    select_clause_value="refresh_token, access_token, user_external_id, oauth_state",
                    where="username=%s AND is_refresh_token_valid=TRUE AND system_id=%s",
                    params=(email, GoogleAccountLocalConstants.GOOGLE_SYSTEM_ID),
                    order_by="user_external_id DESC",
                )
                refresh_token = select_result_dict.get("refresh_token")
                access_token = select_result_dict.get("access_token")
                user_external_id = select_result_dict.get("user_external_id")
                oauth_state = select_result_dict.get("oauth_state")
                if self.creds or not refresh_token:
                    user_external_id = self.__authorize(oauth_state=oauth_state)
                else:
                    self.creds = Credentials(
                        token=access_token,
                        refresh_token=refresh_token,
                        token_uri=self.google_token_uri,
                        client_id=self.google_client_id,
                        client_secret=self.google_client_secret,
                    )
                    try:
                        self.creds.refresh(Request())
                    except exceptions.RefreshError as exception:
                        self.logger.error(
                            "google-contact-local Google Refresh token failed.",
                            object={"exception": exception},
                        )
                        exception_message = str(exception)
                        if (
                            "The credentials do not contain the necessary fields"
                            in exception_message
                        ) or (
                            "The credentials returned by the refresh_handler are already expired"
                            in exception_message
                        ):
                            # The refresh token can become an invalid
                            self.update_by_column_and_value(
                                schema_name="user_external",
                                table_name="user_external_table",
                                column_name="refresh_token",
                                column_value=refresh_token,
                                data_dict={"is_refresh_token_valid": False},
                            )
                            # "end_timestamp": datetime.now(ZoneInfo("UTC"))})
                            user_external_id = self.__authorize()

            # Fetch the user's user_email for profile_id in our DB
            # TODO Can we wrap all indirect calls with Api Management?
            self.service = build("oauth2", "v2", credentials=self.creds)
            try:
                user_info = self.service.userinfo().get().execute()
            except Exception:
                user_external_id = self.__authorize()
                user_info = self.service.userinfo().get().execute()
            if user_info.get("email") != email:
                if user_external_id is not None:
                    self.delete_by_column_and_value(
                        schema_name="user_external",
                        table_name="user_external_table",
                        column_name="user_external_id",
                        column_value=user_external_id,
                    )
                raise Exception(
                    "The email address of the connected Google account does not match the provided email."
                )
            self.user_email = user_info.get(
                "email"
            )  # Cannot be "user_email" because we get it from the API
            # is_verified_email = user_info.get("verified_email")
            # user_account_id = user_info.get("id")  # TODO DO we need this?
            # user_picture = user_info.get("picture")  # TODO: save in storage

            # Deserialize the token_data into a Python dictionary
            token_data_dict = json.loads(self.creds.to_json())
            # TODO: The following log is throwing an exception, fix it
            # logger.info("GoogleContact.authenticate", {'token_data_dict': token_data_dict})
            # TODO: What other data can we get from token_data_dict?

            # Extract the access_token, expires_in, and refresh_token to insert into our DB
            access_token = token_data_dict.get("token")
            expires_in = token_data_dict.get("expiry")
            refresh_token = token_data_dict.get("refresh_token")

            if access_token and user_external_id is None:
                # TODO: Do we still need this if case?
                self.token__user_external.insert_or_update_user_external_access_token(
                    user_external_id=user_external_id,
                    name=self.user_email,
                    profile_id=profile_id,
                    access_token=access_token,
                    expiry=expires_in,
                    refresh_token=refresh_token,
                )
                # self.user_externals_local.insert_or_update_user_external_access_token(
                #     system_id=GoogleAccountLocalConstants.GOOGLE_SYSTEM_ID,
                #     username=self.user_email,
                #     # We can't get profile_id by user_email for play1@circ.zone because it's not in profile_view,
                #     # this method will always select from view
                #     profile_id=profile_id,
                #     access_token=access_token,
                #     expiry=expires_in,
                #     refresh_token=refresh_token)
                # TODO Error handling of the above call
            elif access_token and user_external_id is not None:

                self.user_externals_local.insert_or_update_user_external_access_token(
                    system_id=GoogleAccountLocalConstants.GOOGLE_SYSTEM_ID,
                    username=self.user_email,
                    # We can't get profile_id by user_email for play1@circ.zone because it's not in profile_view,
                    # this method will always select from view
                    profile_id=profile_id,
                    access_token=access_token,
                    expiry=expires_in,
                    refresh_token=refresh_token,
                )

                token_data_dict = {
                    "user_external_id": user_external_id,
                    "access_token": access_token,
                    "expiry": expires_in,
                    "refresh_token": refresh_token,
                }
                self.token__user_external.insert(
                    schema_name="user_external",
                    table_name="token__user_external_table",
                    data_dict=token_data_dict,
                )

                # self.update_by_column_and_value(
                #     schema_name="user_external", table_name="user_external_table",
                #     column_name="user_external_id", column_value=user_external_id,
                #     data_dict={"access_token": access_token, "expiry": expires_in, "refresh_token": refresh_token,
                #                "is_refresh_token_valid": True, "username": self.user_email,
                #                "system_id": GoogleAccountLocalConstants.GOOGLE_SYSTEM_ID})
                # data_dict = {"profile_id": profile_id, "user_external_id": user_external_id}
                # self.insert(schema_name="profile_user_external", table_name="profile_user_external_table",
                #             data_dict=data_dict)
            else:
                raise Exception("Access token not found in token_data.")

    def __authorize(self, oauth_state: str = None) -> int:
        """
        Initiate the OAuth 2.0 authorization flow with Google.

        This private method:
        1. Creates an OAuth flow with the configured client credentials
        2. Generates a state parameter and authorization URL
        3. Displays the URL for the user to visit
        4. Polls the database for the authorization code
        5. Exchanges the code for OAuth tokens

        Args:
            oauth_state (str, optional): An existing OAuth state to use.
                Defaults to None, in which case a new state is generated.

        Returns:
            int: The user_external_id of the created/updated record

        Raises:
            Exception: If profile ID is not found for the email
                      or if the auth code is not found in the database
                      within the timeout period
        """
        client_config = {
            "installed": {
                "client_id": self.google_client_id,
                "client_secret": self.google_client_secret,
                "redirect_uris": self.google_redirect_uris,
                "auth_uri": self.google_auth_uri,
                "token_uri": self.google_token_uri,
            }
        }
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        flow = InstalledAppFlow.from_client_config(
            client_config, SCOPES, redirect_uri=self.google_redirect_uris, state=state
        )
        auth_url, _ = flow.authorization_url(
            access_type="offline", prompt="consent"
        )  # access_type='online' won't return a refresh token
        # old: self.creds = flow.run_local_server(port=0)
        # if GOOGLE_REDIRECT_URIS is localhost it must be
        # GOOGLE_REDIRECT_URIS=http://localhost:54415/
        # if the port number is 54415 and we must also pass that port
        # to the run_local_server function
        # and also add EXACTLY http://localhost:54415/
        # to Authorised redirect URIs in the
        # OAuth 2.0 Client IDs in Google Cloud Platform
        user_external_data_dict = {
            "oauth_state": state,
            "username": self.user_email,
            "system_id": GoogleAccountLocalConstants.GOOGLE_SYSTEM_ID,
            "is_refresh_token_valid": True,
        }

        main_profile_id = self.select_one_value_by_column_and_value(
            schema_name="profile",
            view_table_name="profile_view",
            select_clause_value="profile_id",
            column_value=self.user_email,
            column_name="profile.main_email_address",
        )
        if main_profile_id:
            user_external_data_dict["main_profile_id"] = main_profile_id
        else:
            exception_message = f"Profile ID not found for email {self.user_email}"
            self.logger.error(exception_message)
            raise Exception(exception_message)

        data_dict_compare_user_external = {
            "main_profile_id": main_profile_id,
            "username": self.user_email,
            "system_id": GoogleAccountLocalConstants.GOOGLE_SYSTEM_ID,
            "subsystem_id": GoogleAccountLocalConstants.GOOGLE_CONTACT_SUBSYSTEM_ID,
        }

        user_external_inserted_id = self.upsert(
            schema_name="user_external",
            table_name="user_external_table",
            data_dict=user_external_data_dict,
            data_dict_compare=data_dict_compare_user_external,
        )

        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ')
        print(f'Please go to this URL and authorize the application: {auth_url}', flush=True)  # flash=True is for GHA
        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX ')
        # TODO How can we check if we are in GHA or not?
        # webbrowser.open(auth_url) - doesn't work in GHA

        # TODO user_external_id = UserExternal.insert()
        # TODO "oauth_state": oauth_state

        # If the url is
        # http://localhost:54219/?state=yp8FP2BF7cI9xExjUB70Oyaol0oDNG&code=4/0AdLIrYclkHjKFCb_yJn625Htr8FejaRjFawe7mldEqWINitBz6VD_E0ZOWx0K5d4eocYZg&scope=email%20openid%20https://www.googleapis.com/auth/contacts.readonly%20https://www.googleapis.com/auth/userinfo.email&authuser=0&prompt=consent
        # the auth_code is 4/0AdLIrYclkHjKFCb_yJn625Htr8FejaRjFawe7mldEqWINitBz6VD_E0ZOWx0K5d4eocYZg
        # is found after the code= in the url
        auth_code = None
        # Trying every 5 seconds to get the auth code from the database with a timeout of 50 seconds.
        print(f'Waiting for {TIMEOUT} seconds, for you to choose account {self.user_email} in this URL {auth_url}', flush=True)  # flash=True is for GHA  # noqa
        for i in range(TIMEOUT // SLEEP_TIME):
            # selecting by primary key is faster, so we don't select by state
            auth_code = self.select_one_value_by_column_and_value(
                select_clause_value="access_token",
                column_value=user_external_inserted_id,
            )
            if auth_code:
                self.logger.info(
                    f"Auth code found in the database after {i + 1} times out of {TIMEOUT // SLEEP_TIME}."
                )
                break
            time.sleep(SLEEP_TIME)
            self.logger.info(
                f"Failed to get the auth code from the database for the {i + 1} time out of {TIMEOUT // SLEEP_TIME}."
            )
        if not auth_code:
            # TODO Add the UserContext.username() in the begging of the Exception text
            raise Exception("Auth code not found in the database, you probably didn't choose the Google Account to use in the browser opened.")
        # TODO How can we check that the user choose the expected Google Account or not?
        flow.fetch_token(code=auth_code)
        self.creds = flow.credentials

        token_user_external_data_dict = {
            "user_external_id": user_external_inserted_id,
            "access_token": self.creds.token,
            "refresh_token": self.creds.refresh_token,
            "expiry": self.creds.expiry,
            "oauth_state": state,
        }

        data_dict_compare_token_user_external = {
            "user_external_id": user_external_inserted_id,
            "name": self.user_email,
        }

        token_user_external_inserted_id = self.token__user_external.upsert(
            schema_name="user_external",
            table_name="token__user_external_table",
            data_dict=token_user_external_data_dict,
            data_dict_compare=data_dict_compare_token_user_external,
        )

        self.logger.info(
            f"Token data dict: {token_user_external_data_dict}/n Token user_external inserted ID: {token_user_external_inserted_id}",
            object=token_user_external_data_dict,
        )
        return user_external_inserted_id
        # self.creds = flow.run_local_server(port=self.port)

    def get_email_address(self):
        """
        Get the email address of the authenticated Google account.

        Returns:
            str: The email address of the authenticated Google account,
                 or None if not authenticated.
        """
        return self.user_email
