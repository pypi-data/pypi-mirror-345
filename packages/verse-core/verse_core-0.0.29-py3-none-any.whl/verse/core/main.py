import argparse
import asyncio
from typing import Any

from ._arg_parser import ArgParser
from ._loader import Loader
from .manifest import MANIFEST_FILE
from .spec import SpecBuilder


def run(
    path: str,
    manifest: str,
    handle: str | None,
    tag: str | None,
    statement: str | None,
) -> Any:
    """
    Verse Run
    """
    loader = Loader(path=path, manifest=manifest)
    component_name = loader.get_component_name(handle=handle)
    component = loader.load_component(handle=handle, tag=tag)
    operation = None
    if statement is not None:
        operation = ArgParser.convert_execute_operation(statement, None)
    return component.__run__(
        operation=operation,
        path=path,
        manifest=manifest,
        handle=handle,
        tag=tag,
        component_name=component_name,
    )


async def arun(
    path: str,
    manifest: str,
    handle: str | None,
    tag: str | None,
    statement: str | None,
) -> Any:
    """
    Verse Run Async
    """
    loader = Loader(path=path, manifest=manifest)
    component_name = loader.get_component_name(handle=handle)
    component = loader.load_component(handle=handle, tag=tag)
    operation = None
    if statement is not None:
        operation = ArgParser.convert_execute_operation(statement, None)
    return await component.__arun__(
        operation=operation,
        path=path,
        manifest=manifest,
        handle=handle,
        tag=tag,
        component_name=component_name,
    )


def requirements(
    path: str,
    manifest: str,
    handle: str | None,
    tag: str | None,
    out: str | None,
):
    """
    Verse Requirements
    """
    loader = Loader(path=path, manifest=manifest)
    requirements = loader.generate_requirements(
        handle=handle, tag=tag, out=out
    )
    return requirements


def spec(
    path: str,
    manifest: str,
    component_or_handle: str,
):
    """
    Verse Spec
    """
    spec_builder = SpecBuilder(path=path)
    if "." in component_or_handle:
        component_name = component_or_handle
    else:
        component_name = Loader(
            path=path, manifest=manifest
        ).get_component_name(handle=component_or_handle)
    component_spec = spec_builder.build_component_spec(component_name)
    spec_builder.print(component_spec)


def main():
    parser = argparse.ArgumentParser(prog="verse", description="Verse CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Run the Verse application")
    arun_parser = subparsers.add_parser(
        "arun", help="Run the Verse application in async mode"
    )
    requirements_parser = subparsers.add_parser(
        "requirements", help="Generate the pip requirements"
    )
    spec_parser = subparsers.add_parser("spec", help="Get component spec")
    run_parser_arguments = [
        (
            "handle",
            str,
            None,
            "Root handle (optional positional argument)",
            "?",
        ),
        (
            "tag",
            str,
            None,
            "Provide tag (optional positional argument)",
            "?",
        ),
        ("--path", str, ".", "Project directory", None),
        ("--manifest", str, MANIFEST_FILE, "Manifest filename", None),
        ("--execute", str, None, "Operation to execute", None),
    ]
    requirements_parser_arguments = [
        (
            "handle",
            str,
            None,
            "Root handle (optional positional argument)",
            "?",
        ),
        (
            "tag",
            str,
            None,
            "Provide tag (optional positional argument)",
            "?",
        ),
        ("--path", str, ".", "Project directory", None),
        ("--manifest", str, MANIFEST_FILE, "Manifest filename", None),
        ("--out", str, None, "Output path", None),
    ]
    spec_parser_arguments = [
        ("component_or_handle", str, None, "Component name or handle", "?"),
        ("--path", str, ".", "Project directory", None),
        ("--manifest", str, MANIFEST_FILE, "Manifest filename", None),
    ]
    for arg in run_parser_arguments:
        run_parser.add_argument(
            arg[0], type=arg[1], default=arg[2], help=arg[3], nargs=arg[4]
        )
        arun_parser.add_argument(
            arg[0], type=arg[1], default=arg[2], help=arg[3], nargs=arg[4]
        )
    for arg in requirements_parser_arguments:
        requirements_parser.add_argument(
            arg[0], type=arg[1], default=arg[2], help=arg[3], nargs=arg[4]
        )
    for arg in spec_parser_arguments:
        spec_parser.add_argument(
            arg[0], type=arg[1], default=arg[2], help=arg[3], nargs=arg[4]
        )

    args = parser.parse_args()
    if args.command == "run":
        response = run(
            path=args.path,
            manifest=args.manifest,
            handle=args.handle,
            tag=args.tag,
            statement=args.execute,
        )
        print(response)
    elif args.command == "arun":
        response = asyncio.run(
            arun(
                path=args.path,
                manifest=args.manifest,
                handle=args.handle,
                tag=args.tag,
                statement=args.execute,
            )
        )
        print(response)
    elif args.command == "requirements":
        requirements(
            path=args.path,
            manifest=args.manifest,
            handle=args.handle,
            tag=args.tag,
            out=args.out,
        )
    elif args.command == "spec":
        spec(
            path=args.path,
            manifest=args.manifest,
            component_or_handle=args.component_or_handle,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
