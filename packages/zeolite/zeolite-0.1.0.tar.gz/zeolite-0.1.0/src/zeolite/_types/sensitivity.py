from enum import StrEnum


class Sensitivity(StrEnum):
    HIGHLY_SENSITIVE = "1_highly_sensitive"
    CONFIDENTIAL = "2_confidential"
    IDENTIFIABLE = "3_identifiable"
    POTENTIALLY_IDENTIFIABLE = "4_potentially_identifiable"
    LIMITED = "5_limited"
    NON_SENSITIVE = "6_non_sensitive"
    UNKNOWN = "99_unknown"
