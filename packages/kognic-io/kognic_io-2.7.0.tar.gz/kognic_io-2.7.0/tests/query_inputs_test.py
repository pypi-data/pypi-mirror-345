from typing import List

import pytest

import examples.cameras as cameras_example
import examples.query_inputs as query_inputs_example
from examples.utils import wait_for_scene_job
from kognic.io.client import KognicIOClient
from kognic.io.model import Project
from kognic.io.model.input.input import Input
from tests.utils import TestProjects


@pytest.mark.integration  # TODO: Remove this mark once the integration tests are ready
class TestQueryInputs:
    @staticmethod
    def filter_cameras_project(projects: List[Project]):
        return [p for p in projects if p.project == TestProjects.CamerasProject]

    def test_query_inputs_for_project(self, client: KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)[0].project
        project_inputs = query_inputs_example.run(client=client, project=project)

        assert isinstance(project_inputs, list)
        assert len(project_inputs) >= 1
        assert all(isinstance(input, Input) for input in project_inputs)

    def test_query_inputs_for_scene_uuid(self, client: KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_cameras_project(projects)[0].project
        resp = cameras_example.run(client=client, project=project, dryrun=False)
        scene_uuid = resp.scene_uuid

        assert isinstance(scene_uuid, str)
        wait_for_scene_job(client=client, scene_uuid=scene_uuid)

        inputs = query_inputs_example.run(client=client, scene_uuids=[scene_uuid])

        assert isinstance(inputs, list)
        assert len(inputs) == 1
        assert all(isinstance(input, Input) for input in inputs)
