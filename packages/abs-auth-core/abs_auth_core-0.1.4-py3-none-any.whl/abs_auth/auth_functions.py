from datetime import datetime, UTC
from typing import Callable, Any

from abs_exception_core.exceptions import NotFoundError, ValidationError
class AuthFunctions:
    def  __init__(self, db_session: Callable[...,Any], User:any):
        """
        Args:
            db_session (Callable[..., Session]): A function that returns a SQLAlchemy session.
            User (any): The SQLAlchemy model class representing the user table
        """
        self.db = db_session
        self.User = User

    def get_user_by_attribute(self,attribute: str, value: str):
        """
        Get a user by an attribute.

        Args:
            attribute (str): The attribute to get the user by.
            value (str): The value of the attribute.
        
        Returns:
            User: The user object if found, otherwise None.
        """
        with self.db() as session:
            try:
                if not hasattr(self.User, attribute):
                    raise ValidationError(detail=f"Attribute {attribute} does not exist on the User model")
                
                user = session.query(self.User).filter(getattr(self.User, attribute) == value).first()

                if not user:
                    raise NotFoundError(detail="User not found")
                
                return user
            
            except Exception as e:
                raise e
