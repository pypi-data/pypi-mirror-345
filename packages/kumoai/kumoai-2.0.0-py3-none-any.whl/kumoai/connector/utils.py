import asyncio
import io
import math
import os
import time
from logging import getLogger
from typing import Generator, List, Tuple

import aiohttp
from kumoapi.data_source import (
    CompleteFileUploadRequest,
    DeleteUploadedFileRequest,
    PartUploadMetadata,
    StartFileUploadRequest,
    StartFileUploadResponse,
)
from tqdm.asyncio import tqdm_asyncio

from kumoai import global_state
from kumoai.exceptions import HTTPException
from kumoai.futures import _KUMO_EVENT_LOOP

CHUNK_SIZE = 100 * 10**6  # 100 MB

logger = getLogger(__name__)

CONNECTOR_ID_MAP = {
    "csv": "csv_upload_connector",
    "parquet": "parquet_upload_connector",
}


async def put(
    session: aiohttp.ClientSession,
    url: str,
    data: bytes,
    part_no: int,
) -> Tuple[int, str]:
    r"""Performs an asynchronous PUT request to upload data to a presigned S3
    URL, and returns a tuple corresponding to the uploaded part number and
    the Etag of the header.

    Args:
        session: the ``aiohttp`` client session to use for the request
        url: the S3 presigned URL to PUT ``data`` to
        data: the data (``bytes``) that should be PUT to ``url``
        part_no: the part number of the data to be PUT
    """
    # TODO(manan): add retry...
    async with session.put(url, data=data) as res:
        logger.debug("PUT part_no=%s bytes=%s", part_no, len(data))
        _ = await res.text()
        if res.status != 200:
            raise RuntimeError(
                f"PUT URL={url} failed: with status {res.status}: "
                f"{res}")
        headers = res.headers
        return (part_no + 1, headers['Etag'])


async def multi_put(
    loop: asyncio.AbstractEventLoop,
    urls: List[str],
    data: Generator[bytes, None, None],
) -> List[PartUploadMetadata]:
    r"""Performs multiple asynchronous PUT requests of the data yielded
    from the ``data`` generator to the specified URLs. If the data
    generator is exhausted early, only a subset of URLs are used. If
    the data generator is not exhausted by the URLs, uploaded data may
    be corrupted!
    """
    # TODO(manan): retry
    # TODO(manan): properly stream chunks
    async with aiohttp.ClientSession(
        loop=loop,
        connector=aiohttp.TCPConnector(verify_ssl=False),
        headers={'Content-Type': 'binary'},
    ) as session:
        results = await tqdm_asyncio.gather(*[
            put(session, url, data, i)
            for i, (url, data) in enumerate(zip(urls, data))
        ])
        for r in results:
            if isinstance(r, BaseException):
                raise r
        return [PartUploadMetadata(v[0], v[1]) for v in results]


def stream_read(
    f: io.BufferedReader,
    chunk_size: int,
) -> Generator[bytes, None, None]:
    r"""Streams ``chunk_size`` contiguous bytes from buffered reader
    ``f`` each time the generator is yielded from.
    """
    while True:
        byte_buf = f.read(chunk_size)
        if len(byte_buf) == 0:
            # StopIteration:
            break
        yield byte_buf


def upload_table(name: str, path: str) -> None:
    r"""Synchronously uploads a table located on your local machine to the Kumo
    data plane. Tables uploaded in this way can be accessed with a
    :class:`~kumoai.connector.FileUploadConnector`.

    .. warning::

        Uploaded tables must be single files, either in parquet or CSV
        format. Partitioned tables are not currently supported.

    .. code-block:: python

        import kumoai
        from kumoai.connector import upload_table

        # Assume we have a table located at /data/users.parquet, and we
        # want to upload this table to Kumo, to be used downstream:
        upload_table(name="users", path="/data/users.parquet")

    Args:
        name: The name of the table to be uploaded. The uploaded table can
            be accessed from the :class:`~kumoai.connector.FileUploadConnector`
            with this name.
        path: The full path of the table to be uploaded, on the local
            machine.
    """
    # TODO(manan): support progress bars
    # Validate:
    if not (path.endswith(".parquet") or path.endswith(".csv")):
        raise ValueError(f"Path {path} must be either a CSV or Parquet "
                         f"file. Partitioned data is not currently supported.")

    # Prepare upload (number of parts based on total size):
    file_type = 'parquet' if path.endswith('parquet') else 'csv'
    sz = os.path.getsize(path)
    logger.info("Uploading table %s (path: %s), size=%s bytes", name, path, sz)

    upload_res = _start_table_upload(
        table_name=name,
        file_type=file_type,
        file_size_bytes=sz,
    )

    # Chunk and upload:
    urls = list(upload_res.presigned_part_urls.values())
    loop = _KUMO_EVENT_LOOP

    part_metadata_list_fut = asyncio.run_coroutine_threadsafe(
        multi_put(loop, urls=urls, data=stream_read(
            open(path, 'rb'),
            CHUNK_SIZE,
        )), loop)
    part_metadata_list = part_metadata_list_fut.result()

    # Complete:
    logger.info("Upload complete. Validating table %s.", name)
    for i in range(5):
        try:
            _complete_table_upload(
                table_name=name,
                file_type=file_type,
                upload_path=upload_res.temp_upload_path,
                upload_id=upload_res.upload_id,
                parts_metadata=part_metadata_list,
            )
        except HTTPException as e:
            if e.status_code == 500 and i < 4:
                # TODO(manan): this can happen when DELETE above has
                # not propagated. So we retry with delay here. We
                # assume DELETE is processed reasonably quickly:
                time.sleep(2**(i - 1))
                continue
            else:
                raise e
        else:
            break

    logger.info("Completed uploading table %s to Kumo.", name)


