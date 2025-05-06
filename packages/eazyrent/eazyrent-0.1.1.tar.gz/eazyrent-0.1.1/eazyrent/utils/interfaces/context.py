from pydantic import BaseModel
from core.v2.models import RentalFile
from products.v1.models import ForRentProduct, ForSalesProduct


class ActionContext(BaseModel):
    obj: ForRentProduct | ForSalesProduct | RentalFile
