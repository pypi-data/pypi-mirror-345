# wms

![Version: 0.2.0-dev](https://img.shields.io/badge/Version-0.2.0--dev-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.2.0-dev](https://img.shields.io/badge/AppVersion-0.2.0--dev-informational?style=flat-square)

A Helm chart to deploy the Workload Management System of CTAO

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://harbor.cta-observatory.org/dpps | cert-generator-grid | v0.2.2 |
| oci://harbor.cta-observatory.org/dpps | cvmfs | v0.4.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| CE | object | `{"enabled":true}` | Compute Element (CE) used by DIRAC, likely only needed for testing |
| affinity | object | `{}` |  |
| cert-generator-grid.enabled | bool | `true` |  |
| cert-generator-grid.generatePreHooks | bool | `true` |  |
| cvmfs.enabled | bool | `true` |  |
| cvmfs.publish_docker_images[0] | string | `"harbor.cta-observatory.org/proxy_cache/library/python:3.12-slim"` |  |
| dev.client_image_tag | string | `nil` | tag of the image used to run helm tests |
| dev.mount_repo | bool | `true` | mount the repo volume to test the code as it is being developed |
| dev.run_tests | bool | `true` | run tests in the container |
| dev.sleep | bool | `false` | sleep after test to allow interactive development |
| fullnameOverride | string | `""` |  |
| image.pullPolicy | string | `"IfNotPresent"` |  |
| image.repository_prefix | string | `"harbor.cta-observatory.org/dpps/wms"` |  |
| image.tag | string | `nil` | Overrides the image tag whose default is the chart appVersion. |
| imagePullSecrets[0].name | string | `"harbor-pull-secret"` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podLabels | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| replicaCount | int | `1` |  |
| resetDatabase | bool | `true` | Recreates DIRAC database from scratch. Useful at first installation, but destructive on update: should be changed immediately after the first installation. |
| resources | object | `{}` |  |
| rucio.enabled | bool | `false` |  |
| securityContext | object | `{}` |  |
| service.port | int | `8080` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` | Annotations to add to the service account |
| serviceAccount.automount | bool | `true` | Automatically mount a ServiceAccount's API credentials? |
| serviceAccount.create | bool | `true` | Specifies whether a service account should be created |
| serviceAccount.name | string | `""` | If not set and create is true, a name is generated using the fullname template |
| tolerations | list | `[]` |  |
| volumeMounts | list | `[]` |  |
| volumes | list | `[]` |  |

