"""

TODO: implement thi CI job to test newly deployed intance:

test:
  stage: test
  image:
    name: python:3.12
  before_script:
    - apt update && apt install -y git
    - python -m pip install --upgrade pip
    - pip install poetry poetry-plugin-export

  script:
    - git clone https://dummy:${GITLAB_TOKEN_REGISTRY_READ}@gitlab.com/arundo-tech/pp-test.git
    - cd pp-test/console
    - poetry export -f requirements.txt --output requirements.txt --without-hashes
    - pip install --no-cache-dir --upgrade -r requirements.txt
    #- export PP_TOKEN=${PP_TOKEN}
    - echo ${PP_TOKEN}
    - rm data/multi*
    - rm data/val*
    # wait for deployed release for 10mn and test
    - |
      python3 ./perf_pp_api.py check \
          --endpoint https://${DEPLOY_INGRESS_HOST} \
          --wait-version ${DEPLOY_VERSION_RELEASE} \
          --timeout-version 600
  #only:
  #  - develop


"""

import typer
from rich.console import Console
from paxpar.cli.tools import call, root_command_callback

console = Console()

app = typer.Typer(
    help="test related commands",
    callback=root_command_callback(),
)


# pp test core -m blackbox -v tests/
@app.command()
def report():
    # pytest --html=report.html --self-contained-html
    call(
        """poetry run python -m pytest \
            --rootdir . \
            -v \
            --html=tests/report.html \
            --self-contained-html \
            --junitxml=tests/report.xml \
            -m blackbox tests/
        """,
        pythonpath_set=False,
    )


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def core(ctx: typer.Context):
    """
        Test paxpar core service

        Based on this call made by vscode pytest integration :
        ./.venv/bin/python -m pytest --rootdir . --override-ini junit_family=xunit1 --junit-xml=/tmp/tmp-4387BOK7IHnW32PW.xml ./tests/api/test_core_check.py::test_check
    cwd: .

    """
    extra_args = " ".join(list(ctx.args))
    # poetry run pytest {extra_args}
    call(
        f"""poetry run python -m pytest --rootdir . {extra_args}""",
        pythonpath_set=False,
    )
