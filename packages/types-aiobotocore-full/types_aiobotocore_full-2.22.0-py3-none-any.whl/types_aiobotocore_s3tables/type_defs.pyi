"""
Type annotations for s3tables service type definitions.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_s3tables/type_defs/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from types_aiobotocore_s3tables.type_defs import CreateNamespaceRequestTypeDef

    data: CreateNamespaceRequestTypeDef = ...
    ```
"""

from __future__ import annotations

import sys
from datetime import datetime

from .literals import (
    JobStatusType,
    MaintenanceStatusType,
    TableMaintenanceJobTypeType,
    TableMaintenanceTypeType,
    TableTypeType,
)

if sys.version_info >= (3, 9):
    from builtins import dict as Dict
    from builtins import list as List
    from collections.abc import Sequence
else:
    from typing import Dict, List, Sequence
if sys.version_info >= (3, 12):
    from typing import Literal, NotRequired, TypedDict
else:
    from typing_extensions import Literal, NotRequired, TypedDict

__all__ = (
    "CreateNamespaceRequestTypeDef",
    "CreateNamespaceResponseTypeDef",
    "CreateTableBucketRequestTypeDef",
    "CreateTableBucketResponseTypeDef",
    "CreateTableRequestTypeDef",
    "CreateTableResponseTypeDef",
    "DeleteNamespaceRequestTypeDef",
    "DeleteTableBucketPolicyRequestTypeDef",
    "DeleteTableBucketRequestTypeDef",
    "DeleteTablePolicyRequestTypeDef",
    "DeleteTableRequestTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetNamespaceRequestTypeDef",
    "GetNamespaceResponseTypeDef",
    "GetTableBucketMaintenanceConfigurationRequestTypeDef",
    "GetTableBucketMaintenanceConfigurationResponseTypeDef",
    "GetTableBucketPolicyRequestTypeDef",
    "GetTableBucketPolicyResponseTypeDef",
    "GetTableBucketRequestTypeDef",
    "GetTableBucketResponseTypeDef",
    "GetTableMaintenanceConfigurationRequestTypeDef",
    "GetTableMaintenanceConfigurationResponseTypeDef",
    "GetTableMaintenanceJobStatusRequestTypeDef",
    "GetTableMaintenanceJobStatusResponseTypeDef",
    "GetTableMetadataLocationRequestTypeDef",
    "GetTableMetadataLocationResponseTypeDef",
    "GetTablePolicyRequestTypeDef",
    "GetTablePolicyResponseTypeDef",
    "GetTableRequestTypeDef",
    "GetTableResponseTypeDef",
    "IcebergCompactionSettingsTypeDef",
    "IcebergMetadataTypeDef",
    "IcebergSchemaTypeDef",
    "IcebergSnapshotManagementSettingsTypeDef",
    "IcebergUnreferencedFileRemovalSettingsTypeDef",
    "ListNamespacesRequestPaginateTypeDef",
    "ListNamespacesRequestTypeDef",
    "ListNamespacesResponseTypeDef",
    "ListTableBucketsRequestPaginateTypeDef",
    "ListTableBucketsRequestTypeDef",
    "ListTableBucketsResponseTypeDef",
    "ListTablesRequestPaginateTypeDef",
    "ListTablesRequestTypeDef",
    "ListTablesResponseTypeDef",
    "NamespaceSummaryTypeDef",
    "PaginatorConfigTypeDef",
    "PutTableBucketMaintenanceConfigurationRequestTypeDef",
    "PutTableBucketPolicyRequestTypeDef",
    "PutTableMaintenanceConfigurationRequestTypeDef",
    "PutTablePolicyRequestTypeDef",
    "RenameTableRequestTypeDef",
    "ResponseMetadataTypeDef",
    "SchemaFieldTypeDef",
    "TableBucketMaintenanceConfigurationValueTypeDef",
    "TableBucketMaintenanceSettingsTypeDef",
    "TableBucketSummaryTypeDef",
    "TableMaintenanceConfigurationValueTypeDef",
    "TableMaintenanceJobStatusValueTypeDef",
    "TableMaintenanceSettingsTypeDef",
    "TableMetadataTypeDef",
    "TableSummaryTypeDef",
    "UpdateTableMetadataLocationRequestTypeDef",
    "UpdateTableMetadataLocationResponseTypeDef",
)

class CreateNamespaceRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: Sequence[str]

class ResponseMetadataTypeDef(TypedDict):
    RequestId: str
    HTTPStatusCode: int
    HTTPHeaders: Dict[str, str]
    RetryAttempts: int
    HostId: NotRequired[str]

class CreateTableBucketRequestTypeDef(TypedDict):
    name: str

class DeleteNamespaceRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str

class DeleteTableBucketPolicyRequestTypeDef(TypedDict):
    tableBucketARN: str

class DeleteTableBucketRequestTypeDef(TypedDict):
    tableBucketARN: str

class DeleteTablePolicyRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str
    name: str

class DeleteTableRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str
    name: str
    versionToken: NotRequired[str]

class GetNamespaceRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str

class GetTableBucketMaintenanceConfigurationRequestTypeDef(TypedDict):
    tableBucketARN: str

class GetTableBucketPolicyRequestTypeDef(TypedDict):
    tableBucketARN: str

class GetTableBucketRequestTypeDef(TypedDict):
    tableBucketARN: str

class GetTableMaintenanceConfigurationRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str
    name: str

class GetTableMaintenanceJobStatusRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str
    name: str

class TableMaintenanceJobStatusValueTypeDef(TypedDict):
    status: JobStatusType
    lastRunTimestamp: NotRequired[datetime]
    failureMessage: NotRequired[str]

class GetTableMetadataLocationRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str
    name: str

class GetTablePolicyRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str
    name: str

class GetTableRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str
    name: str

class IcebergCompactionSettingsTypeDef(TypedDict):
    targetFileSizeMB: NotRequired[int]

SchemaFieldTypeDef = TypedDict(
    "SchemaFieldTypeDef",
    {
        "name": str,
        "type": str,
        "required": NotRequired[bool],
    },
)

class IcebergSnapshotManagementSettingsTypeDef(TypedDict):
    minSnapshotsToKeep: NotRequired[int]
    maxSnapshotAgeHours: NotRequired[int]

class IcebergUnreferencedFileRemovalSettingsTypeDef(TypedDict):
    unreferencedDays: NotRequired[int]
    nonCurrentDays: NotRequired[int]

class PaginatorConfigTypeDef(TypedDict):
    MaxItems: NotRequired[int]
    PageSize: NotRequired[int]
    StartingToken: NotRequired[str]

class ListNamespacesRequestTypeDef(TypedDict):
    tableBucketARN: str
    prefix: NotRequired[str]
    continuationToken: NotRequired[str]
    maxNamespaces: NotRequired[int]

class NamespaceSummaryTypeDef(TypedDict):
    namespace: List[str]
    createdAt: datetime
    createdBy: str
    ownerAccountId: str

class ListTableBucketsRequestTypeDef(TypedDict):
    prefix: NotRequired[str]
    continuationToken: NotRequired[str]
    maxBuckets: NotRequired[int]

class TableBucketSummaryTypeDef(TypedDict):
    arn: str
    name: str
    ownerAccountId: str
    createdAt: datetime

class ListTablesRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: NotRequired[str]
    prefix: NotRequired[str]
    continuationToken: NotRequired[str]
    maxTables: NotRequired[int]

TableSummaryTypeDef = TypedDict(
    "TableSummaryTypeDef",
    {
        "namespace": List[str],
        "name": str,
        "type": TableTypeType,
        "tableARN": str,
        "createdAt": datetime,
        "modifiedAt": datetime,
    },
)

class PutTableBucketPolicyRequestTypeDef(TypedDict):
    tableBucketARN: str
    resourcePolicy: str

class PutTablePolicyRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str
    name: str
    resourcePolicy: str

class RenameTableRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str
    name: str
    newNamespaceName: NotRequired[str]
    newName: NotRequired[str]
    versionToken: NotRequired[str]

class UpdateTableMetadataLocationRequestTypeDef(TypedDict):
    tableBucketARN: str
    namespace: str
    name: str
    versionToken: str
    metadataLocation: str

class CreateNamespaceResponseTypeDef(TypedDict):
    tableBucketARN: str
    namespace: List[str]
    ResponseMetadata: ResponseMetadataTypeDef

class CreateTableBucketResponseTypeDef(TypedDict):
    arn: str
    ResponseMetadata: ResponseMetadataTypeDef

class CreateTableResponseTypeDef(TypedDict):
    tableARN: str
    versionToken: str
    ResponseMetadata: ResponseMetadataTypeDef

class EmptyResponseMetadataTypeDef(TypedDict):
    ResponseMetadata: ResponseMetadataTypeDef

class GetNamespaceResponseTypeDef(TypedDict):
    namespace: List[str]
    createdAt: datetime
    createdBy: str
    ownerAccountId: str
    ResponseMetadata: ResponseMetadataTypeDef

class GetTableBucketPolicyResponseTypeDef(TypedDict):
    resourcePolicy: str
    ResponseMetadata: ResponseMetadataTypeDef

class GetTableBucketResponseTypeDef(TypedDict):
    arn: str
    name: str
    ownerAccountId: str
    createdAt: datetime
    ResponseMetadata: ResponseMetadataTypeDef

class GetTableMetadataLocationResponseTypeDef(TypedDict):
    versionToken: str
    metadataLocation: str
    warehouseLocation: str
    ResponseMetadata: ResponseMetadataTypeDef

class GetTablePolicyResponseTypeDef(TypedDict):
    resourcePolicy: str
    ResponseMetadata: ResponseMetadataTypeDef

