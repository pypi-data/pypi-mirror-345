"""
Models for the ExcelJet API client.
"""

from typing import Dict, List, Optional, Any, Union, Literal
from enum import Enum
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Enum for the supported content types"""
    ARTICLE = "article"
    CHART = "chart"
    CHART_TYPE = "chart_type"
    COURSE = "course"
    FORMULA = "formula"
    FUNCTION = "function"
    GLOSSARY = "term"
    PAGE = "page"
    PIVOT = "pivot"
    PUZZLE = "puzzle"
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    LESSON = "lesson"


class NodeIDListItem(BaseModel):
    """Schema for items in node ID list"""
    nid: int
    title: str
    content_type: str
    path: str
    changed: int


class NodeIDListResponse(BaseModel):
    """Schema for list of node IDs response"""
    items: List[NodeIDListItem]
    count: int


class NodeResponse(BaseModel):
    """Response schema for getting a specific node"""
    nid: int
    title: str
    type: str
    path: str
    created: int
    changed: int
    status: bool
    model_config = {"extra": "allow"}  # Allow extra fields from backdrop data


class NodeCreatedResponse(BaseModel):
    """Response schema for node creation/update"""
    nid: int
    title: str
    type: str
    path: str
    created: int
    changed: int
    status: bool
    model_config = {"extra": "allow"}  # Allow extra fields from original node data


class BulkNodeCreationResponse(BaseModel):
    """Response schema for bulk node creation"""
    created: int
    node_ids: List[int]


class BulkNodeDeletionResponse(BaseModel):
    """Response schema for bulk node deletion"""
    deleted: int
    node_ids: List[int]
    not_found: List[int]


class BulkNodeUpdateResponse(BaseModel):
    """Response schema for bulk node update"""
    updated: int
    node_ids: List[int]
    not_found: List[int]
    invalid: List[Union[Dict[str, Any], int]]


class AllNodesDeletedResponse(BaseModel):
    """Response schema for deleting all nodes"""
    message: str
    deleted_count: int


class NodeIDList(BaseModel):
    """Schema for list of node IDs for bulk operations"""
    node_ids: List[int]


# Node models for request validation
class BackdropNode(BaseModel):
    """Base schema for all Backdrop node types"""
    nid: int
    title: str
    type: str
    path: str
    created: int
    changed: int
    status: bool
    # Optional fields - these depend on node type but are handled generically
    body: Optional[str] = None
    abstract: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    duration: Optional[str] = None
    video_count: Optional[int] = None
    total_duration: Optional[str] = None
    curriculum: Optional[List[Dict[str, Any]]] = None
    
    model_config = {"extra": "allow"}  # Allow extra fields for flexibility 