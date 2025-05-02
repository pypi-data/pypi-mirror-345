import os
import shutil
import tempfile
from typing import Annotated
from paxpar.cli.command.version import version_get
from paxpar.shared.conf import get_conf_payload
import typer
from paxpar.cli.tools import PaxparCLI_ObjCtx, call, root_command_callback, call_yaml, console
from paxpar.cli.command.image import REGISTRIES
import httpx
import yaml

app = typer.Typer(
    help="pp deploy commands",
    callback=root_command_callback(),
)

"""
❯ scw container container list
ID                                    NAME                      NAMESPACE ID                          STATUS  MIN SCALE  MAX SCALE  MEMORY LIMIT  CPU LIMIT  TIMEOUT    ERROR MESSAGE  PRIVACY
6b0e651b-cc7e-4255-9264-013d1ebb8066  proxy                     8080c26f-515c-40c7-b388-fb168520207c  ready   0          1          2048          1120       5 minutes  -              public
36a7a4e1-dd3e-47d1-b381-ae003518b832  container-stoic-herschel  8080c26f-515c-40c7-b388-fb168520207c  ready   0          5          2048          1120       5 minutes  -              public
5a6669b7-cfd2-4076-809e-8a5dd14d7bea  gotenberg6-phentz         8080c26f-515c-40c7-b388-fb168520207c  ready   0          5          2048          1120       5 minutes  -              public
9645138c-a20a-4f4f-ac9b-be79a2d9f01f  gotenberg8                8080c26f-515c-40c7-b388-fb168520207c  ready   0          5          2048          1120       5 minutes  -              public
f8801dd4-a65b-44d6-b888-9aba928cad2e  simple-web                8080c26f-515c-40c7-b388-fb168520207c  ready   0          5          256           250        5 minutes  -              public
30a89147-362d-44aa-a961-7f3a158dbab9  paxpar-core-2c48f2d6      8080c26f-515c-40c7-b388-fb168520207c  ready   0          5          3072          1000       5 minutes  -              public
"""


@app.command(name="list")
def list_deployments(
    ctx: typer.Context,
):
    """
    List deployed instance
    """
    # TODO: get deployments from scaleway
    # call("""scw container container list""")

    #namespaces = call_yaml("""kubectl get namespaces -o yaml""")
    namespaces = call_yaml("""kubectl get Ingress --all-namespaces -o yaml""")

    #from IPython import embed; embed()

    # print(namespaces)
    #for namespace in namespaces.get("items", []):
    #    if (name := namespace.get("metadata", {}).get("name", "")).startswith("pp-dev"):
    #        print(name)

    for ingress in namespaces['items']:
        for rule in ingress['spec']['rules']:
            host = rule['host']
            raw = httpx.get(f"https://{host}/api/version")
            if raw.status_code == 200:
                print('back', raw.text)

            else:
                raw = httpx.get(f"https://{host}/VERSION")
                if raw.status_code == 200:
                    print('front', raw)
                    #TODO: get back used by this front
                else:
                    print(f'unknown {host} !!!!')


@app.command()
def remove(
    ctx: typer.Context,
    name: str,
):
    """
    Remove a deployed instance
    """
    ctx_obj: PaxparCLI_ObjCtx = ctx.obj
    # TODO: check if it is a pp deployment before !
    call(
        f"""kubectl delete namespace {name}""",
        ctx_obj=ctx_obj,
    )


