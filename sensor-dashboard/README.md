# sensor-dashboard

Grafana + Prometheus stack for local system sensor monitoring (CPU temps, fans, battery, GPU).
Runs the same way on any Linux machine.

## Quick start

```bash
# AMD GPU / no discrete GPU
docker compose up -d

# NVIDIA GPU (also enables the nvidia_gpu_exporter service)
docker compose --profile nvidia up -d
```

Open Grafana at **http://localhost:3000** — login `admin` / `admin`.
The "System Sensors" dashboard is pre-provisioned and ready.

## NVIDIA setup

The `nvidia` profile requires the NVIDIA Container Toolkit:

```bash
# Install nvidia-container-toolkit, then:
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Also uncomment the `nvidia_gpu` scrape job in `prometheus.yml`.

## What's collected

| Collector | Metrics |
|---|---|
| hwmon | CPU & AMD GPU temps, fan RPMs |
| cpufreq | Per-core scaling frequency |
| powersupplyclass | Battery %, charge/discharge status, watts |
| thermal_zone | ACPI thermal zones |
| nvidia_gpu_exporter | NVIDIA GPU temp (requires `--profile nvidia`) |

## Ports

| Service | Port |
|---|---|
| Grafana | 3000 |
| Prometheus | 9090 |
| node_exporter | 9100 (host network) |
| nvidia_gpu_exporter | 9835 |
