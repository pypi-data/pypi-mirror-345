from typing import List

import pytest

import examples.lidars_with_imu_data as lidars_example
import kognic.io.client as IOC
import kognic.io.model as IAM
from examples.utils import wait_for_scene_job
from tests.utils import TestProjects


@pytest.mark.skip("LIDAR-only inputs are currently unsupported")
class TestLidarsWithImuData:
    @staticmethod
    def filter_lidar_project(projects: List[IAM.Project]):
        return [p for p in projects if p.project == TestProjects.LidarsProject]

    def test_validate_lidars_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_project(projects)[0].project
        resp = lidars_example.run(client=client, project=project)
        assert resp is None

    def test_create_lidars_input(self, client: IOC.KognicIOClient):
        projects = client.project.get_projects()
        project = self.filter_lidar_project(projects)[0].project
        resp = lidars_example.run(client=client, project=project, dryrun=False)
        wait_for_scene_job(client=client, scene_uuid=resp.scene_uuid, timeout=60)
        assert isinstance(resp.scene_uuid, str)
