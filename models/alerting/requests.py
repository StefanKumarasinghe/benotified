"""
Request payload models for alertmanager routes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AlertWebhookRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    alerts: List[Dict[str, Any]] = Field(default_factory=list)


class RuleImportRequest(BaseModel):
    yamlContent: Optional[str] = None
    defaults: Dict[str, Any] = Field(default_factory=dict)
    dryRun: bool = False


class JiraConfigUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    baseUrl: Optional[str] = None
    email: Optional[str] = None
    apiToken: Optional[str] = None
    bearerToken: Optional[str] = None


class JiraIntegrationCreateRequest(BaseModel):
    name: Optional[str] = None
    enabled: bool = True
    visibility: str = "private"
    sharedGroupIds: List[str] = Field(default_factory=list)
    baseUrl: Optional[str] = None
    email: Optional[str] = None
    apiToken: Optional[str] = None
    bearerToken: Optional[str] = None
    authMode: Optional[str] = None
    supportsSso: Optional[bool] = None


class JiraIntegrationUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = None
    enabled: Optional[bool] = None
    visibility: Optional[str] = None
    sharedGroupIds: Optional[List[str]] = None
    baseUrl: Optional[str] = None
    email: Optional[str] = None
    apiToken: Optional[str] = None
    bearerToken: Optional[str] = None
    authMode: Optional[str] = None
    supportsSso: Optional[bool] = None


class IncidentJiraCreateRequest(BaseModel):
    integrationId: str
    projectKey: str
    summary: Optional[str] = None
    description: Optional[str] = None
    issueType: Optional[str] = None


class IncidentJiraCommentRequest(BaseModel):
    text: str
