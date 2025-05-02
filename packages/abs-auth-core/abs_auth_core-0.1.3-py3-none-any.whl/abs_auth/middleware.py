from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from typing import Callable, Any

from .jwt_functions import JWTFunctions
from .auth_functions import AuthFunctions
from abs_exception_core.exceptions import UnauthorizedError

security = HTTPBearer()
logger = logging.getLogger(__name__)


# Dependency acting like per-route middleware
def auth_middleware(
    db_session: Callable[...,Any],
    Users:any,
    jwt_secret_key:str,
    jwt_algorithm:str
):
    """
    This middleware is used for authentication of the user.
    Args:
        db_session: Callable[...,Any]: Session of the SQLAlchemy database engine
        Users: User table fo teh system
        jwt_secret_key: Secret key of the JWT for jwt functions
        jwt_algorithm: Algorithm used for JWT

    Returns:
    """
    def get_auth(token: HTTPAuthorizationCredentials = Depends(security)):
        jwt_functions = JWTFunctions(secret_key=jwt_secret_key,algorithm=jwt_algorithm)
        try:
            if not token or not token.credentials:
                raise UnauthorizedError(detail="Invalid authentication credentials")

            payload = jwt_functions.get_data(token=token.credentials)
            uuid = payload.get("uuid")
            auth_functions = AuthFunctions(db_session,Users)

            user = auth_functions.get_user_by_attribute(attribute="uuid", value=uuid)
            
            if not user:
                logger.error(f"Authentication failed: User with id {uuid} not found")
                raise UnauthorizedError(detail="Authentication failed")

            return user  # Attach user for use in route

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            raise UnauthorizedError(detail="Authentication failed")
    return get_auth