"""Module for situation-specific retry utils."""

from flywheel import Acquisition, Subject, Session, Project, FileSpec
import logging
import time
import re

log = logging.getLogger(__name__)


def upload_file_with_retry(
    container: Project | Subject | Session | Acquisition,
    upload_fn,
    file: FileSpec,
    metadata: str = None,
    max_retry: int = 3,
):
    """Calls POST /api/container/cid/files with smart retry.

    Args:
        container: Flywheel Project/Subject/Session/Acquisition object
        upload_fn: fw_client.upload_file_to_{container_type}
        file: Flywheel FileSpec object
        metadata: Metadata to attach to the uploaded file, if any
        max_retry: Max times to retry after initial POST, default 3
    """
    # If a version of the file already exists in destination container,
    # will need to make sure overwrite happens, not just that file exists,
    # to confirm upload.
    version = 0
    for f in container.files:
        if f.name == file.name:
            # Overwriting, store current version
            version = f.version

    retry_num = 0
    while retry_num <= max_retry:
        try:
            return upload_fn(container.id, file, metadata=metadata)
            # API: POST /api/container/cid/files
        except Exception as e:
            log.warning(
                f"Encountered error uploading file {file.name}\n{e}\n"
                f"Retries remaining: {max_retry-retry_num}"
            )
            time.sleep(2**retry_num)
            container = container.reload()
            for f in container.files:
                if f.name == file.name and f.version > version:
                    # File uploaded, log, don't retry
                    log.info(
                        f"{file.name} version {f.version} exists in {container.type} {container.label}. "
                        "Upload completed with above error, continuing..."
                    )
                    return f
            retry_num += 1
    raise Exception(f"Max retries attempted for uploading {file.name}.")


def create_container_with_retry(
    dest_parent: Project | Subject | Session,
    origin_type: str,
    label: str,
    meta_dict: dict,
    max_retry: int = 3,
):
    """Calls POST /api/container with smart retry.

    Args:
        dest_parent: Parent of container to be created
        origin_type: Type of container to create
        label: Label of new container
        meta_dict: Dictionary of container meta information
        max_retry: Max times to retry after initial POST, default 3
    """
    adder = getattr(dest_parent, f"add_{origin_type}")
    finder_first = getattr(getattr(dest_parent, f"{origin_type}s"), "find_first")
    query = f"label={quote_numeric_string(label)}"

    retry_num = 0
    while retry_num <= max_retry:
        try:
            # API: POST /container
            return adder(label=label, **meta_dict)
        except Exception as e:
            log.warning(
                f"Encountered error creating {origin_type} {label}\n{e}\n"
                f"Retries remaining: {max_retry-retry_num}"
            )
            time.sleep(2**retry_num)
            # Check to see if container exists
            dest_container = finder_first(query)
            if dest_container:
                log.info(
                    f"{origin_type} {label} exists in {dest_parent.label}. "
                    "Container creation completed with above error, continuing..."
                )
                return dest_container
            retry_num += 1
    raise Exception(f"Max retries attempted for creating {origin_type} {label}.")


def quote_numeric_string(input_str: str):
    """Wraps a numeric string in double quotes. Attempts to coerce non-str to str and logs a warning.

    Args:
        input_str: string to be modified (if numeric string)

    Returns:
        str: A numeric string wrapped in quotes if input_str is numeric, or str(input_str)
    """

    if not isinstance(input_str, str):
        log.warning(
            f"Expected {input_str} to be a string. Is type: {type(input_str)}. Attempting to coerce to str..."
        )
        input_str = str(input_str)
    if re.match(r"^[\d]+[\.]?[\d]*$", input_str):
        output_str = f'"{input_str}"'
    else:
        output_str = input_str
    return output_str
