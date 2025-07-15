from pydantic import BaseModel
from typing import Optional, Union, Dict, Any
from app.models.portfolio_models import OptimizedPortfolio

class UserDataBase(BaseModel):
    user_id: str # This was user-name in Dash
    investment_goals: Optional[str] = ""
    amount: Optional[float] = 0 # This was current-savings
    income: Optional[float] = 0 # This was annual-income

class UserDataCreate(UserDataBase):
    pass

class UserData(UserDataBase):
    custom_portfolio: Optional[Union[OptimizedPortfolio, Dict[str, Any]]] = None

    model_config = {
        "from_attributes": True
    }

class ClientInfo(BaseModel):
    user_id: str
    amount: Optional[float] = 0
    income: Optional[float] = 0 