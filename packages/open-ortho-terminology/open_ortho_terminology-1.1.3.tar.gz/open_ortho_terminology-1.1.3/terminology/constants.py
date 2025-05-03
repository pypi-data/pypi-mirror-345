# Base UID for all OIDs in this project
BASE_UID = "1.3.6.1.4.1.61741.11.3"

# Code Systems (1.3.6.1.4.1.61741.11.3.2.*)
CS_BASE_UID = f"{BASE_UID}.2"

# Code System UIDs
CS_EXTRAORAL_2D_PHOTOGRAPHIC_SCHEDULED_PROTOCOL_UID = f"{CS_BASE_UID}.1"
CS_EXTRAORAL_3D_VISIBLE_LIGHT_SCHEDULED_PROTOCOL_UID = f"{CS_BASE_UID}.2"
CS_INTRAORAL_2D_PHOTOGRAPHIC_SCHEDULED_PROTOCOL_UID = f"{CS_BASE_UID}.3"
CS_INTRAORAL_3D_VISIBLE_LIGHT_SCHEDULED_PROTOCOL_UID = f"{CS_BASE_UID}.4"

# Code System short name to UID mapping
CODE_SYSTEM_UIDS = {
    "extraoral-2d-photographic-scheduled-protocol": CS_EXTRAORAL_2D_PHOTOGRAPHIC_SCHEDULED_PROTOCOL_UID,
    "extraoral-3d-visible-light-scheduled-protocol": CS_EXTRAORAL_3D_VISIBLE_LIGHT_SCHEDULED_PROTOCOL_UID,
    "intraoral-2d-photographic-scheduled-protocol": CS_INTRAORAL_2D_PHOTOGRAPHIC_SCHEDULED_PROTOCOL_UID,
    "intraoral-3d-visible-light-scheduled-protocol": CS_INTRAORAL_3D_VISIBLE_LIGHT_SCHEDULED_PROTOCOL_UID,
}

# Naming Systems (1.3.6.1.4.1.61741.11.3.1.*)
NS_BASE_UID = f"{BASE_UID}.1"
NS_OPEN_ORTHO_UID = f"{NS_BASE_UID}.1"
NS_MEDOCO_HEALTH_UID = f"{NS_BASE_UID}.2"
NS_DENTAL_EYE_PAD_UID = f"{NS_BASE_UID}.3"

# Value Sets (1.3.6.1.4.1.61741.11.3.3.*)
VS_BASE_UID = f"{BASE_UID}.3"
VS_SCHEDULED_PROTOCOL_UID = f"{VS_BASE_UID}.1"

# Naming System short name to UID mapping
NAMING_SYSTEM_UIDS = {
    "open-ortho": NS_OPEN_ORTHO_UID,
    "medoco-health": NS_MEDOCO_HEALTH_UID, # these shouldn't be here, they are not in our domain.
    "dental-eye-pad": NS_DENTAL_EYE_PAD_UID # these shouldn't be here, they are not in our domain.
}

# Value Set short name to UID mapping
VALUE_SET_UIDS = {
    "scheduled-protocol": VS_SCHEDULED_PROTOCOL_UID
}
