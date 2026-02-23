"""
Access control utilities for checking user permissions and resolving group memberships for tenant-based resources, including functions to determine if a user is a tenant admin, resolve group objects from group IDs with optional membership enforcement, assign shared groups to database objects based on visibility settings, and check if a user has access to a resource based on its visibility and shared group memberships.

Copyright (c) 2026 Stefan Kumarasinghe

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
"""

import logging
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from db_models import Group, User

logger = logging.getLogger(__name__)


def _is_tenant_admin(db: Session, tenant_id: str, user_id: Optional[str]) -> bool:
    if not user_id:
        return False
    user = db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()
    return bool(user and (getattr(user, "is_superuser", False) or str(getattr(user, "role", "")).lower() == "admin"))


def _resolve_groups(
    db: Session,
    tenant_id: str,
    group_ids: List[str],
    *,
    actor_user_id: Optional[str] = None,
    actor_group_ids: Optional[List[str]] = None,
    enforce_membership: bool = True,
) -> List[Group]:
    normalized = [s for gid in (group_ids or []) if gid is not None and (s := str(gid).strip())]
    if not normalized:
        return []

    groups = db.query(Group).filter(Group.tenant_id == tenant_id, Group.id.in_(normalized)).all()
    present_by_id = {g.id: g for g in groups}
    missing_ids = [gid for gid in normalized if gid not in present_by_id]
    for gid in missing_ids:
        db.execute(
            pg_insert(Group)
            .values(
                id=gid,
                tenant_id=tenant_id,
                name=(f"group-{gid}"[:100] or gid[:100]),
                description="Shadow group from main-server context",
                is_active=True,
            )
            .on_conflict_do_nothing(index_elements=[Group.id])
        )
    if missing_ids:
        groups = db.query(Group).filter(Group.tenant_id == tenant_id, Group.id.in_(normalized)).all()
        present_by_id = {g.id: g for g in groups}
    groups = [present_by_id[gid] for gid in normalized if gid in present_by_id]

    if enforce_membership and not _is_tenant_admin(db, tenant_id, actor_user_id):
        actor_groups = set(actor_group_ids or [])
        unauthorized = [gid for gid in normalized if gid not in actor_groups]
        if unauthorized:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a member of one or more specified groups")

    return groups


def _assign_shared_groups(
    db_obj,
    db: Session,
    tenant_id: str,
    visibility: str,
    group_ids: Optional[List[str]],
    *,
    actor_user_id: str,
    actor_group_ids: Optional[List[str]],
):
    if visibility != "group":
        db_obj.shared_groups = []
        return
    if group_ids is None:
        raise ValueError("group_ids is required when visibility is 'group'")
    db_obj.shared_groups = _resolve_groups(
        db, tenant_id, group_ids,
        actor_user_id=actor_user_id,
        actor_group_ids=actor_group_ids,
    )


def _has_access(
    visibility: str,
    created_by: Optional[str],
    user_id: str,
    shared_group_ids: List[str],
    user_group_ids: List[str],
    require_write: bool = False,
) -> bool:
    if created_by == user_id:
        return True
    if require_write:
        return False
    if visibility in ("public", "tenant"):
        return True
    if visibility == "group":
        return bool(set(shared_group_ids) & set(user_group_ids))
    if visibility == "private":
        return False
    logger.warning("Unknown visibility value %r encountered in access check", visibility)
    return False