@app.command()
def back(
    ctx: typer.Context,
    version: Annotated[str | None, typer.Argument()] = None,
    conf_file: list[str] = [],
    conf_file1: Annotated[str | None, typer.Option(envvar="PP_CONF_1")] = None,
    conf_file2: Annotated[str | None, typer.Option(envvar="PP_CONF_2")] = None,
    conf_file3: Annotated[str | None, typer.Option(envvar="PP_CONF_2")] = None,
    # the namespace to deploy to
    namespace: Annotated[
        str | None, typer.Option(envvar="DEPLOY_K8S_NAMESPACE")
    ] = None,
    # cluster agent to deploy to
    # cf https://gitlab.com/arundo-tech/paxpar-gitops/-/clusters
    k8s_context: Annotated[
        str, typer.Option(envvar="GITLAB_K8S_AGENT")
    ] = "arundo-tech/paxpar-gitops:arundo-cluster2024",
):
    """
    Deploy paxpar backend
    """
    ctx_obj: PaxparCLI_ObjCtx = ctx.obj

    # version = "4.2.37"
    if version is None:
        version = version_get(ctx_obj)
        if ctx_obj.verbose:
            print(f"No version specified, assuming {version}")

    if namespace is None:
        namespace = f"pp-dev-{version}".replace(".", "-")
        if ctx_obj.verbose:
            print(f"No namespace specified, assuming {namespace}")

    # set kubernetes context to the right cluster
    # example:  kubectl config use-context arundo-tech/paxpar-gitops:paxpar-clust1
    call(
        f"""kubectl config use-context {k8s_context}""",
        ctx_obj=ctx_obj,
    )
    call(
        f"""kubectl create namespace {namespace}""",
        ctx_obj=ctx_obj,
    )

    registries_credentials_create(
        namespace,
        ctx_obj,
    )

    # build PP_CONF section:
    # --set PP_CONF_1={PP_CONF_1} \
    # --set PP_CONF_2={PP_CONF_2} \
    # --set PP_CONF_3={PP_CONF_3} \
    conf_files = [
                    conf_file1 or "",
                    conf_file2 or "",
                    conf_file3 or "",
                    *conf_file,
                ]

    conf_payload = get_conf_payload(
        conf_files = conf_files,
        use_envvars=True,
    )

    if not ctx_obj.dry_run:
        # create overlays/generated from overlays/custom
        shutil.rmtree("packages/pp-api/deploy/kustomize/overlays/generated")
        shutil.copytree(
            "packages/pp-api/deploy/kustomize/overlays/custom",
            "packages/pp-api/deploy/kustomize/overlays/generated",
        )

    kust = yaml.safe_load(open("packages/pp-api/deploy/kustomize/overlays/generated/kustomization.yaml", "rt"))

    # ======= here we change the kustimize file !!

    kust['namespace'] = namespace
    kust['images'][0]['newTag'] = version
    kust['configMapGenerator'][0]['literals'] = [
        f'PP_CONF_{i}={conf_file}' for i, conf_file in enumerate(conf_files) if len(conf_file) > 0
    ]

    # ======= # ======= # ======= # ======= # ======= # ======= 


    if ctx_obj.verbose:
        print(yaml.safe_dump(kust, indent=2))

    if not ctx_obj.dry_run:
        with open("packages/pp-api/deploy/kustomize/overlays/generated/kustomization.yaml", "wt") as f:
            yaml.safe_dump(kust, f)

    call(
        #'''kubectl kustomize packages/pp-api/deploy/kustomize/overlays/generated''',
        '''kubectl apply -k packages/pp-api/deploy/kustomize/overlays/generated''',
        #cwd='packages/pp-api/deploy/kustomize/overlays/generated',
        ctx_obj=ctx_obj,
    )



