from pydantic import BaseModel
from eazyrent.core.v2.models import RentalFile
from eazyrent.products.v1.models import ForRentProduct, ForSalesProduct


class ActionContext(BaseModel):
    obj: ForRentProduct | ForSalesProduct | RentalFile
