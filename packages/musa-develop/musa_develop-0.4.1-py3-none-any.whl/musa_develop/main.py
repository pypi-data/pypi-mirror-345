import os
import sys
import argparse
from .check import CHECKER
from musa_develop.install import PACKAGE_MANAGER
from .report import report
from .utils import parse_args, demo_parse_args, FontBlue, get_os_name, FontRed
from .download import DOWNLOADER
from musa_develop.demo import DEMO
from musa_develop.demo.demo import DemoTask
from musa_develop import __version__ as VERSION

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
OPTIONAL_LENGTH = 11


class CustomHelpFormatter(argparse.HelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._indent_increment = 8  # 增加缩进层级
        self._max_help_position = 30  # 控制 `help` 对齐位置
        self._width = 100  # 设定更宽的列宽，避免换行问题


def main():
    parser = argparse.ArgumentParser(
        prog="musa-develop",
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
        description="A tool for deploying and checking the musa environment.",
    )
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help=f"{' '*OPTIONAL_LENGTH}Show this help message and exit.",
    )
    parser.add_argument(
        "-V",
        "--version",
        dest="version",
        action="store_true",
        help=f"{' '*OPTIONAL_LENGTH}Show the musa-develop version and exit.",
    )
    report_parser = parser.add_argument_group(FontBlue("Report"))
    report_parser.add_argument(
        "-r",
        "--report",
        dest="report",
        action="store_true",
        default=False,
        help=f"{' '*OPTIONAL_LENGTH}Display the software stack and hardware information of the current environment.",
    )

    check_parser = parser.add_argument_group(FontBlue("Check"))
    check_parser.add_argument(
        "-c",
        "--check",
        nargs="?",
        dest="check",
        metavar="PACKAGE_NAME",
        const="driver",
        default="",
        choices=[
            "host",
            "driver",
            "mtlink",
            "ib",
            "smartio",
            "container_toolkit",
            "torch_musa",
            "musa",
            "vllm",
            None,
        ],
        help=f"""{" "*OPTIONAL_LENGTH}Check musa-related develop environment. Default value is 'driver' if only '-c' or '--check' is set.
{" "*OPTIONAL_LENGTH}PACKAGE_NAME choices = [
                "host",
                "driver",
                "mtlink",
                "ib",
                "smartio",
                "container_toolkit",
                "musa",
                "torch_musa",
                "vllm"
            ]""",
    )
    check_parser.add_argument(
        "--container",
        dest="container",
        metavar="CONTAINER_NAME",
        type=str,
        default=None,
        help="(optional) Check the musa environment in the container while musa-develop tool is executing in the host.",
    )

    download_parser = parser.add_argument_group(FontBlue("Download"))
    download_parser.add_argument(
        "-d",
        "--download",
        dest="download",
        metavar="PACKAGE_NAME",
        type=parse_args,
        help=f"""{" "*OPTIONAL_LENGTH}Only download MUSA software stack offline packages; users need to install them manually.
           PACKAGE_NAME choices = [
                "kuae/kuae=1.3.0/kuae==1.3.0",
                "sdk/sdk=3.1.0/sdk==3.1.0",
                "musa",
                "mudnn",
                "mccl",
                "driver",
                "smartio",
                "container_toolkit",
                "torch_musa",
                "mutriton",
            ]
        """,
    )
    download_parser.add_argument(
        "--dir",
        type=str,
        help="""(optional) Specified software package download link. Need use it with --d""",
    )
    download_parser.add_argument(
        "--intranet",
        action="store_true",
        help=argparse.SUPPRESS,  # 隐藏，指定后可内网下载驱动
    )

    install_parser = parser.add_argument_group(FontBlue("Install"))
    install_parser.add_argument(
        "--auto-install",
        action="store_true",
        dest="auto_install",
        default=False,
        help="Select recommended options during the installation of lightdm and container_toolkit, and automatically reboot after driver installation completes.",
    )
    install_parser.add_argument(
        "-i",
        "--install",
        dest="install",
        metavar="PACKAGE_NAME",
        type=parse_args,
        # TODO(@wangkang): 是否需要kuae参数?, 如何处理?
        help=f"""{" "*OPTIONAL_LENGTH}Install the specified software based on the package name.
           PACKAGE_NAME choices = [
                "mudnn",
                "mccl",
                "driver",
                "musa"
                "container_toolkit",
                "torch_musa",
                "smartio",
                "host"
            ]
        """,
    )
    install_parser.add_argument(
        "-u",
        "--uninstall",
        metavar="PACKAGE_NAME",
        dest="uninstall",
        type=parse_args,
        help=f"""{" "*OPTIONAL_LENGTH}Uninstall the specified software based on the package name.
           PACKAGE_NAME choices = [
                "musa",
                "mudnn",
                "mccl",
                "driver",
                "smartio",
                "container_toolkit",
                "torch_musa",
                "vllm"
            ]
        """,
    )

    install_parser.add_argument(
        "--update",
        dest="update",
        metavar="PACKAGE_NAME",
        type=parse_args,
        choices=[
            ("driver", "3.1.0"),
            ("driver", "3.1.1"),
        ],
        help=f"""{" "*OPTIONAL_LENGTH}Update the driver to specified version(3.1.0 or 3.1.1). Example: --update driver=3.1.0""",
    )

    install_parser.add_argument(
        "-f",
        "--force",
        dest="allow_force_install",
        action="store_true",
        default=False,
        help="(optional) Force reinstallation by first uninstalling the existing package, then installing the specified version.",
    )

    install_parser.add_argument(
        "--path",
        type=str,
        help="""(optional) Install the specified offline package based on the path. Need use it with --i""",
    )

    # =====================demo=====================
    demo_parser = parser.add_argument_group(FontBlue("Demo"))
    demo_parser.add_argument(
        "--demo",
        dest="demo",
        type=demo_parse_args,
        help=f"""{" "*OPTIONAL_LENGTH}Run the built-in AI demo, specifying the product name, product version, and whether to run it inside a Docker container.
           DEMO choices = [
                "torch_musa==1.3.0/torch_musa--1.3.0",
                "torch_musa=1.3.0/torch_musa-1.3.0",
                "torch_musa==1.3.0==docker/torch_musa=1.3.0=docker",
                "torch_musa--1.3.0--docker/torch_musa-1.3.0-docker",
                "vllm==0.2.1/vllm--0.2.1",
                "vllm=0.2.1/vllm-0.2.1",
                "vllm==0.2.1==docker/vllm=0.2.1=docker",
                "vllm--0.2.1--docker/vllm-0.2.1-docker",
                "vllm_musa"
                "kuae==1.3.0/kuae--1.3.0",
                "kuae=1.3.0/kuae-1.3.0",
                "kuae==1.3.0==docker/kuea=1.3.0=docker",
                "kuae--1.3.0--docker/kuea-1.3.0-docker",
                "ollama==1.3.0/ollam=1.3.0",
                "ollama--1.3.0/ollam-1.3.0",
                "ollama==1.3.0==docker/ollam=1.3.0=docker",
                "ollama--1.3.0--docker/ollam-1.3.0-docker",
            ]
        """,
        # "torch_musa",
        # "torch_musa==docker/torch_musa--docker",
        # "torch_musa=docker/torch_musa-docker",
        # "vllm",
        # "vllm==docker/vllm=docker",
        # "vllm--docker/vllm-docker",
        # "kuae",
    )
    # Task Options
    task_options = DemoTask()
    demo_parser.add_argument(
        "-t",
        "--task",
        dest="task",
        type=str,
        default="base",
        # choices=task_options.get_all_task(),
        help=f"""(optional) Run a specified task.
{" "*OPTIONAL_LENGTH}TASK choices:
{" "*OPTIONAL_LENGTH}    {task_options.get_all_task()}""",
    )
    demo_parser.add_argument(
        "--image",
        dest="image",
        type=str,
        default="",
        help=argparse.SUPPRESS,  # 隐藏，指定镜像，需要手动确定镜像与当前驱动版本相匹配
    )

    # TODO(@gl): v0.3.0：need test
    demo_parser.add_argument(
        "--name",
        dest="name",
        type=str,
        default=None,
        help="(optional) Specify a name for container to run demo.",
    )
    demo_parser.add_argument(
        "-v",
        "--volume",
        dest="volume_list",
        metavar="<HOST_DIR>:<CTNR_DIR>",
        action="append",
        default=[],
        help="(optional) map a host directory to a container directory.",
    )
    demo_parser.add_argument(
        "-p",
        "--publish",
        dest="port_list",
        action="append",
        default=[],
        help="(optional) specify a port mapping. Format: host_port:container_port",
    )
    demo_parser.add_argument(
        "--network",
        "--net",
        dest="network",
        default="bridge",
        help="(optional) connect a container to a network",
    )
    demo_parser.add_argument(
        "--pid",
        dest="pid",
        default="",
        help="(optional) set the PID mode for the container.",
    )
    demo_parser.add_argument(
        "-w",
        "--workdir",
        dest="workdir",
        default="",
        help="(optional) set the working directory inside the container.",
    )

    demo_parser.add_argument(
        "--model",
        dest="model",
        default="",
        help="(optional) the original model path for vllm demo without weight conversion",
    )

    demo_parser.add_argument(
        "--converted-model",
        dest="converted_model",
        default="",
        help="(optional) the model path for vllm demo with weight conversion",
    )
    demo_parser.add_argument(
        "--tensor-parallel-size",
        "--tp-size",
        dest="tp_size",
        default="",
        help="(optional) number of partitions for tensor parallelism to distribute model computation across multiple devices(just for vllm demo).",
    )
    demo_parser.add_argument(
        "--webui",
        dest="webui",
        action="store_true",
        default=False,
        help="(optional) Enable a Web-based user interface for sending queries to the vLLM inference server(just for vllm demo).",
    )
    # 隐藏参数， 仅开发者内部结合 --demo vllm --task xxxx使用, 用于拉取tutorial_on_musa指定分支
    demo_parser.add_argument(
        "--git-branch",
        dest="branch",
        default="",
        help=argparse.SUPPRESS,
    )
    demo_parser.add_argument("--host", dest="host", type=str, help="Run demo on host.")
    # ===========================================

    # default with no args will print help
    if len(sys.argv) == 1:
        report()
        return

    args, unknown_args = parser.parse_known_args()

    if args.version:
        print(VERSION)
        return

    # ====================check===================
    if args.container and not args.check:
        parser.error("--container can only be used with -c/--check")
        return

    if args.check:
        checker = CHECKER[args.check](container_name=args.container)
        checker.check()
        checker.report()
        return

    # ====================report===================
    if args.report:
        report()
        return

    # ====================download===================
    if args.intranet:
        os.environ["DOWNLOAD_IN_HOST_TEST"] = "True"
    if args.download:
        download_name, download_version = args.download
        DOWNLOADER().download(download_name, download_version, args.dir)
        return

    # ====================install===================
    if args.install:
        install_name, install_version = args.install
        if get_os_name == "Kylin":
            PACKAGE_MANAGER["kylin"].install(install_name, install_version)
        if PACKAGE_MANAGER.get(install_name):
            PACKAGE_MANAGER.get(install_name).install(
                install_version,
                args.path,
                allow_force_install=args.allow_force_install,
                auto_install=args.auto_install,
            )
        else:
            print(
                FontRed(
                    f"Error: package manager for {install_name} not found. please run 'musa-develop -h' for help."
                )
            )
        return

    # =====================uninstall=====================
    if args.uninstall:
        uninstall_name, uninstall_version = args.uninstall
        if get_os_name == "Kylin":
            PACKAGE_MANAGER["kylin"].uninstall(uninstall_name)
        if PACKAGE_MANAGER.get(uninstall_name):
            PACKAGE_MANAGER.get(uninstall_name).uninstall()
        else:
            print(
                FontRed(
                    f"Error: package manager for {uninstall_name} not found. please run 'musa-develop -h' for help."
                )
            )
        return

    # ====================update===================
    if args.update:
        install_name, install_version = args.update
        PACKAGE_MANAGER[install_name].update(install_version, args.path)
        return

    # =====================demo=====================
    if not args.demo:
        if args.task or args.name or args.volume_list or args.port_list or args.host:
            parser.error(
                "The --demo option is required when using --task, -v/--volume, --name or --host."
            )
            return 1
    elif args.demo and args.host:
        if args.name or args.volume_list or args.port_list:
            parser.error(
                "The --host option is not required when using -v/--volume, -p/--publish, --name or --host."
            )
            return 1
    else:
        volume_list = []
        for volume_dirs in args.volume_list:
            if ":" not in volume_dirs:
                parser.error(
                    f"Invalid mount directory format: '{args.volume_list}'. Missing ':' separator. Expected format: HOST_DIR:CONTAINER_DIR"
                )
                return 1
            elif len(volume_dirs.split(":")) != 2:
                parser.error(
                    f"Invalid mount directory format: '{args.volume_list}'. Requiring two directory. Expected format: HOST_DIR:CONTAINER_DIR"
                )
                return 1
            else:
                volume_list.append(volume_dirs.split(":"))

        # port mapping
        port_list = [ports.rsplit(":", 1) for ports in args.port_list if ports]

        # task args check
        if not args.task:
            args.task = "base"
            print("Without specifying a task, start a container runs on MT-GPU. ")
        if "torch_musa" in args.demo and args.task not in task_options.get_all_task():
            parser.error(
                f"task '{args.task}' is invalid, choose from {task_options.get_all_task()}"
            )
        demo, version, _ = args.demo
        use_docker = True
        demo_class = DEMO.get(demo, None)
        if demo_class:
            demo_class.start(
                version,
                args.task,
                use_docker=use_docker,
                container_name=args.name,
                demo=demo,
                port_list=port_list,
                volume_list=volume_list,
                network=args.network,
                pid=args.pid,
                workdir=args.workdir,
                model=args.model,
                converted_model=args.converted_model,
                tp_size=args.tp_size,
                webui=args.webui,
                git_branch=args.branch,
                allow_force_install=args.allow_force_install,
                auto_install=args.auto_install,
                image=args.image,
            )
        else:
            parser.error(f"demo '{demo}' is invalid, choose from {DEMO.keys()}")
    # ============================================


if __name__ == "__main__":
    main()
