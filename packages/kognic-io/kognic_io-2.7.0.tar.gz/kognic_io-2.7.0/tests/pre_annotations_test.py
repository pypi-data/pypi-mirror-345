from __future__ import absolute_import, annotations

import time
from datetime import datetime

import pytest

import examples.create_scene_with_scene_request
import kognic.io.client as IOC
from examples.utils import wait_for_scene_job


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestPreAnnotations:
    def test_list(self, client: IOC.KognicIOClient):
        data = client.pre_annotation.list(statuses=["processing", "available"])
        assert len(data) > 0, "Expected at least one pre-annotation to be returned"

    def test_create_indexed(
        self,
        client: IOC.KognicIOClient,
        uri_for_external_ol: str,
    ):
        scene = examples.create_scene_with_scene_request.run(client)
        wait_for_scene_job(client, scene.scene_uuid, timeout=60)
        pre_annotation_id = client.pre_annotation.create_from_cloud_resource(
            scene_uuid=scene.scene_uuid,
            external_id=f"pre_annotation_external_id-{datetime.now().isoformat()}",
            cloud_resource_uri=uri_for_external_ol,
            postponse_import=True,
        )

        data = client.pre_annotation.list(
            ids=[pre_annotation_id],
        )
        assert data is not None, "Expected a pre-annotation to be created"
        assert len(data) == 1, "Expected exactly one pre-annotation to be returned"
        assert data[0].get("status") == "indexed", "Expected the pre-annotation to be in indexed status"

    def test_create(
        self,
        client: IOC.KognicIOClient,
        uri_for_external_ol: str,
    ):
        scene = examples.create_scene_with_scene_request.run(client)
        wait_for_scene_job(client, scene.scene_uuid, timeout=60)
        pre_annotation_id = client.pre_annotation.create_from_cloud_resource(
            scene_uuid=scene.scene_uuid,
            external_id=f"pre_annotation_external_id-{datetime.now().isoformat()}",
            cloud_resource_uri=uri_for_external_ol,
            postponse_import=False,
        )
        time.sleep(5)
        data = client.pre_annotation.list(
            ids=[pre_annotation_id],
        )
        assert data is not None, "Expected a pre-annotation to be created"
        assert len(data) == 1, "Expected exactly one pre-annotation to be returned"
        assert data[0].get("status") == "available", "Expected the pre-annotation to be in available status"

    def test_make_indexed_available(self, client: IOC.KognicIOClient, uri_for_external_ol: str):
        scene = examples.create_scene_with_scene_request.run(client)
        wait_for_scene_job(client, scene.scene_uuid, timeout=60)
        pre_annotation_id = client.pre_annotation.create_from_cloud_resource(
            scene_uuid=scene.scene_uuid,
            external_id=f"pre_annotation_external_id-{datetime.now().isoformat()}",
            cloud_resource_uri=uri_for_external_ol,
            postponse_import=True,
        )

        data = client.pre_annotation.list(
            ids=[pre_annotation_id],
        )
        assert data is not None, "Expected a pre-annotation to be created"
        assert len(data) == 1, "Expected exactly one pre-annotation to be returned"
        assert data[0].get("status") == "indexed", "Expected the pre-annotation to be in indexed status"

        client.pre_annotation.make_indexed_pre_annotation_available(pre_annotation_id)
        time.sleep(5)
        data = client.pre_annotation.list(
            ids=[pre_annotation_id],
        )
        assert data is not None, "Expected a pre-annotation to be created"
        assert len(data) == 1, "Expected exactly one pre-annotation to be returned"
        assert data[0].get("status") == "available", "Expected the pre-annotation to be in available status"

    def test_delete(self, client: IOC.KognicIOClient, uri_for_external_ol: str):
        scene = examples.create_scene_with_scene_request.run(client)
        wait_for_scene_job(client, scene.scene_uuid, timeout=60)
        pre_annotation_id = client.pre_annotation.create_from_cloud_resource(
            scene_uuid=scene.scene_uuid,
            external_id=f"pre_annotation_external_id-{datetime.now().isoformat()}",
            cloud_resource_uri=uri_for_external_ol,
            postponse_import=True,
        )

        client.pre_annotation.delete(id=pre_annotation_id)
