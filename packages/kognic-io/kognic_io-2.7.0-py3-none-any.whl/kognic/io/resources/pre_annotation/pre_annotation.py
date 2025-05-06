from typing import List, Optional
from urllib.parse import urlencode

from requests.exceptions import HTTPError

from kognic.io.model.base_serializer import BaseSerializer
from kognic.io.resources.abstract import IOResource
from kognic.openlabel.models.models import OpenLabelAnnotation


class CreatePreannotationRequest(BaseSerializer):
    scene_uuid: str
    pre_annotation: OpenLabelAnnotation


class PreAnnotationResource(IOResource):
    """
    Resource exposing Kognic PreAnnotations
    """

    def create(self, scene_uuid: str, pre_annotation: OpenLabelAnnotation, dryrun: bool) -> Optional[dict]:
        """
        Upload pre-annotation to a previously created scene.
        This is not possible to do if the scene already have inputs created for it

        :param scene_uuid: the uuid for the scene. Will be the input uuid when input is created
        :param pre_annotation: PreAnnotation on the OpenLabel format
        :param dryrun: If True the files/metadata will be validated but no pre-annotation will be created
        """
        pre_anno_request = CreatePreannotationRequest(scene_uuid=scene_uuid, pre_annotation=pre_annotation)
        return self._client.post("v1/pre-annotations", json=pre_anno_request.to_dict(), dryrun=dryrun, discard_response=True)

    def list(
        self,
        ids: Optional[List[str]] = None,
        external_ids: Optional[List[str]] = None,
        scene_uuids: Optional[List[str]] = None,
        scene_external_ids: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        List pre-annotations.

        :param scene_uuids: The uuids of the scenes.
        :param status: The status of the pre-annotations to filter on. If None, all pre-annotations will be returned.

        :return: A page of the pre-annotations matching the query.
        """
        params = {
            "offset": 0,
            "limit": 1000,
        }
        if ids:
            params["uuids"] = ids
        if external_ids:
            params["externalIds"] = external_ids
        if scene_uuids:
            params["sceneUuids"] = scene_uuids
        if scene_external_ids:
            params["sceneExternalIds"] = scene_external_ids
        if statuses:
            params["statuses"] = statuses

        has_next = True
        offset = 0
        data = []

        while has_next:
            url = f"{self._client.host}/v2/pre-annotations?{urlencode(params, doseq=True)}"
            resp = self._client.session.get(
                url,
                headers=self._client.headers,
                timeout=self._client.timeout,
            )

            if 400 <= resp.status_code < 500:
                try:
                    message = resp.json()["message"]
                except ValueError:
                    message = resp.text
                raise HTTPError(f"Client error: {resp.status_code} - {message}", response=resp)
            elif resp.status_code >= 300:
                resp.raise_for_status()

            json_resp = resp.json()
            data += json_resp.get("data", [])
            has_next = json_resp.get("hasNext")
            offset += 1000

        return data

    def create_from_cloud_resource(
        self, scene_uuid: str, external_id: str, cloud_resource_uri: str, postponse_import: Optional[bool] = True
    ) -> str:
        """
        Create pre-annotation to a previously created scene. The pre-annotation will be created in the same workspace as the scene.


        :param scene_uuid: The uuid for the scene.
        :param external_id: A human readable unique identifier of the pre-annotation.
        :param cloud_resource_uri: The cloud resource uri of the pre-annotation
        :param postponse_import: If True, the pre-annotation will be created but not imported to the kognic platform.
            So no data will leave you cloud yet.
            If False, the pre-annotation will be created and imported to the kognic platform
            and kognic will read the cloud_resource_uri from your bucket.

        :return: The uuid of the created pre-annotation.
        """
        body = dict(
            sceneUuid=scene_uuid,
            externalId=external_id,
            externalResourceId=cloud_resource_uri,
            postponeExternalResourceImport=postponse_import,
        )
        resp = self._client.post("v2/pre-annotations", json=body)
        return resp.get("id")

    def make_indexed_pre_annotation_available(self, id: str):
        """
        Import the cloud resource to kognics platform.

        :param id: The uuid of the pre-annotation.
        """
        body = dict(status="processing")
        self._client.patch(f"v2/pre-annotations/{id}", json=body, discard_response=True)

    def delete(self, id: str):
        """
        Delete the pre-annotation.

        :param id: The uuid of the pre-annotation.
        """
        self._client.delete(f"v2/pre-annotations/{id}", discard_response=True)
