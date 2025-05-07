import logging
from collections.abc import Callable
from datetime import timedelta
from typing import Any, TypeVar, cast, override

from minio import Minio
from minio.error import S3Error

from archipy.adapters.minio.ports import MinioBucketType, MinioObjectType, MinioPolicyType, MinioPort
from archipy.configs.base_config import BaseConfig
from archipy.configs.config_template import MinioConfig
from archipy.helpers.decorators.cache import ttl_cache_decorator
from archipy.models.errors import (
    AlreadyExistsError,
    InternalError,
    InvalidArgumentError,
    NotFoundError,
    PermissionDeniedError,
)

# Type variables for decorators
T = TypeVar("T")  # Return type
F = TypeVar("F", bound=Callable[..., Any])  # Function type

logger = logging.getLogger(__name__)


class MinioAdapter(MinioPort):
    """Concrete implementation of the MinioPort interface using the minio library."""

    def __init__(self, minio_configs: MinioConfig | None = None) -> None:
        """Initialize MinioAdapter with configuration.

        Args:
            minio_configs: Optional MinIO configuration. If None, global config is used.
        """
        # Determine config source (explicit or from global config)
        if minio_configs is not None:
            self.configs = minio_configs
        else:
            # First get global config, then extract MINIO config
            global_config: Any = BaseConfig.global_config()
            if not hasattr(global_config, "MINIO"):
                raise InvalidArgumentError(argument_name="MINIO")
            self.configs = cast(MinioConfig, global_config.MINIO)

        # Ensure we have a valid endpoint value
        endpoint = str(self.configs.ENDPOINT or "")
        if not endpoint:
            raise InvalidArgumentError(argument_name="endpoint")

        self._adapter = Minio(
            endpoint,
            access_key=self.configs.ACCESS_KEY,
            secret_key=self.configs.SECRET_KEY,
            session_token=self.configs.SESSION_TOKEN,
            secure=self.configs.SECURE,
            region=self.configs.REGION,
        )

    def clear_all_caches(self) -> None:
        """Clear all cached values."""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "clear_cache"):
                attr.clear_cache()

    @override
    @ttl_cache_decorator(ttl_seconds=300, maxsize=100)  # Cache for 5 minutes
    def bucket_exists(self, bucket_name: str) -> bool:
        """Check if a bucket exists."""
        try:
            if not bucket_name:
                raise InvalidArgumentError(argument_name="bucket_name")
            return self._adapter.bucket_exists(bucket_name)
        except S3Error as e:
            if "NoSuchBucket" in str(e):
                return False
            raise InternalError(details=f"Failed to check bucket existence: {e}") from e

    @override
    def make_bucket(self, bucket_name: str) -> None:
        """Create a new bucket."""
        try:
            if not bucket_name:
                raise InvalidArgumentError(argument_name="bucket_name")
            self._adapter.make_bucket(bucket_name)
            self.clear_all_caches()  # Clear cache since bucket list changed
        except S3Error as e:
            if "BucketAlreadyOwnedByYou" in str(e) or "BucketAlreadyExists" in str(e):
                raise AlreadyExistsError(resource_type="bucket") from e
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(additional_data={"details": "Permission denied to create bucket"}) from e
            raise InternalError(details=f"Failed to create bucket: {e}") from e

    @override
    def remove_bucket(self, bucket_name: str) -> None:
        """Remove a bucket."""
        try:
            if not bucket_name:
                raise InvalidArgumentError(argument_name="bucket_name")
            self._adapter.remove_bucket(bucket_name)
            self.clear_all_caches()  # Clear cache since bucket list changed
        except S3Error as e:
            if "NoSuchBucket" in str(e):
                raise NotFoundError(resource_type="bucket") from e
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(additional_data={"details": "Permission denied to remove bucket"}) from e
            raise InternalError(details=f"Failed to remove bucket: {e}") from e

    @override
    @ttl_cache_decorator(ttl_seconds=300, maxsize=1)  # Cache for 5 minutes
    def list_buckets(self) -> list[MinioBucketType]:
        """List all buckets."""
        try:
            buckets = self._adapter.list_buckets()
            return [{"name": b.name, "creation_date": b.creation_date} for b in buckets]
        except S3Error as e:
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(additional_data={"details": "Permission denied to list buckets"}) from e
            raise InternalError(details=f"Failed to list buckets: {e}") from e

    @override
    def put_object(self, bucket_name: str, object_name: str, file_path: str) -> None:
        """Upload a file to a bucket."""
        try:
            if not bucket_name or not object_name or not file_path:
                raise InvalidArgumentError(
                    argument_name=(
                        "bucket_name, object_name or file_path"
                        if not all([bucket_name, object_name, file_path])
                        else "bucket_name" if not bucket_name else "object_name" if not object_name else "file_path"
                    ),
                )
            self._adapter.fput_object(bucket_name, object_name, file_path)
            if hasattr(self.list_objects, "clear_cache"):
                self.list_objects.clear_cache()  # Clear object list cache
        except S3Error as e:
            if "NoSuchBucket" in str(e):
                raise NotFoundError(resource_type="bucket") from e
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(additional_data={"details": "Permission denied to upload object"}) from e
            raise InternalError(details=f"Failed to upload object: {e}") from e

    @override
    def get_object(self, bucket_name: str, object_name: str, file_path: str) -> None:
        """Download an object to a file."""
        try:
            if not bucket_name or not object_name or not file_path:
                raise InvalidArgumentError(
                    argument_name=(
                        "bucket_name, object_name or file_path"
                        if not all([bucket_name, object_name, file_path])
                        else "bucket_name" if not bucket_name else "object_name" if not object_name else "file_path"
                    ),
                )
            self._adapter.fget_object(bucket_name, object_name, file_path)
        except S3Error as e:
            if "NoSuchBucket" in str(e) or "NoSuchKey" in str(e):
                raise NotFoundError(resource_type="object") from e
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(additional_data={"details": "Permission denied to download object"}) from e
            raise InternalError(details=f"Failed to download object: {e}") from e

    @override
    def remove_object(self, bucket_name: str, object_name: str) -> None:
        """Remove an object from a bucket."""
        try:
            if not bucket_name or not object_name:
                raise InvalidArgumentError(
                    argument_name=(
                        "bucket_name or object_name"
                        if not all([bucket_name, object_name])
                        else "bucket_name" if not bucket_name else "object_name"
                    ),
                )
            self._adapter.remove_object(bucket_name, object_name)
            if hasattr(self.list_objects, "clear_cache"):
                self.list_objects.clear_cache()  # Clear object list cache
        except S3Error as e:
            if "NoSuchBucket" in str(e) or "NoSuchKey" in str(e):
                raise NotFoundError(resource_type="object") from e
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(additional_data={"details": "Permission denied to remove object"}) from e
            raise InternalError(details=f"Failed to remove object: {e}") from e

    @override
    @ttl_cache_decorator(ttl_seconds=300, maxsize=100)  # Cache for 5 minutes
    def list_objects(
        self,
        bucket_name: str,
        prefix: str = "",
        *,
        recursive: bool = False,
    ) -> list[MinioObjectType]:
        """List objects in a bucket."""
        try:
            if not bucket_name:
                raise InvalidArgumentError(argument_name="bucket_name")
            objects = self._adapter.list_objects(bucket_name, prefix=prefix, recursive=recursive)
            return [
                {"object_name": obj.object_name, "size": obj.size, "last_modified": obj.last_modified}
                for obj in objects
            ]
        except S3Error as e:
            if "NoSuchBucket" in str(e):
                raise NotFoundError(resource_type="bucket") from e
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(additional_data={"details": "Permission denied to list objects"}) from e
            raise InternalError(details=f"Failed to list objects: {e}") from e

    @override
    @ttl_cache_decorator(ttl_seconds=300, maxsize=100)  # Cache for 5 minutes
    def stat_object(self, bucket_name: str, object_name: str) -> MinioObjectType:
        """Get object metadata."""
        try:
            if not bucket_name or not object_name:
                raise InvalidArgumentError(
                    argument_name=(
                        "bucket_name or object_name"
                        if not all([bucket_name, object_name])
                        else "bucket_name" if not bucket_name else "object_name"
                    ),
                )
            obj = self._adapter.stat_object(bucket_name, object_name)
        except S3Error as e:
            if "NoSuchBucket" in str(e) or "NoSuchKey" in str(e):
                raise NotFoundError(resource_type="object") from e
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(additional_data={"details": "Permission denied to get object stats"}) from e
            raise InternalError(details=f"Failed to get object stats: {e}") from e
        else:
            return {
                "object_name": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified,
                "content_type": obj.content_type,
                "etag": obj.etag,
            }

    @override
    def presigned_get_object(self, bucket_name: str, object_name: str, expires: int = 3600) -> str:
        """Generate a presigned URL for downloading an object."""
        try:
            if not bucket_name or not object_name:
                raise InvalidArgumentError(
                    argument_name=(
                        "bucket_name or object_name"
                        if not all([bucket_name, object_name])
                        else "bucket_name" if not bucket_name else "object_name"
                    ),
                )
            return self._adapter.presigned_get_object(bucket_name, object_name, expires=timedelta(seconds=expires))
        except S3Error as e:
            if "NoSuchBucket" in str(e) or "NoSuchKey" in str(e):
                raise NotFoundError(resource_type="object") from e
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(
                    additional_data={"details": "Permission denied to generate presigned URL"},
                ) from e
            raise InternalError(details=f"Failed to generate presigned GET URL: {e}") from e

    @override
    def presigned_put_object(self, bucket_name: str, object_name: str, expires: int = 3600) -> str:
        """Generate a presigned URL for uploading an object."""
        try:
            if not bucket_name or not object_name:
                raise InvalidArgumentError(
                    argument_name=(
                        "bucket_name or object_name"
                        if not all([bucket_name, object_name])
                        else "bucket_name" if not bucket_name else "object_name"
                    ),
                )
            return self._adapter.presigned_put_object(bucket_name, object_name, expires=timedelta(seconds=expires))
        except S3Error as e:
            if "NoSuchBucket" in str(e):
                raise NotFoundError(resource_type="bucket") from e
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(
                    additional_data={"details": "Permission denied to generate presigned PUT URL"},
                ) from e
            raise InternalError(details=f"Failed to generate presigned PUT URL: {e}") from e

    @override
    def set_bucket_policy(self, bucket_name: str, policy: str) -> None:
        """Set bucket policy."""
        try:
            if not bucket_name or not policy:
                raise InvalidArgumentError(
                    argument_name=(
                        "bucket_name or policy"
                        if not all([bucket_name, policy])
                        else "bucket_name" if not bucket_name else "policy"
                    ),
                )
            self._adapter.set_bucket_policy(bucket_name, policy)
        except S3Error as e:
            if "NoSuchBucket" in str(e):
                raise NotFoundError(resource_type="bucket") from e
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(
                    additional_data={"details": "Permission denied to set bucket policy"},
                ) from e
            raise InternalError(details=f"Failed to set bucket policy: {e}") from e

    @override
    @ttl_cache_decorator(ttl_seconds=300, maxsize=100)  # Cache for 5 minutes
    def get_bucket_policy(self, bucket_name: str) -> MinioPolicyType:
        """Get bucket policy."""
        try:
            if not bucket_name:
                raise InvalidArgumentError(argument_name="bucket_name")
            policy = self._adapter.get_bucket_policy(bucket_name)
        except S3Error as e:
            if "NoSuchBucket" in str(e):
                raise NotFoundError(resource_type="bucket") from e
            if "AccessDenied" in str(e):
                raise PermissionDeniedError(
                    additional_data={"details": "Permission denied to get bucket policy"},
                ) from e
            raise InternalError(details=f"Failed to get bucket policy: {e}") from e
        else:
            return {"policy": policy}
