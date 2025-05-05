# (C) 2024 Fujitsu Limited

import argparse
import getpass
import logging
import sys
import traceback
from datetime import datetime, timedelta

from botocore.exceptions import ClientError
from pycognito.aws_srp import AWSSRP
from pycognito.exceptions import ForceChangePasswordException, SoftwareTokenMFAChallengeException

from fujitsu_quantum import aws_utils
from fujitsu_quantum.auth import FQCAuthBoto3, FQCAuthError
from fujitsu_quantum.config import Config
from fujitsu_quantum.devices import Devices

# Used to make debugging faster. Input your testing user credentials,
# and when the CLI asks for a username and password, just click Enter.
Username = ""
Password = ""


def main() -> None:
    try:
        parser = argparse.ArgumentParser(description="Fujitsu Quantum CLI")
        parser.add_argument("command", choices=["login", "refresh", "logout", "auth-status", "test"],
                            help="Command to run")
        parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
        options = parser.parse_args()

        if options.debug:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG)
            logging.debug("Set log level to DEBUG")
        else:
            logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

        if options.command == "login":
            original_retry_max_attempts = Config.retry_max_attempts
            try:
                # Some unrecoverable errors may occur (e.g., an SSL verification error when connecting to AWS).
                # To avoid long waiting times in case of such errors, set the retry-max-attempts to a small value.
                Config.retry_max_attempts = 3
                login()
            finally:
                Config.retry_max_attempts = original_retry_max_attempts

        elif options.command == "refresh":
            FQCAuthBoto3().refresh_auth(force=True)
            print("The credential file has been successfully updated.")

        elif options.command == "logout":
            FQCAuthBoto3().logout()
            print("Successfully logged out.")

        elif options.command == 'auth-status':
            try:
                auth = FQCAuthBoto3()
                if auth.refresh_token_expiration_time < datetime.now():
                    print('Credentials are outdated.\n'
                          'Please run `fujitsu-quantum login` to update the credentials.')
                else:
                    print('You have valid credentials.\n'
                          'The credentials will expire at '
                          f'{auth.refresh_token_expiration_time.strftime(FQCAuthBoto3.TIME_FORMAT)}.')
            except FQCAuthError as e:
                print(e.args[0])

        elif options.command == 'test':
            original_retry_max_attempts = Config.retry_max_attempts
            try:
                # Some unrecoverable errors may occur (e.g., SSL verification errors).
                # To avoid long waiting times in case of such errors, set the retry-max-attempts to a small value.
                Config.retry_max_attempts = 3

                # test if sending a request to the backend causes no errors
                Devices.get('SVSim')

                print('All tests passed.')
            finally:
                Config.retry_max_attempts = original_retry_max_attempts

        else:
            print(f"Invalid command: {options.command}")

    except ClientError as exc:
        boto3_error_code = exc.response["Error"]["Code"]
        boto3_error_message = exc.response["Error"]["Message"]
        if boto3_error_code == 'NotAuthorizedException':
            error_message = f'Failed to {options.command}.\n{boto3_error_message}.'
        elif boto3_error_code == 'CodeMismatchException':
            error_message = 'Failed to login.\nThe TOTP code is invalid.'
        else:
            error_message = f'Failed to login.\n{boto3_error_message}. ({boto3_error_code})'

        print(error_message)
    except Exception as exc:
        print(''.join(traceback.format_exception(type(exc), exc, exc.__traceback__)))


def login():
    user = input("Enter username: ") or Username
    while len(user) == 0:
        user = input("Enter username: ") or Username
    password = getpass.getpass("Enter password: ") or Password
    client = aws_utils.get_client("cognito-idp", region_name="ap-northeast-1")
    aws = AWSSRP(
        client=client,
        pool_id=Config.auth_pool_id,
        client_id=Config.auth_sdk_client_id,
        username=user,
        password=password,
    )
    try:
        logging.debug("AWSSRP.authenticate")
        aws.authenticate_user()

    except ForceChangePasswordException:
        print("Your account is in an invalid state. Please contact the support team.", file=sys.stderr)
        raise RuntimeError("Invalid account state.")

    except SoftwareTokenMFAChallengeException as exc:
        logging.debug("pycognito.SoftwareTokenMFAChallengeException")

        device_name = exc.get_tokens()["ChallengeParameters"].get("FRIENDLY_DEVICE_NAME", None)
        if device_name is not None:
            code_prompt = "Enter the 6-digit code generated by your TOTP device ({0}): ".format(device_name)
        else:
            code_prompt = "Enter the 6-digit code generated by your TOTP device): "

        code = input(code_prompt)
        while len(code) == 0:
            code = input(code_prompt)

        current_time = datetime.now()
        tokens = client.respond_to_auth_challenge(
            ClientId=Config.auth_sdk_client_id,
            Session=exc.get_tokens()["Session"],
            ChallengeName=exc.get_tokens()["ChallengeName"],
            ChallengeResponses={
                "USERNAME": user,
                "SOFTWARE_TOKEN_MFA_CODE": code,
            },
        )

        access_token = tokens["AuthenticationResult"]["AccessToken"]
        refresh_token = tokens["AuthenticationResult"]["RefreshToken"]
        access_token_expires_in = tokens["AuthenticationResult"]["ExpiresIn"]
        access_token_expiration_time = current_time + timedelta(seconds=access_token_expires_in)
        refresh_token_expiration_time = current_time + timedelta(days=180)

        if "NewDeviceMetadata" in tokens["AuthenticationResult"]:
            logging.debug("Confirming device...")
            _, _ = aws.confirm_device(tokens=tokens)
            device_key = tokens["AuthenticationResult"]["NewDeviceMetadata"]["DeviceKey"]
        else:
            device_key = None

        print("Authentication succeeded.")

        FQCAuthBoto3.store_credentials(
            client_id=Config.auth_sdk_client_id,
            username=user,
            access_token=access_token,
            access_token_expiration_time=access_token_expiration_time,
            refresh_token=refresh_token,
            refresh_token_expiration_time=refresh_token_expiration_time,
            device_key=device_key,
        )

        print("Successfully logged in.")


if __name__ == "__main__":
    main()