@app.command(deprecated=True)
def api(
    ctx: typer.Context,
    #target: str = "arundo_cluster",
    version: Annotated[str | None, typer.Argument()] = None,
    conf_file: list[str] = [],
    conf_file1: Annotated[str | None, typer.Option(envvar="PP_CONF_1")] = None,
    conf_file2: Annotated[str | None, typer.Option(envvar="PP_CONF_2")] = None,
    conf_file3: Annotated[str | None, typer.Option(envvar="PP_CONF_2")] = None,
    helm_values_file: list[str] = [],
    helm_values: list[str] = [],
    #gitlab_token_registry_read: Annotated[
    #    str, typer.Option(envvar="GITLAB_TOKEN_REGISTRY_READ")
    #] = "xxx",
    #gitea_token_registry_read: Annotated[
    #    str, typer.Option(envvar="GITEA_TOKEN_REGISTRY_READ")
    #] = "xxx",
    # pax-partitus project id
    deploy_gitlab_project_id: Annotated[
        str, typer.Option(envvar="DEPLOY_GITLAB_PROJECT_ID")
    ] = "8545789",
    # DEPLOY_VERSION_RELEASE: "d4276905"
    deploy_helm_chart_name: Annotated[
        str, typer.Option(envvar="DEPLOY_HELM_CHART_NAME")
    ] = "paxpar",
    # the namespace to deploy to
    namespace: Annotated[
        str | None, typer.Option(envvar="DEPLOY_K8S_NAMESPACE")
    ] = None,
    # cluster agent to deploy to
    # cf https://gitlab.com/arundo-tech/paxpar-gitops/-/clusters
    k8s_context: Annotated[
        str, typer.Option(envvar="GITLAB_K8S_AGENT")
    ] = "arundo-tech/paxpar-gitops:arundo-cluster2024",
    ci_job_token: Annotated[str, typer.Option(envvar="CI_JOB_TOKEN")] = "xxx",
):
    """
    Deploy paxpar API
    """
    ctx_obj: PaxparCLI_ObjCtx = ctx.obj

    #assert target == "arundo_cluster"

    # version = "4.2.37"
    if version is None:
        version = version_get(ctx_obj)
        if ctx_obj.verbose:
            print(f"No version specified, assuming {version}")

    if namespace is None:
        namespace = f"pp-dev-{version}".replace(".", "-")
        if ctx_obj.verbose:
            print(f"No namespace specified, assuming {namespace}")

    # from infra/paxpar-front-builder/back-release.yaml

    # only needed for test
    # DEPLOY_INGRESS_HOST = "api.dev.paxpar.io"

    # set kubernetes context to the right cluster
    # example:  kubectl config use-context arundo-tech/paxpar-gitops:paxpar-clust1
    call(
        f"""kubectl config use-context {k8s_context}""",
        ctx_obj=ctx_obj,
    )

    # TODO: also add issuers ressources here ?
    # add the gitlab helm repo
    call(
        f"""
        helm repo add \
            --username cicd \
            --password {ci_job_token} \
            repo{deploy_gitlab_project_id} \
            https://gitlab.com/api/v4/projects/{deploy_gitlab_project_id}/packages/helm/stable    
        """,
        ctx_obj=ctx_obj,
        check=False, # if repo already exists
    )
    # - helm repo update
    # - helm search repo ${DEPLOY_HELM_CHART_NAME}

    # build PP_CONF section:
    # --set PP_CONF_1={PP_CONF_1} \
    # --set PP_CONF_2={PP_CONF_2} \
    # --set PP_CONF_3={PP_CONF_3} \
    conf_files = [
                    conf_file1 or "",
                    conf_file2 or "",
                    conf_file3 or "",
                    *conf_file,
                ]
    pp_conf_n = " ".join(
        [
            rf'''--set PP_CONF_{i + 1}="{c}"'''.strip() if len(c) > 0 else r" "
            for i, c in enumerate(conf_files)
        ]
    )

    # helm_values_file section:
    #  -f values_overridden.yaml \
    #  -f values_overridden2.yaml \
    #TODO: add pp_conf_n as first helm_falues_file
    with tempfile.NamedTemporaryFile(mode="tw", suffix=".yaml", delete=False) as f:
        conf_payload = get_conf_payload(
            conf_files = conf_files,
            use_envvars=True,
        )
        f.write(yaml.dump(conf_payload, indent=2))
        f.flush()


        helm_values_file.insert(0, f.name)

        helm_values_file_n = " ".join([rf"-f {c}".strip() for c in helm_values_file])

        # helm_values section:
        #  --set GIT_CHECKOUT={GIT_CHECKOUT} \
        #  --set GIT_REPO={GIT_REPO} \
        #  --set GIT_BRANCH={GIT_BRANCH} \
        #  --set GIT_TOKEN={GIT_TOKEN} \
        helm_values_n = " ".join([rf"--set {c}".strip() for c in helm_values])

        # install the given chart version
        call(
            f'''
            helm upgrade \
            {deploy_helm_chart_name} \
            packages/pp-api/deploy/paxpar/ \
            --dry-run \
            --version {version} \
            --install \
            -n {namespace} \
            --create-namespace \
            {helm_values_file_n} \
            {helm_values_n} \
            {pp_conf_n} \
            ''',
            #repo{deploy_gitlab_project_id}/{deploy_helm_chart_name}
            ctx_obj=ctx_obj,
        )

    registries_credentials_create(
        namespace,
        ctx_obj,
    )

    # Create certmanager issuer
    ###TODO

    if ctx_obj.verbose:
        # some final info
        call(
            f"""kubectl get pods -n {namespace}""",
            ctx_obj=ctx_obj,
        )
        call(
            f"""helm list -n {namespace}""",
            ctx_obj=ctx_obj,
        )

    print(
        f"app {deploy_helm_chart_name} version {version} deployed on cluster/namespace {k8s_context}/{namespace}."
    )

    # backup image and upload to package registry
    # <!> microk8s n'est pas dans alpinelinux...
    # - microk8s ctr images export core_${DEPLOY_VERSION_RELEASE}.tar registry.gitlab.com/arundo-tech/paxpar/core:v${DEPLOY_VERSION_RELEASE}
    # - |
    #  curl \
    #    --header "JOB-TOKEN: $CI_JOB_TOKEN" \
    #    --upload-file ./core_${DEPLOY_VERSION_RELEASE}.tar \
    #    "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/packages/generic/api_package/${VERSION_RELEASE}/paxparcore.tar"


def registry_credentials_create(
    secret_name: str,
    server: str,
    namespace: str,
    token: str,
    ctx_obj: PaxparCLI_ObjCtx,
):
    """
    Create a k8s secret for the given registry
    """
    # delete first to avoid an error
    call(
        f"""
        kubectl delete secret {secret_name} \
            -n {namespace} \
            --ignore-not-found
    """,
        ctx_obj=ctx_obj,
    )
    call(
        f"""
        kubectl create secret docker-registry {secret_name}  \
            -n {namespace} \
            --docker-server={server}  \
            --docker-username=deploy-user \
            --docker-password={token} \
            --docker-email=support@paxpar.tech    
    """,
        ctx_obj=ctx_obj,
    )


def registries_credentials_create(
    namespace: str,
    ctx_obj: PaxparCLI_ObjCtx,
):
    """
    Create k8s secrets for all registries
    """
    for registry_id in REGISTRIES:
        registry = REGISTRIES[registry_id]
        envv = f"{registry_id.upper()}_SECRET_KEY"
        secret = os.environ[envv]

        registry_credentials_create(
            secret_name = f"{registry_id}-registry-credentials",
            server = f"https://{registry['url']}",
            namespace = namespace,
            token = secret,
            ctx_obj = ctx_obj,
        )