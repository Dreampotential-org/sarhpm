## Running For Development Environment
---

Run the following command

```bash
docker-compose run --service project
```

## Running For Staging Environment
---

Run the following command

```bash
./buildkite/pipeline.sh
```
or

```bash
docker-compose -f docker-compose-staging.yml down
docker-compose build
docker-compose -f docker-compose-staging.yml up -d
```
## urbanrecovery.usepam.com
```
username: root@root.com
password: YTNmNzllZmUzNjAzMDViZGQ4Mzg4ZTI3
```


