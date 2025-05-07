# simpipe

![Version: 0.1.0-dev](https://img.shields.io/badge/Version-0.1.0--dev-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.1.0-dev](https://img.shields.io/badge/AppVersion-0.1.0--dev-informational?style=flat-square)

A helm chart to deploy the SimPipe service components

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://registry-1.docker.io/bitnamicharts | mongodb | 16.4.5 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| dev.client_image_tag | string | `nil` |  |
| dev.mount_repo | bool | `true` |  |
| dev.runAsGroup | int | `1000` |  |
| dev.runAsUser | int | `1000` |  |
| dev.run_tests | bool | `true` |  |
| dev.sleep | bool | `false` |  |
| dev.start_long_running_client | bool | `false` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository | string | `"harbor.cta-observatory.org/dpps/simpipe-prod"` |  |
| mongodb.architecture | string | `"standalone"` |  |
| mongodb.auth.databases[0] | string | `"simulation-model"` |  |
| mongodb.auth.enabled | bool | `true` |  |
| mongodb.auth.passwords[0] | string | `"topsecret"` |  |
| mongodb.auth.rootPassword | string | `"topsecret"` |  |
| mongodb.auth.rootUser | string | `"root"` |  |
| mongodb.auth.usernames[0] | string | `"simpipe"` |  |
| mongodb.enabled | bool | `true` |  |
| mongodb.fullnameOverride | string | `"simtools-mongodb"` |  |
| mongodb.global.security.allowInsecureImages | bool | `true` |  |
| mongodb.image.registry | string | `"harbor.cta-observatory.org"` |  |
| mongodb.image.repository | string | `"proxy_cache/bitnami/mongodb"` |  |
| mongodb.image.tag | string | `"8.0.5-debian-12-r0"` |  |
| mongodb.replicaCount | int | `1` |  |
| simulation_model | object | `{"log_level":"warning","repository":"https://gitlab.cta-observatory.org/cta-science/simulations/simulation-model/simulation-models.git","revision":"v0.5.0"}` | Configuration of the simulation model source |
| simulation_model.log_level | string | `"warning"` | Log level for the application bootstrapping the simulation model database |
| simulation_model.repository | string | `"https://gitlab.cta-observatory.org/cta-science/simulations/simulation-model/simulation-models.git"` | Git repository with the model files |
| simulation_model.revision | string | `"v0.5.0"` | Git revision to checkout |

