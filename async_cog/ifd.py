from pydantic import BaseModel


class IFD(BaseModel):
    offset: int
    n_entries: int
    next_ifd_pointer: int
