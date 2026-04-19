def test_docker_compose_file_exists():
    import os
    assert os.path.exists('docker-compose.yml')
