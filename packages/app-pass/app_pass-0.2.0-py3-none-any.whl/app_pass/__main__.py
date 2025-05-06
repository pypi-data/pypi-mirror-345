import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Sequence

from rich.console import Console
from rich.text import Text

from ._app import OSXAPP
from ._commands import Command
from ._issues import Issue
from ._macho import sign_impl
from ._notarize import notarize_impl
from ._util import run_commands, serialize_to_sh


def configure_logging(verbose: int):
    verbosity = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
    logging.basicConfig(format="%(levelname)s:%(message)s", level=verbosity[verbose])


def print_summary(app: OSXAPP, issues: Sequence[Issue]):
    console = Console()
    text = Text()
    text.append(f"Summary for {app.root}\n", style="bold magenta")
    if not issues:
        text.append("Found no issues!", style="bold lime")
    else:
        text.append(
            text.assemble(
                ("Found ", ""),
                (f"{len(issues)} ", "bold red"),
                ("issues of which ", ""),
                (f"{len([issue for issue in issues if issue.fixable])} ", "bold green"),
                ("can be fixed.", ""),
            )
        )

    console.print(text)


def print_unfixable(app: OSXAPP, issues: Sequence[Issue]):
    console = Console()
    text = Text()
    for issue in issues:
        text.append(
            text.assemble(
                ("Could ", ""),
                (f"not ", "bold red"),
                ("fix issue: ", ""),
                (f"{issue.details}\n ", "red"),
            )
        )

    console.print(text)


def parse_args() -> Namespace:

    common_args = ArgumentParser(add_help=False)
    common_args.add_argument("-v", "--verbose", action="count", default=0)
    common_args.add_argument("--no-progress", action="store_true")
    common_args.add_argument("--dry-run", action="store_true")
    common_args.add_argument("app_bundle", type=Path)
    common_args.add_argument("--sh-output", type=Path)

    fix_args = ArgumentParser(add_help=False)
    fix_args.add_argument("--rc-path-delete", action="store_true")
    fix_args.add_argument("--force-update", action="store_true")

    sign_args = ArgumentParser(add_help=False)
    sign_args.add_argument("entitlement_file", type=Path)
    sign_args.add_argument("developer_id", type=str)

    notarize_args = ArgumentParser(add_help=False)
    notarize_args.add_argument("-v", "--verbose", action="count", default=0)
    notarize_args.add_argument("app_bundle", type=Path)
    notarize_args.add_argument("keychain_profile", type=str)
    notarize_args.add_argument("keychain", type=Path)
    notarize_args.add_argument("apple_id_email", type=str)
    notarize_args.add_argument("team_id", type=str)

    parser = ArgumentParser()

    subparsers = parser.add_subparsers(dest="action", help="subcommand")
    check = subparsers.add_parser("check", parents=[common_args], help="Same as fix with '--dry-run'")

    fix = subparsers.add_parser(
        "fix",
        parents=[common_args, fix_args],
        help="Fix common issues that prevent your .app bundle from being notarized.",
    )
    sign = subparsers.add_parser(
        "sign",
        parents=[common_args, sign_args],
        help="Deep signing of binaries contained in your .app bundle (also within .jar archives) in a way that they will pass notarization/gatekeeper.",
    )

    fixsign = subparsers.add_parser(
        "fixsign", parents=[common_args, sign_args, fix_args], help="Do 'fix' and 'sign' in one go."
    )

    notarize = subparsers.add_parser(
        "notarize",
        parents=[notarize_args],
        help=(
            "Compress, submit, wait for notarization to complete and staple your app. "
            "This command does not offer a .sh out file option. "
        ),
    )

    return parser.parse_args()


def check(app: OSXAPP):
    """Check if .app bundle is likely to pass MacOs Gatekeeper

    Check integrity of binaries:
      * no RC_PATH outside the app
      * all linked libraries can be reached within the app or
        in "/System/", "/usr/", "/Library/".

    Check all binaries are signed.
    """
    return fix(app)


def fix(app: OSXAPP, rc_path_delete: bool = False, force_update: bool = False, need_repack=True) -> list[Command]:
    """Fix issues in mach-o libraries .app bundle

    Remove paths that point outside the app.

    Args:
        rc_path_delete: delete rc_paths that point outside the app. Use with care

    """
    issues = app.check_macho_binaries(rc_path_delete=rc_path_delete)
    issues.extend(app.check_jar_binaries(force_update=force_update))
    print_summary(app, issues)

    unfixable = [issue for issue in issues if not issue.fixable]
    print_unfixable(app, unfixable)

    commands: list[Command] = []
    for issue in issues:
        if issue.fixable:
            assert issue.fix is not None
            commands.append(issue.fix)

    if need_repack:
        commands.extend(app.jar_repack)
    return commands


def sign(app: OSXAPP, entitlement_file: Path, developer_id: str) -> list[Command]:
    # For jars, we need to sign and repack before signing  all
    assert entitlement_file.exists(), entitlement_file
    commands: list[Command] = []
    for jar in app.jars:
        commands.extend(jar.sign(entitlement_file, developer_id))

    # need to repack before signing the rest of the app
    commands.extend(app.jar_repack)

    for binary in app.macho_binaries:
        commands.append(sign_impl(entitlement_file, developer_id, binary.path))

    commands.append(sign_impl(entitlement_file, developer_id, app.bundle_exe))
    commands.append(sign_impl(entitlement_file, developer_id, app.root))

    return commands


def fixsign(
    app: OSXAPP, entitlement_file: Path, developer_id: str, rc_path_delete: bool = False, force_update: bool = False
):
    commands = fix(app, rc_path_delete, force_update, need_repack=False)
    commands.extend(sign(app, entitlement_file, developer_id))

    return commands


def notarize(app_path: Path, keychain_profile: str, keychain: Path, apple_id_email: str, team_id: str) -> int:
    success = notarize_impl(app_path, keychain_profile, keychain, apple_id_email, team_id)
    return success


def main():
    args = parse_args()
    configure_logging(verbose=args.verbose)

    commands: list[Command] = []
    match args.action:
        case "notarize":
            return notarize(args.app_bundle, args.keychain_profile, args.keychain, args.apple_id_email, args.team_id)
        case "check" | "fix" | "sign" | "fixsign":
            app = OSXAPP.from_path(args.app_bundle, with_progress=not args.no_progress)
            commands.extend(app.jar_extract)
            match args.action:
                case "check":
                    # force dry_run to be true for now
                    args.dry_run = True
                    commands.extend(check(app))
                case "fix":
                    commands.extend(fix(app, args.rc_path_delete, args.force_update))
                case "sign":
                    commands.extend(sign(app, args.entitlement_file, args.developer_id))
                case "fixsign":
                    commands.extend(
                        fixsign(app, args.entitlement_file, args.developer_id, args.rc_path_delete, args.force_update)
                    )
        case _:
            raise ValueError(f"Unexpected action {args.action}")

    if args.sh_output:
        serialize_to_sh(commands, args.sh_output)

    if not args.dry_run:
        run_commands(commands)


if __name__ == "__main__":
    sys.exit(main())
