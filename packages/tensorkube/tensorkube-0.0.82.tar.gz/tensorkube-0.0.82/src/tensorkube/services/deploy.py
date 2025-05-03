import os
import time
import uuid
from typing import Optional, Dict, List

import click
from kubernetes import client
from pkg_resources import resource_filename
from tensorkube.services.k8s_service import find_and_delete_old_job, check_pod_status, start_streaming_pod,  \
    get_pod_name_corresponing_to_job, get_pod_status_from_job, list_secrets, get_image_tags_to_retain , apply_image_cleanup_job, start_streaming_service
from tensorkube.helpers import  sanitise_name, \
    extract_command_from_dockerfile, extract_workdir_from_dockerfile

from tensorkube.constants import DEFAULT_NAMESPACE, BUILD_TOOL, PodStatus, CliColors
from tensorkube.services.aws_service import get_credentials, are_credentials_valid
from tensorkube.services.environment_service import check_environment_exists
from tensorkube.services.s3_service import  upload_files_in_parallel, empty_s3_folder, get_bucket_name

from tensorkube.services.build import apply_k8s_buildkit_config

from tensorkube.services.knative_service import apply_knative_service, apply_virtual_service_for_routing, \
    apply_tls_virtual_service, apply_tls_gateway, get_tls_gateway_name, check_existing_virtual_service, \
    get_subpath_virtual_service_name, delete_virtual_service


DEFAULT_GPUS = 0
DEFAULT_GPU_TYPE = None
DEFAULT_CPU = 100
DEFAULT_MEMORY = 200
DEFAULT_MIN_SCALE = 0
DEFAULT_MAX_SCALE = 3
DEFAULT_GITHUB_ACTIONS = False
DEFAULT_ENV = None
DEFAULT_SECRET = None
DEFAULT_DOMAIN_NAME = None
DEFAULT_ENTRYPOINT = None


def upload_build_context_to_s3(bucket_name, sanitised_project_name, cwd):
    # TODO: figure out how to upload only the updated files to the s3 bucket
    click.echo("Deleting any outdated files in the S3 bucket...")
    empty_s3_folder(bucket_name=bucket_name, folder_name="build/" + sanitised_project_name + "/")

    click.echo("Uploading the current directory to the S3 bucket...")
    upload_files_in_parallel(bucket_name=bucket_name, folder_path=cwd, s3_path="build/" + sanitised_project_name + "/")


def create_deployment_details(secret: list, env: str):
    secrets = [s for s in secret]
    if env and not check_environment_exists(env_name=env):
        click.echo("Environment does not exist. Please create the environment first.")
        return None, None, None, None, None
    env_namespace = DEFAULT_NAMESPACE if not env else env
    if secrets:
        secrets_list = list_secrets(env_namespace)
        secrets_names_list = [secret.metadata.name for secret in secrets_list]
        for secret in secrets:
            if secret not in secrets_names_list:
                click.echo(
                    click.style("Secret ", fg=CliColors.ERROR.value) + click.style(secret, fg=CliColors.ERROR.value,
                                                                                   bold=True,
                                                                                   italic=True) + click.style(
                        " not found in the environment.", fg=CliColors.ERROR.value))
                return None, None, None, None, None

    image_tag = uuid.uuid4().hex
    cwd = os.getcwd()
    non_sanitised_name = os.path.basename(cwd)
    sanitised_project_name = sanitise_name(non_sanitised_name)

    return secrets, env_namespace, image_tag, cwd, sanitised_project_name


def build_app(env, sanitised_project_name, image_tag, upload_to_nfs: bool = False, image_url: Optional[str] = None, convert_to_nydus_image: bool= False,
              work_dir: str = os.getcwd(), secrets: List[str] = []):
    is_dockerfile_present = False
    for root, dirs, files in os.walk(work_dir):
        for file in files:
            local_file = os.path.join(root, file)
            if local_file == work_dir + "/Dockerfile":
                is_dockerfile_present = True

    if not is_dockerfile_present:
        click.echo("No Dockerfile found in current directory.")
        return

    bucket_name = get_bucket_name(env_name=env)

    build_job_name = f'{BUILD_TOOL}-{sanitised_project_name}'
    old_cleanup_job = 'cleanup-{}'.format(sanitised_project_name)

    env_namespace = DEFAULT_NAMESPACE if not env else env
    old_job_deleted = find_and_delete_old_job(job_name=build_job_name, namespace=env_namespace)
    old_cleanup_job_del = find_and_delete_old_job(job_name=old_cleanup_job, namespace=env_namespace)
    if not old_job_deleted:
        click.echo("Another deployment is already in progress. Please wait for the build to complete.")
        return

    # TODO!: add logic to update the aws-secret only if IAM Identity Center User
    credentials = get_credentials()
    if are_credentials_valid(credentials):
        click.echo("Credentials are up to date")
    else:
        click.echo("The AWS credentials have expired. Please update the credentials.")
        return
    upload_build_context_to_s3(bucket_name=bucket_name, sanitised_project_name=sanitised_project_name, cwd=work_dir)
    click.echo("Building the Docker image...")
    
    apply_k8s_buildkit_config(sanitised_project_name=sanitised_project_name, image_tag=image_tag, env_name=env, image_url=image_url, upload_to_nfs=upload_to_nfs,convert_to_nydus_image=convert_to_nydus_image, secrets=secrets)
    build_job_pod_name = get_pod_name_corresponing_to_job(job_name=build_job_name, namespace=env_namespace)
    if build_job_pod_name is None:
        click.echo("Build Pod not found")
        return PodStatus.FAILED.value
    # TODO: stream multiple lines instead of one by one
    start_streaming_pod(pod_name=build_job_pod_name, namespace=env_namespace, status=PodStatus.SUCCEEDED)

    transition_time = time.time()
    # wait for the pod to transition
    while True:
        try:
            pod_status = check_pod_status(pod_name=build_job_pod_name, namespace=env_namespace)
        except client.ApiException as e:
            if e.status == 404:
                print('Pod not found.')
                pod_status = get_pod_status_from_job(job_name=build_job_name, namespace=env_namespace)
            else:
                pod_status = PodStatus.FAILED.value
        print('Waiting for pod to transition')
        if pod_status in ['Succeeded', 'Completed', 'Failed']:
            break
        if time.time() - transition_time > 60:  # 60 seconds have passed
            print("Timeout: Pod did not reach the desired state within 1 minute.")
            break
        time.sleep(5)
    return pod_status

