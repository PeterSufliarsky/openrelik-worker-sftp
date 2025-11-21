# OpenRelik worker for uploading files using SFTP
## Description
This worker can be used for uploading files to a server using SFTP.

## Deploy
Add the below configuration to the OpenRelik docker-compose.yml file.

```
openrelik-worker-sftp:
    container_name: openrelik-worker-sftp
    image: openrelik-worker-sftp:latest
    restart: always
    environment:
      - REDIS_URL=redis://openrelik-redis:6379
      - OPENRELIK_PYDEBUG=0
    volumes:
      - ./data:/usr/share/openrelik/data
    command: "celery --app=src.app worker --task-events --concurrency=4 --loglevel=INFO -Q openrelik-worker-sftp"
    # ports:
      # - 5678:5678 # For debugging purposes.
```

## Test
```
uv sync --group test
uv run pytest -s --cov=.
```