def delete_uploaded_table(
    name: str,
    file_type: str,
) -> None:
    r"""Synchronously deletes a previously uploaded table from the Kumo data
    plane.

    .. code-block:: python

        import kumoai
        from kumoai.connector import delete_uploaded_table

        # Assume we have uploaded a `.parquet` table named `users`,
        # and we want to delete this table from Kumo:
        delete_uploaded_table(name="users", file_type="parquet")

        # Assume we have uploaded a `.csv` table named `orders`,
        # and we want to delete this table from Kumo:
        delete_uploaded_table(name="orders", file_type="csv")

    Args:
        name: The name of the table to be deleted. This table must have
            previously been uploaded with a call to
            :meth:`~kumoai.connector.upload_table`.
        file_type: The file type of the table to be deleted; this can either
            be :obj:`"parquet"` or :obj:`"csv"`
    """
    assert file_type in {'parquet', 'csv'}
    req = DeleteUploadedFileRequest(
        source_table_name=name,
        connector_id=CONNECTOR_ID_MAP[file_type],
    )
    global_state.client.connector_api.delete_file_upload(req)
    logger.info("Successfully deleted table %s from Kumo.", name)


def replace_table(
    name: str,
    path: str,
    file_type: str,
) -> None:
    r"""Replaces an existing uploaded table on the Kumo data plane with a new
    table.

    .. code-block:: python

        import kumoai
        from kumoai.connector import replace_table

        # Replace an existing `.csv` table named `users`
        # with a new version located at `/data/new_users.csv`:
        replace_table(
            name="users",
            path="/data/new_users.csv",
            file_type="csv",
        )

    Args:
        name: The name of the table to be replaced. This table must have
            previously been uploaded with a call to
            :meth:`~kumoai.connector.upload_table`.
        path: The full path of the new table to be uploaded, on the
            local machine.
        file_type: The file type of the table to be replaced; this
            can either be :obj:`"parquet"` or :obj:`"csv"`.

    Raises:
        ValueError: If the specified path does not point to a valid
            `.csv` or `.parquet` file.
    """
    # Validate:
    if not (path.endswith(".parquet") or path.endswith(".csv")):
        raise ValueError(f"Path {path} must be either a CSV or Parquet file. "
                         f"Partitioned data is not currently supported.")

    try:
        logger.info("Deleting previously uploaded table %s of type %s.", name,
                    file_type)
        delete_uploaded_table(name=name, file_type=file_type)
    except Exception:
        # TODO(manan): fix this...
        pass

    logger.info("Uploading table %s.", name)
    upload_table(name=name, path=path)
    logger.info("Successfully replaced table %s with the new table.", name)


def _start_table_upload(
    table_name: str,
    file_type: str,
    file_size_bytes: float,
) -> StartFileUploadResponse:
    assert file_type in CONNECTOR_ID_MAP.keys()
    req = StartFileUploadRequest(
        source_table_name=table_name,
        connector_id=CONNECTOR_ID_MAP[file_type],
        num_parts=max(1, math.ceil(file_size_bytes / CHUNK_SIZE)),
    )
    return global_state.client.connector_api.start_file_upload(req)


def _complete_table_upload(
    table_name: str,
    file_type: str,
    upload_path: str,
    upload_id: str,
    parts_metadata: List[PartUploadMetadata],
) -> None:
    assert file_type in CONNECTOR_ID_MAP.keys()

    req = CompleteFileUploadRequest(
        source_table_name=table_name,
        connector_id=CONNECTOR_ID_MAP[file_type],
        temp_upload_path=upload_path,
        upload_id=upload_id,
        parts_metadata=parts_metadata,
    )
    return global_state.client.connector_api.complete_file_upload(req)