GetTableResponseTypeDef = TypedDict(
    "GetTableResponseTypeDef",
    {
        "name": str,
        "type": TableTypeType,
        "tableARN": str,
        "namespace": List[str],
        "versionToken": str,
        "metadataLocation": str,
        "warehouseLocation": str,
        "createdAt": datetime,
        "createdBy": str,
        "managedByService": str,
        "modifiedAt": datetime,
        "modifiedBy": str,
        "ownerAccountId": str,
        "format": Literal["ICEBERG"],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

class UpdateTableMetadataLocationResponseTypeDef(TypedDict):
    name: str
    tableARN: str
    namespace: List[str]
    versionToken: str
    metadataLocation: str
    ResponseMetadata: ResponseMetadataTypeDef

class GetTableMaintenanceJobStatusResponseTypeDef(TypedDict):
    tableARN: str
    status: Dict[TableMaintenanceJobTypeType, TableMaintenanceJobStatusValueTypeDef]
    ResponseMetadata: ResponseMetadataTypeDef

class IcebergSchemaTypeDef(TypedDict):
    fields: Sequence[SchemaFieldTypeDef]

class TableMaintenanceSettingsTypeDef(TypedDict):
    icebergCompaction: NotRequired[IcebergCompactionSettingsTypeDef]
    icebergSnapshotManagement: NotRequired[IcebergSnapshotManagementSettingsTypeDef]

class TableBucketMaintenanceSettingsTypeDef(TypedDict):
    icebergUnreferencedFileRemoval: NotRequired[IcebergUnreferencedFileRemovalSettingsTypeDef]

class ListNamespacesRequestPaginateTypeDef(TypedDict):
    tableBucketARN: str
    prefix: NotRequired[str]
    PaginationConfig: NotRequired[PaginatorConfigTypeDef]

class ListTableBucketsRequestPaginateTypeDef(TypedDict):
    prefix: NotRequired[str]
    PaginationConfig: NotRequired[PaginatorConfigTypeDef]

class ListTablesRequestPaginateTypeDef(TypedDict):
    tableBucketARN: str
    namespace: NotRequired[str]
    prefix: NotRequired[str]
    PaginationConfig: NotRequired[PaginatorConfigTypeDef]

class ListNamespacesResponseTypeDef(TypedDict):
    namespaces: List[NamespaceSummaryTypeDef]
    continuationToken: str
    ResponseMetadata: ResponseMetadataTypeDef

class ListTableBucketsResponseTypeDef(TypedDict):
    tableBuckets: List[TableBucketSummaryTypeDef]
    continuationToken: str
    ResponseMetadata: ResponseMetadataTypeDef

class ListTablesResponseTypeDef(TypedDict):
    tables: List[TableSummaryTypeDef]
    continuationToken: str
    ResponseMetadata: ResponseMetadataTypeDef

class IcebergMetadataTypeDef(TypedDict):
    schema: IcebergSchemaTypeDef

class TableMaintenanceConfigurationValueTypeDef(TypedDict):
    status: NotRequired[MaintenanceStatusType]
    settings: NotRequired[TableMaintenanceSettingsTypeDef]

class TableBucketMaintenanceConfigurationValueTypeDef(TypedDict):
    status: NotRequired[MaintenanceStatusType]
    settings: NotRequired[TableBucketMaintenanceSettingsTypeDef]

class TableMetadataTypeDef(TypedDict):
    iceberg: NotRequired[IcebergMetadataTypeDef]

class GetTableMaintenanceConfigurationResponseTypeDef(TypedDict):
    tableARN: str
    configuration: Dict[TableMaintenanceTypeType, TableMaintenanceConfigurationValueTypeDef]
    ResponseMetadata: ResponseMetadataTypeDef

PutTableMaintenanceConfigurationRequestTypeDef = TypedDict(
    "PutTableMaintenanceConfigurationRequestTypeDef",
    {
        "tableBucketARN": str,
        "namespace": str,
        "name": str,
        "type": TableMaintenanceTypeType,
        "value": TableMaintenanceConfigurationValueTypeDef,
    },
)

class GetTableBucketMaintenanceConfigurationResponseTypeDef(TypedDict):
    tableBucketARN: str
    configuration: Dict[
        Literal["icebergUnreferencedFileRemoval"], TableBucketMaintenanceConfigurationValueTypeDef
    ]
    ResponseMetadata: ResponseMetadataTypeDef

PutTableBucketMaintenanceConfigurationRequestTypeDef = TypedDict(
    "PutTableBucketMaintenanceConfigurationRequestTypeDef",
    {
        "tableBucketARN": str,
        "type": Literal["icebergUnreferencedFileRemoval"],
        "value": TableBucketMaintenanceConfigurationValueTypeDef,
    },
)
CreateTableRequestTypeDef = TypedDict(
    "CreateTableRequestTypeDef",
    {
        "tableBucketARN": str,
        "namespace": str,
        "name": str,
        "format": Literal["ICEBERG"],
        "metadata": NotRequired[TableMetadataTypeDef],
    },
)
