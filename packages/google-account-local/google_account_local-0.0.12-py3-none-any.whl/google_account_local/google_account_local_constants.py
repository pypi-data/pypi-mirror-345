from logger_local.LoggerComponentEnum import LoggerComponentEnum
from python_sdk_remote.utilities import our_get_env  # noqa: E402


GOOGLE_USER_EXTERNAL_USERNAME = our_get_env("GOOGLE_USER_EXTERNAL_USERNAME", raise_if_empty=True)


class GoogleAccountLocalConstants:
    class LoggerSetupConstants:
        GOOGLE_ACCOUNT_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 291
        GOOGLE_ACCOUNT_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = "google-account-local"
        DEVELOPER_EMAIL = GOOGLE_USER_EXTERNAL_USERNAME
        # TODO all LOGGER_OBJECTs should be camerCase
        # TODO Update the logger_local itself package to accept camelCase

        GOOGLE_ACCOUNT_LOCAL_CODE_LOGGER_OBJECT = {
            "component_id": GOOGLE_ACCOUNT_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
            "component_name": GOOGLE_ACCOUNT_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
            "component_category": LoggerComponentEnum.ComponentCategory.Code.value,
            "developer_email": DEVELOPER_EMAIL,
        }
        GOOGLE_ACCOUNT_LOCAL_PYTHON_PACKAGE_TEST_LOGGER_OBJECT = {
            "component_id": GOOGLE_ACCOUNT_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
            "component_name": GOOGLE_ACCOUNT_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
            "component_category": LoggerComponentEnum.ComponentCategory.Unit_Test.value,
            "testing_framework": LoggerComponentEnum.testingFramework.pytest.value,
            "developer_email": DEVELOPER_EMAIL,
        }

    GOOGLE_SYSTEM_ID = 6
    GOOGLE_CONTACT_SUBSYSTEM_ID = 6
