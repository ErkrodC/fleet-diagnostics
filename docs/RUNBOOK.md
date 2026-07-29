# Fleet Diagnostics Runbook

## Service overview

| Service | Container port | Host URL |
|---|---:|---|
| Exporter | 8000 | <http://localhost:8000/metrics> |
| Prometheus | 9090 | <http://localhost:9090/targets> |
| Grafana | 3000 | <http://localhost:3000> |

Inside the Compose network, each service has its own Docker DNS name and
listening address:

| Service | Internal address |
|---|---|
| Exporter | `http://exporter:8000` |
| Prometheus | `http://prometheus:9090` |
| Grafana | `http://grafana:3000` |

The services currently communicate in this direction:

| Caller | Destination | Purpose |
|---|---|---|
| Prometheus | `http://exporter:8000/metrics` | Scrape fleet metrics |
| Grafana | `http://prometheus:9090` | Query stored time-series data |

No service currently needs to call Grafana. A browser reaches Grafana through
the host port mapping at `http://localhost:3000`.

## Standard checks

Check service state and resource usage:

```powershell
docker compose ps --all
docker compose top exporter
docker stats --no-stream
```

Inspect recent logs:

```powershell
docker compose logs --tail 100 exporter
docker compose logs --tail 100 prometheus
docker compose logs --tail 100 grafana
```

Follow logs during reproduction:

```powershell
docker compose logs --follow exporter
```

## Connectivity checks

Enter the Grafana container:

```powershell
docker compose exec grafana sh
```

Test name resolution, TCP connectivity, and application health:

```sh
getent hosts prometheus
getent hosts exporter
nc -vz -w 2 prometheus 9090
nc -vz -w 2 exporter 8000
wget -S -O- http://prometheus:9090/-/healthy
wget -S -O- http://exporter:8000/metrics
```

Interpretation:

| Result | Likely layer |
|---|---|
| Name does not resolve | DNS or service registration |
| Network unreachable | Interface or route |
| Timeout | Routing, firewall, packet loss, or unavailable host |
| Connection refused | Host reachable; no listener on the port |
| HTTP 4xx | Network works; request/authentication problem |
| HTTP 5xx | Network works; server-side application problem |

## Linux resource checks

Inside a container:

```sh
ps aux
top
free -h
df -h
du -sh /var/lib/grafana
id
ls -ld /var/lib/grafana
netstat -lnt
```

- `free -h` shows memory pressure; focus on `available`.
- `df -h` shows filesystem capacity.
- `du -sh` locates space-consuming directories.
- `id` and `ls -l` help diagnose ownership and permission failures.
- `netstat -lnt` shows listening TCP sockets.

## Symptom: exporter target is down

1. Open <http://localhost:9090/targets> and capture the last scrape error.
2. Confirm exporter state with `docker compose ps --all`.
3. Read exporter logs.
4. From Grafana or another container, resolve `exporter`.
5. Test TCP port 8000.
6. Request `/metrics` and confirm that `fleet_*` metrics exist.
7. Restart only after collecting evidence:

```powershell
docker compose restart exporter
```

8. Verify the Prometheus target returns to `UP`.

## Symptom: dashboard is blank

1. Confirm Grafana and Prometheus are running.
2. Check the Prometheus target is `UP`.
3. Query `fleet_asset_online` directly in Prometheus.
4. From Grafana, test `prometheus:9090`.
5. Confirm the provisioned Prometheus data source uses that URL.
6. Inspect Grafana logs for provisioning or query errors.

## Symptom: telemetry does not change

1. Confirm the host file changed under `sample_data/`.
2. Confirm the read-only bind mount exists in `compose.yaml`.
3. Request exporter metrics and inspect the current value.
4. Allow for the exporter polling interval and Prometheus scrape interval.
5. If exporter values are stale, inspect exporter logs and file visibility.
6. If exporter values changed but Prometheus did not, investigate scraping.
7. If Prometheus changed but Grafana did not, investigate the query and refresh
   window.

## Recovery rule

Never stop at “the restart command succeeded.” Verify the complete user-facing
path:

```text
process running
-> expected port listening
-> HTTP endpoint healthy
-> Prometheus target UP
-> query returns current data
-> Grafana displays current data
```
