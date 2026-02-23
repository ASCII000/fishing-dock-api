"""
API for supa base integration
"""

from datetime import datetime

import httpx
import uuid

from ..interfaces import IBlobStorage
from ..exceptions import BlobStorageException
from ..schemas import FileSchema


class SupabaseStorage(IBlobStorage):
    """
    Constructor for supabase
    """

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        supabase_storage_name: str,
    ):
        """
        Args:
            supabase_url: str
            supabase_key: str
            supabase_storage_name: str
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_storage_name = supabase_storage_name

    async def delete_archive(self, file_id: str) -> None:
        """
        Delete archive
        """
        await self._request("DELETE", f"/storage/v1/object/{self.supabase_storage_name}/{file_id}")

    async def upload_archive(self, file_name, file_extension, file_content) -> FileSchema:
        """
        Upload archive
        """

        file_name = f"{uuid.uuid4()}.{file_extension}"
        await self._request(
            "POST",
            f"/storage/v1/object/{self.supabase_storage_name}/{file_name}",
            content=file_content,
            headers={
                "Content-Type": self.get_content_type(file_extension),
                "x-upsert": "true",
            }
        )

        return FileSchema(
            id=file_name,
            created_at=datetime.now(),
            link=self.get_public_url(file_name),
            name=file_name,
        )

    def get_public_url(self, file_name) -> str:
        """
        Get public url
        """
        return (
            f"{self.supabase_url}/storage/v1/object/public/"
            f"{self.supabase_storage_name}/{file_name}"
        )

    def get_content_type(self, extension: str) -> str:
        """
        Get content type
        """
        types = {
            "zip": "application/zip",
            "webp": "image/webp",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "pdf": "application/pdf",
            "json": "application/json",
        }

        return types.get(extension.lower(), "application/octet-stream")

    async def _request(self, method, path, **kwargs):
        """
        Request Supabase API
        """

        headers = {
            "Authorization": f"Bearer {self.supabase_key}"
        }

        # Append headers if exists
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))


        async with httpx.AsyncClient(
            base_url=self.supabase_url,
            headers=headers,
        ) as client:

            response = await client.request(
                method=method,
                url=path,
                **kwargs
            )

            try:
                response.raise_for_status()
            
            except httpx.HTTPStatusError as err:
                raise BlobStorageException(
                    code=err.response.status_code or 500,
                    detail=err.response.json(),
                    message="Error de comunicaçao com o provedor de armazenamento."
                ) from err

if __name__ == "__main__":            
    from findacat import FindaCat, CatOptions
    from src.setup import config
    import asyncio

    async def beautiful_main():
        """
        Save one cat ;)
        """

        my_cats = FindaCat()
        options = CatOptions(format="webp")
        cat = my_cats.get_cat(options)
        cat_image = cat.content

        storage = SupabaseStorage(
            supabase_url=config.SUPABASE_URL,
            supabase_key=config.SUPABASE_KEY,
            supabase_storage_name=config.SUPABASE_STORAGE_NAME,
        )

        try:
            file = await storage.upload_archive(
                "mycat",
                "webp",
                cat_image,
            )
        except BlobStorageException as err:
            print(
                f"""
                Error: {err.message}
                Detail: {err.detail}
                Code: {err.code}
                """
            )

            raise

        print(
            f"""
            Your cat

            Name: {file.name}
            Link: {file.link}
            Created at: {file.created_at}
            """
        )

    asyncio.run(beautiful_main())
