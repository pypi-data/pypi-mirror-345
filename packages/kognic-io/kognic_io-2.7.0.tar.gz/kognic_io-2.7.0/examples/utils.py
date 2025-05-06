import time

from kognic.io.client import KognicIOClient
from kognic.io.model import SceneStatus


def wait_for_scene_job(client: KognicIOClient, scene_uuid: str, timeout=20) -> SceneStatus:
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        response = client.scene.get_scenes_by_uuids(scene_uuids=[scene_uuid])
        scene = response[0]
        if scene.status in [SceneStatus.Created, SceneStatus.Failed]:
            return scene.status

        time.sleep(1)

    raise Exception(f"Job was not finished: {scene_uuid}")
