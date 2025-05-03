import click
import subprocess
from pkg_resources import resource_filename
from tensorkube.constants import get_cluster_name
from tensorkube.services.configure_service import update_cfn_configure_stack

def apply():
    try:
        folder_name = "configurations/cloudformation/configure/cluster_access_lambda_files/helm-charts/tk-karpenter-config"
        chart_path = resource_filename("tensorkube", folder_name)
        release_name = "karpenter-configuration"
        subprocess.run(["helm", "upgrade", "--install", release_name,  chart_path, "--set", f"clusterName={get_cluster_name()}"], check=True)
        updated_params = {
            "TemplatesVersion": "v0.0.2",
            "AWSAccessLambdaFunctionImageVersion": "v1.0.1",
            "CliVersion": "0.0.80",
            "EksAccessLambdaFunctionImageVersion": "v1.0.1"
        }
        update_cfn_configure_stack(updated_parameters=updated_params, test=False)

    except Exception as e:
        click.echo(click.style(f"Failed to apply karpenter configuration helm chart from {chart_path}: {e}", bold=True, fg="red"))
        raise e