def deploy_knative_service(env: str, gpus: int, gpu_type: str, cpu: float, memory: float, min_scale: int, max_scale: int, concurrency: int,
                           pod_status: str, cwd: str, sanitised_project_name: str, image_url: str, secrets: list, port: int, domain: Optional[str],
                           enable_efs: bool = False, github_actions: bool = DEFAULT_GITHUB_ACTIONS, readiness: Optional[Dict] = None,
                           startup_probe: Optional[Dict] = None, liveness_probe: Optional[Dict] = None, volumes: Optional[List[Dict]] = None):
    env_namespace = DEFAULT_NAMESPACE if not env else env

    if pod_status == 'Succeeded' or pod_status == 'Completed':
        click.echo("Successfully built and pushed the Docker image.")
        yaml_file_path = resource_filename('tensorkube', 'configurations/build_configs/knative_base_config.yaml')
        dockerfile_path = cwd + "/Dockerfile"
        workdir = extract_workdir_from_dockerfile(dockerfile_path)
        command = extract_command_from_dockerfile(dockerfile_path)
        service_name = f"{sanitised_project_name}-gpus-{gpus}-{str(gpu_type).lower()}"
        apply_knative_service(service_name=service_name, yaml_file_path=yaml_file_path,
                                            sanitised_project_name=sanitised_project_name, image_tag=image_url,
                                            workdir=workdir, command=command, gpus=gpus, gpu_type=gpu_type, cpu=cpu,
                                            memory=memory, min_scale=min_scale, max_scale=max_scale, env=env,
                                            secrets=secrets, enable_efs=enable_efs, domain=domain,
                                            concurrency=concurrency, readiness = readiness, port = port,
                                            startup_probe=startup_probe, liveness_probe=liveness_probe,
                                            volumes=volumes)
        if domain is None:
            virtual_service_yaml_file_path = resource_filename('tensorkube',
                                                               'configurations/build_configs/virtual_service.yaml')
            apply_virtual_service_for_routing(service_name=service_name, yaml_file_path=virtual_service_yaml_file_path,
                                              env=env, sanitised_project_name=sanitised_project_name)
        else:
            # check if the subpath virtual service exists if yes clean it up
            click.echo(click.style(
                "Checking for existing virtual service for subpath routing", fg="green"
            ))
            subpath_virtual_service_name = get_subpath_virtual_service_name(
                                                      service_name=service_name)
            if check_existing_virtual_service(namespace=env_namespace,
                                              virtual_service_name=subpath_virtual_service_name):
                delete_virtual_service(virtual_service_name=subpath_virtual_service_name, namespace=env_namespace)
            virtual_service_yaml_file_path = resource_filename('tensorkube',
                                                               'configurations/build_configs/istio_virtualservice_domain.yaml')
            gateway_yaml_file_path = resource_filename('tensorkube',
                                                       'configurations/build_configs/istio_gateway_subdomain_base.yaml')
            # Apply the Istio Gateway
            apply_tls_gateway(service_name=service_name, domain=domain, yaml_file_path=gateway_yaml_file_path,
                              gateway_namespace=env_namespace)
            apply_tls_virtual_service(service_name=service_name, domain=domain,
                                      yaml_file_path=virtual_service_yaml_file_path,
                                      gateway_name=get_tls_gateway_name(domain), namespace=env_namespace)
        images_to_retain = get_image_tags_to_retain(sanitised_project_name=sanitised_project_name,
                                                    service_name=service_name, namespace=env_namespace)
        if enable_efs:
            apply_image_cleanup_job(sanitised_project_name=sanitised_project_name, image_tags=images_to_retain, env=env)
        start_streaming_service(service_name=service_name, namespace=env_namespace)
    else:
        if github_actions:
            raise Exception("Failed to build the Docker image. Please check the logs for more details. Pod status: {}".format(
                pod_status))
        else:
            click.echo("Failed to build the Docker image. Please check the logs for more details. Pod status: {}".format(
                pod_status))
