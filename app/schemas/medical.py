from app.models.medical import MedicalReport
from typing import List 


class MedicalReportPaginate:
    reports : List[MedicalReport]
    total: int = 0
    page: int = 1
    limit: int = 10