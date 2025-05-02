import json
import logging
import time

import flywheel
import requests
from flywheel.rest import ApiException

from fw_gear_deid_export.retry_utils import upload_file_with_retry
from flywheel_gear_toolkit.utils import sdk_post_retry_handler

TICKETED_UPLOAD_PATH = "/{ContainerType}/{ContainerId}/files"
log = logging.getLogger(__name__)


class Uploader:
    def __init__(self, fw_client: flywheel.Client):
        self.fw_client = fw_client
        self._supports_signed_url = None

    def supports_signed_url(self):
        """Get signed url feature"""
        if self._supports_signed_url is None:
            config = self.fw_client.get_config()

            # Support the new and legacy method of feature advertisement, respectively
            features = config.get("features")
            f1 = features.get("signed_url", False) if features else False
            f2 = config.get("signed_url", False)

            self._supports_signed_url = f1 or f2
        return self._supports_signed_url

    def upload(self, container, name, fileobj, metadata=None, upload_session=None):
        upload_fn = getattr(
            self.fw_client, f"upload_file_to_{container.container_type}", None
        )

        if not upload_fn:
            print(
                f"Skipping unsupported upload to container: {container.container_type}"
            )
            return

        log.debug(f"Uploading file {name} to {container.container_type}={container.id}")
        if self.supports_signed_url():
            self.signed_url_upload(
                container,
                name,
                fileobj,
                metadata=metadata,
                upload_session=upload_session,
            )
        else:
            upload_file_with_retry(
                container=container,
                upload_fn=upload_fn,
                file=flywheel.FileSpec(name, fileobj),
                metadata=json.dumps(metadata),
                max_retry=3,
            )

    def signed_url_upload(
        self, container, name, fileobj, metadata=None, upload_session=None
    ):
        """Upload fileobj to container as name, using signed-urls"""
        # Create ticketed upload
        path_params = {
            "ContainerType": pluralize(container.container_type),
            "ContainerId": container.id,
        }
        ticket, upload_url, headers = self.create_upload_ticket(
            path_params, name, metadata=metadata
        )

        log.debug(
            f"Upload url for {name} on {container.container_type}={container.id}: {ticket} (ticket={upload_url})"
        )
        if upload_session is None:
            upload_session = requests.Session()

        # Perform the upload
        resp = upload_session.put(upload_url, data=fileobj, headers=headers)
        max_retries = 3
        retry_num = 0
        if resp.status_code == 429 or 500 <= resp.status_code < 600:
            while retry_num < max_retries:
                log.info("Upload failed, retrying...")
                time.sleep(2**retry_num)
                retry_num += 1
                resp.close()
                resp = upload_session.put(upload_url, data=fileobj, headers=headers)

        resp.raise_for_status()
        resp.close()

        # Complete the upload
        self.complete_upload_ticket(path_params, ticket)

    def create_upload_ticket(self, path_params, name, metadata=None):
        """Create upload ticket"""
        body = {"metadata": metadata or {}, "filenames": [name]}

        response = self.call_api(
            TICKETED_UPLOAD_PATH,
            "POST",
            path_params=path_params,
            query_params=[("ticket", "")],
            body=body,
            response_type=object,
        )
        headers = get_upload_ticket_suggested_headers(response)
        return response["ticket"], response["urls"][name], headers

    def complete_upload_ticket(self, path_params, ticket):
        """Complete upload ticket"""
        self.call_api(
            TICKETED_UPLOAD_PATH,
            "POST",
            path_params=path_params,
            query_params=[("ticket", ticket)],
        )

    def call_api(self, resource_path, method, **kwargs):
        """Call api"""
        kwargs.setdefault("auth_settings", ["ApiKey"])
        kwargs.setdefault("_return_http_data_only", True)
        kwargs.setdefault("_preload_content", True)

        if method == "POST":
            ticket, ticket_id = kwargs.get("query_params", [(None, None)])[0]
            if ticket_id:
                # If ticket_id is within query_params, this is a complete_upload_ticket call,
                # which should be safe to retry, and if it returns
                # f'flywheel.rest.ApiException: (404) Reason: Could not find resource upload_ticket:{ticket}'
                # then the ticket has already been completed and the gear should continue
                with sdk_post_retry_handler(self.fw_client):
                    try:
                        return self.fw_client.api_client.call_api(
                            resource_path, method, **kwargs
                        )
                    except ApiException as e:
                        if e.status == 404:
                            log.debug(
                                "Signed URL ticket completion returned a 404, therefore "
                                "ticket no longer exists to be used. Continuing."
                            )
                            return
                        else:
                            raise e

            elif ticket:
                # If "ticket" is specified with no id, this is a create_upload_ticket call,
                # which should be safe to retry, because if it creates a second ticket,
                # the first ticket will expire after a time.
                with sdk_post_retry_handler(self.fw_client):
                    return self.fw_client.api_client.call_api(
                        resource_path, method, **kwargs
                    )

        # Other calls can be handled by the default retry
        # (but this gear currently only uses those two calls with call_api)
        return self.fw_client.api_client.call_api(resource_path, method, **kwargs)


def pluralize(container_type):
    """Convert container_type to plural name

    Simplistic logic that supports:
    group,  project,  session, subject, acquisition, analysis, collection
    """
    if container_type == "analysis":
        return "analyses"
    if not container_type.endswith("s"):
        return container_type + "s"
    return container_type


def get_upload_ticket_suggested_headers(response):
    """Read headers response property. Return None if it doesn't exist or is empty"""
    headers = None
    if response is not None:
        try:
            if response["headers"] and isinstance(response["headers"], dict):
                headers = response["headers"]
        except KeyError:
            pass
    return headers
