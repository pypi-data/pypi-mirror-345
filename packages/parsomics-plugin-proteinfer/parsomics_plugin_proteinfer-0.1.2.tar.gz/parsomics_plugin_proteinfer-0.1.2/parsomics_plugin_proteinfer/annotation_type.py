from enum import Enum


class ProteinferAnnotationType(str, Enum):
    EC_NUMBER = "EC_NUMBER"
    PFAM = "PFAM"
