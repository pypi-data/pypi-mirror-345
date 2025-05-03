import sys

from pygeai.cli.commands import Command, Option, ArgumentsEnum
from pygeai.cli.commands.builders import build_help_text
from pygeai.cli.texts.help import MIGRATE_HELP_TEXT
from pygeai.core.common.exceptions import MissingRequirementException
from pygeai.migration.strategies import ProjectMigrationStrategy, AgentMigrationStrategy
from pygeai.migration.tools import MigrationTool


def show_help():
    """
    Displays help text in stdout
    """
    help_text = build_help_text(migrate_commands, MIGRATE_HELP_TEXT)
    sys.stdout.write(help_text)


def migrate_base(option_list: list):
    from_api_key = None
    from_instance = None
    to_api_key = None
    to_instance = None

    for option_flag, option_arg in option_list:
        if option_flag.name == "from_api_key":
            from_api_key = option_arg
        if option_flag.name == "from_instance":
            from_instance = option_arg
        if option_flag.name == "to_api_key":
            to_api_key = option_arg
        if option_flag.name == "to_instance":
            to_instance = option_arg

    if not (from_api_key and from_instance):
        raise MissingRequirementException("Cannot migrate resources without indicating source: API key and instance")

    return from_api_key, from_instance, to_api_key, to_instance


migrate_base_options = [
    Option(
        "from_api_key",
        ["--from-api-key", "--fak"],
        "API key for the source instance",
        True
    ),
    Option(
        "from_instance",
        ["--from-instance", "--fi"],
        "Source instance to migrate from",
        True
    ),
    Option(
        "to_api_key",
        ["--to-api-key", "--tak"],
        "API key for the destination instance",
        True
    ),
    Option(
        "to_instance",
        ["--to-instance", "--ti"],
        "Destination instance to migrate to",
        True
    ),
]


def clone_project(option_list: list):
    from_api_key = None
    from_project_id = None
    from_instance = None
    to_api_key = None
    to_project_name = None
    to_instance = None
    admin_email = None

    for option_flag, option_arg in option_list:
        if option_flag.name == "from_api_key":
            from_api_key = option_arg
        if option_flag.name == "from_project_id":
            from_project_id = option_arg
        if option_flag.name == "from_instance":
            from_instance = option_arg
        if option_flag.name == "to_api_key":
            to_api_key = option_arg
        if option_flag.name == "to_project_name":
            to_project_name = option_arg
        if option_flag.name == "to_instance":
            to_instance = option_arg
        if option_flag.name == "admin_email":
            admin_email = option_arg

    if not (from_project_id and from_instance):
        raise MissingRequirementException("Cannot migrate resources without indicating source: project and instance")

    if not admin_email:
        raise MissingRequirementException("Admin email for new project must be defined.")

    migration_strategy = ProjectMigrationStrategy(
        from_api_key=from_api_key,
        from_project_id=from_project_id,
        from_instance=from_instance,
        to_api_key=to_api_key,
        to_project_name=to_project_name,
        to_instance=to_instance,
        admin_email=admin_email
    )
    tool = MigrationTool(migration_strategy)
    response = tool.run_migration()

    sys.stdout.write(f"Migration result: \n{response}\n")


clone_project_options = [
    Option(
        "from_api_key",
        ["--from-api-key", "--fak"],
        "API key for the source instance",
        True
    ),
    Option(
        "from_project_id",
        ["--from-project-id", "--fpid"],
        "ID of the source project to migrate from",
        True
    ),
    Option(
        "from_instance",
        ["--from-instance", "--fi"],
        "URL from the source instance to migrate from",
        True
    ),
    Option(
        "to_api_key",
        ["--to-api-key", "--tak"],
        "API key for the destination instance. If not specified, the same instance's API key will be used",
        True
    ),
    Option(
        "to_project_name",
        ["--to-project-name", "--tpn"],
        "Name of the destination project to migrate to",
        True
    ),
    Option(
        "to_instance",
        ["--to-instance", "--ti"],
        "URL from the destination instance to migrate to. If not specified, the same instance's URL will be used",
        True
    ),
    Option(
        "admin_email",
        ["--admin-email", "--ae"],
        "Email from destination project's administrator",
        True
    ),
]


def clone_agent(option_list: list):
    from_api_key = None
    from_project_id = None
    from_instance = None
    to_api_key = None
    to_project_id = None
    to_instance = None
    agent_id = None

    for option_flag, option_arg in option_list:
        if option_flag.name == "from_api_key":
            from_api_key = option_arg
        if option_flag.name == "from_project_id":
            from_project_id = option_arg
        if option_flag.name == "from_instance":
            from_instance = option_arg
        if option_flag.name == "to_api_key":
            to_api_key = option_arg
        if option_flag.name == "to_project_id":
            to_project_id = option_arg
        if option_flag.name == "to_instance":
            to_instance = option_arg
        if option_flag.name == "agent_id":
            agent_id = option_arg

    if not (from_project_id and from_instance and agent_id):
        raise MissingRequirementException("Cannot migrate resources without indicating source: project, instance and agent id")

    migration_strategy = AgentMigrationStrategy(
        from_api_key=from_api_key,
        from_project_id=from_project_id,
        from_instance=from_instance,
        to_api_key=to_api_key,
        to_project_id=to_project_id,
        to_instance=to_instance,
        agent_id=agent_id
    )
    tool = MigrationTool(migration_strategy)
    response = tool.run_migration()

    sys.stdout.write(f"Migration result: \n{response}\n")


clone_agent_options = [
    Option(
        "from_api_key",
        ["--from-api-key", "--fak"],
        "API key for the source instance",
        True
    ),
    Option(
        "from_project_id",
        ["--from-project-id", "--fpid"],
        "ID of the source project to migrate from",
        True
    ),
    Option(
        "from_instance",
        ["--from-instance", "--fi"],
        "URL from the source instance to migrate from",
        True
    ),
    Option(
        "to_api_key",
        ["--to-api-key", "--tak"],
        "API key for the destination instance. If not specified, the same instance's API key will be used",
        True
    ),
    Option(
        "to_project_id",
        ["--to-project-id", "--tpid"],
        "ID of the destination project to migrate to",
        True
    ),
    Option(
        "to_instance",
        ["--to-instance", "--ti"],
        "URL from the destination instance to migrate to. If not specified, the same instance's URL will be used",
        True
    ),
    Option(
        "agent_id",
        ["--agent-id", "--aid"],
        "Unique identifier from the agent to be migrated",
        True
    ),

]


migrate_commands = [
    Command(
        "help",
        ["help", "h"],
        "Display help text",
        show_help,
        ArgumentsEnum.NOT_AVAILABLE,
        [],
        []
    ),
    Command(
        "clone_project",
        ["clone-project"],
        "Clone project from instance",
        clone_project,
        ArgumentsEnum.REQUIRED,
        [],
        clone_project_options
    ),
    Command(
        "clone_agent",
        ["clone-agent"],
        "Clone agentt from instance",
        clone_agent,
        ArgumentsEnum.REQUIRED,
        [],
        clone_agent_options
    ),

]
