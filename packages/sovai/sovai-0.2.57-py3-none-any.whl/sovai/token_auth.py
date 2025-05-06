from sovai.api_config import ApiConfig, save_key
from sovai.utils.client_side import verify_token
from sovai.errors.sovai_errors import InvalidCredentialsError


def token_auth(token: str):
    ApiConfig.token = token
    ApiConfig.token_type = "Bearer"
    save_key()
    is_valid, user_id = verify_token(verbose=False)

    if not is_valid:
        # print('invalid')
        raise InvalidCredentialsError("Invalid or expired token. Please authenticate.")

