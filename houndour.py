import rotom
import json
import docker
import time


if __name__ == '__main__':
    with open('houndour.json') as f:
        config = json.load(f)

    rotom_client = rotom.Rotom(config)
    docker_client = docker.from_env()
    while True:
        rotom_client.get_status_page()
        needs_reboot = rotom_client.get_reboot_needed()
        if len(needs_reboot) == 0:
            print('[Houndour] all devices alive')
        for device in needs_reboot:
            print(f'[Houndour] {device["deviceName"]} needs to be restarted')
            restarted = False
            for container in docker_client.containers.list():
                if container.name == device['dockerName']:
                    container.restart()
                    restarted = True
                    break
            if restarted:
                print(f'[Houndour] {device["deviceName"]} sucessfully restarted')
            else:
                print(f'[Houndour] {device["deviceName"]} container not found')
        time.sleep(rotom_client.get_check_interval())