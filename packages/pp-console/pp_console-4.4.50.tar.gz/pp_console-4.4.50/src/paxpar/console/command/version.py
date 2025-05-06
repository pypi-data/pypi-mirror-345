import importlib.metadata

import toml
import typer
import yaml
from paxpar.cli.tools import (
    PaxparCLI_ObjCtx,
    call,
    call_text_output,
    root_command_callback,
)
from rich.console import Console

# the git branch that support the version
# any other branch are considered as *build* variant of the current version
main_git_branch = 'main'


console = Console()


def root_command(
    ctx: typer.Context,
):
    if ctx.obj.verbose:
        print(f'pyproject.toml : {pyproject_version_get("pyproject.toml")}')
        print(f'packages/pp-api/pyproject.toml : {pyproject_version_get("packages/pp-api/pyproject.toml")}')
        print(f'packages/pp-cli/pyproject.toml : {pyproject_version_get("packages/pp-cli/pyproject.toml")}')
        print(f'packages/pp-core/pyproject.toml : {pyproject_version_get("packages/pp-core/pyproject.toml")}')
        print(f'packages/pp-schema/pyproject.toml : {pyproject_version_get("packages/pp-schema/pyproject.toml")}')
        print(f'packages/pp-shared/pyproject.toml : {pyproject_version_get("packages/pp-shared/pyproject.toml")}')

    print(version_get(ctx.obj))


app = typer.Typer(
    help="Misc pp commands",
    invoke_without_command=True,
    callback=root_command_callback(root_command),
)



def version_get(
    ctx_obj: PaxparCLI_ObjCtx,        
):
    '''
    get current version
    '''
    # see https://semver.org/

    branch = call_text_output("git branch --show-current").strip()
    if branch == "":
        """
        When show currnt does not work (gitlab CI is in a detached mode), we locate branch name by hash:
        ❯ git branch --contains `git rev-parse HEAD`
        * (HEAD detached at 28163a689)
          3490-monorepo-api-widgets
        ❯ git branch --contains `git rev-parse HEAD`
         * 3490-monorepo-api-widgets        
        """
        branch = (
            call_text_output(
                "git branch -a --contains `git rev-parse HEAD`  | grep remotes/"
            )
            .strip()
            .split("/")[-1]
        )

    # see https://semver.org/
    # we use "-" pre-release char because "+" build char in not valid as a docker image tag
    build_prefix = f"-{branch}"if branch != main_git_branch else ""
    base_version = open("VERSION").read().strip()
    cli_version = importlib.metadata.version("paxpar.cli")
    version = f"{base_version}{build_prefix}"

    if ctx_obj.verbose:
        print(f'"{branch}" is the current git branch')
        print(f'"{build_prefix}" is the build prefix')
        print(f'"{base_version}" is the base VERSION')
        print(f'"{cli_version}" is the paxpar.cli version')
        print(f'"{version}" is the version')


    return version


def pyproject_version_get(target: str):
    """
    get version in a pyproject.toml file
    """
    data = toml.load(open(target))
    return data["project"]["version"]


def pyproject_version_set(
    target: str,
    version: str,
    ctx_obj: PaxparCLI_ObjCtx,
):
    """
    set version in a pyproject.toml file
    """
    try:
        data = toml.load(open(target))
        data["project"]["version"] = version
        if not ctx_obj.dry_run:
            toml.dump(data, open(target, "w"))
        if ctx_obj.verbose:
            print(target + " set to " + version)
    except Exception as e:
        print("Erreur pyproject_version")
        print(e)


def helm_version_set(
    target: str,
    version: str,
    ctx_obj: PaxparCLI_ObjCtx,
):
    """
    set version in a Helm Chart
    """
    # data = yaml.safe_load(open("deploy/paxpar/Chart.yaml"))
    data = yaml.safe_load(open(target))
    data["appVersion"] = version
    data["version"] = version
    if not ctx_obj.dry_run:
        yaml.safe_dump(data, open(target, "w"))
    if ctx_obj.verbose:
        print(f"{target} set to " + version)


@app.command()
def show(
    ctx: typer.Context,
):
    """Show current version (DEFAULT COMMAND)"""
    root_command(ctx)


@app.command()
def bump(
    ctx: typer.Context,
): ...


@app.command()
def set(
    ctx: typer.Context,
    version: str,
    tag: bool = True,
    publish: bool = False,
    version_file: bool = True,
    helm: bool = True,
    pyproject: bool = True,
):
    ctx_obj: PaxparCLI_ObjCtx = ctx.obj
    if ctx_obj.verbose:
        print(f"set-version to {version} ...")

    # set VERSION file
    if not ctx_obj.dry_run and version_file:
        open("VERSION", "w").write(version)
    if ctx_obj.verbose:
        print("VERSION set to " + version)

    if helm:
        # set helm chart version
        helm_version_set("packages/pp-api/deploy/paxpar/Chart.yaml", version, ctx_obj)

    if pyproject:
        # set pyproject.toml files
        # keep in sync with .releaserc.yaml
        pyproject_version_set("pyproject.toml", version, ctx_obj)
        pyproject_version_set("packages/pp-api/pyproject.toml", version, ctx_obj)
        pyproject_version_set("packages/pp-cli/pyproject.toml", version, ctx_obj)
        pyproject_version_set("packages/pp-core/pyproject.toml", version, ctx_obj)
        pyproject_version_set("packages/pp-schema/pyproject.toml", version, ctx_obj)
        pyproject_version_set("packages/pp-shared/pyproject.toml", version, ctx_obj)


    if tag and not ctx_obj.dry_run:
        call(f'''
            git commit -am "manual version {version}"
            git tag -a v{version} -m "fix: manual version set"            
            git status
            ''',
            ctx_obj=ctx.obj,
        )

    if publish and not ctx_obj.dry_run:
        call('''
            git push
            git push --follow-tags
            git status
            ''',
            ctx_obj=ctx.obj,
        )

    
    print("set-version done for " + version)
