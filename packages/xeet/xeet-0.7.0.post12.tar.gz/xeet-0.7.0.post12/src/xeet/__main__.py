from xeet import xeet_version
from xeet.common import XeetException
from xeet.log import init_logging, log_error, log_info
from xeet.pr import *
from xeet.core.api import SchemaType
from xeet.core import TestsCriteria
from xeet.cli_printer import CliPrinterSummaryOpts, CliPrinterTestTimingOpts
import xeet.cli as actions

import os
import argparse
import argcomplete


_RUN_CMD = "run"
_LIST_CMD = "list"
_GROUPS_CMD = "groups"
_INFO_CMD = "info"
_DUMP_CMD = "dump"
_DUMP_TEST_CMD = "test"
_DUMP_SCHEMA_CMD = "schema"
_DUMP_CONFIG_CMD = "config"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog='xeet')
    parser.add_argument('--version', action='version', version=f'v{xeet_version}')
    parser.add_argument('--no-colors', action='store_true', default=False, help='disable colors')

    conf_file_parser = argparse.ArgumentParser(add_help=False)
    conf_file_parser.add_argument('-c', '--conf', metavar='CONF', help='configuration file to use')

    common_parser = argparse.ArgumentParser(add_help=False, parents=[conf_file_parser])
    common_parser.add_argument('-v', '--log-verbosity', action='count', help='log file verbosity',
                               default=0)
    common_parser.add_argument('--log-file', metavar='FILE', help='set log file', default=None)

    test_filter_parser = argparse.ArgumentParser(add_help=False)
    test_filter_parser.add_argument('-g', '--group', metavar='GROUP', default=[], action='append',
                                    help='run tests in this group')
    test_filter_parser.add_argument('-G', '--require-group', metavar='GROUP', default=[],
                                    action='append', help='require tests to be in this group')
    test_filter_parser.add_argument('-X', '--exclude-group', metavar='GROUP', default=[],
                                    action='append', help='exclude tests in this group')
    test_filter_parser.add_argument('-t', '--test', metavar='TEST', default=[], help='test name',
                                    action='append')
    test_filter_parser.add_argument('-T', '--exclude-test', metavar='TEST', default=[],
                                    help='test name exclusion', action='append')
    test_filter_parser.add_argument('-z', '--fuzzy-test', metavar='NAME', default=[],
                                    action='append', help='fuzzy test name')
    test_filter_parser.add_argument('-Z', '--fuzzy-exclude-test', metavar='NAME', default=[],
                                    action='append', help='fuzzy test name exclusion')

    subparsers = parser.add_subparsers(help='commands', dest='subparsers_name')
    subparsers.required = True

    run_parser = subparsers.add_parser(_RUN_CMD, help='run a test',
                                       parents=[common_parser, test_filter_parser])
    run_parser.add_argument('--debug', action='store_true', default=False,
                            help='run tests in debug mode')
    run_parser.add_argument('-r', '--repeat', metavar='COUNT', default=1, type=int,
                            help='repeat count')
    run_parser.add_argument('-V', '--variable', metavar='VAR', default=[], action='append',
                            help='set a variable')
    run_parser.add_argument('-j', '--jobs', metavar='NUMBER', nargs='?', default=1, type=int,
                            help='number of jobs to use')
    run_parser.add_argument('--randomize', action='store_true', default=False)
    output_type_grp = run_parser.add_mutually_exclusive_group()
    output_type_grp.add_argument('--concise', action='store_const',
                                 const=actions.RunVerbosity.Concise, help='concise output',
                                 dest='run_verbosity')
    output_type_grp.add_argument('--verbose', action='store_const',
                                 const=actions.RunVerbosity.Verbose, help='verbose output',
                                 dest='run_verbosity')
    output_type_grp.add_argument('--quiet', action='store_const',
                                 const=actions.RunVerbosity.Quiet, help='quiet output',
                                 dest='run_verbosity')
    run_parser.set_defaults(verbosity=actions.RunVerbosity.Default)
    summary_grp = run_parser.add_mutually_exclusive_group()
    summary_grp.add_argument('--summary-only', action='store_const', dest='summary_opt',
                             const=CliPrinterSummaryOpts.SummaryOnly, help='show summary only')
    summary_grp.add_argument('--no-summary', action='store_const', dest='summary_opt',
                             const=CliPrinterSummaryOpts.NoSummary, help='no summary')
    run_parser.set_defaults(summary_opt=CliPrinterSummaryOpts.Default)
    time_choices = [s.value for s in CliPrinterTestTimingOpts]
    run_parser.add_argument('--test-timing', choices=time_choices,
                            default=CliPrinterTestTimingOpts.NoTime.value, help='test timing')

    info_parser = subparsers.add_parser(_INFO_CMD, help='show test info', parents=[common_parser])
    info_parser.add_argument('-t', '--test-name', metavar='TEST', default=None,
                             help='set test name', required=True)
    info_parser.add_argument('-x', '--expand', help='expand values', action='store_true',
                             default=False)
    info_parser.add_argument('-f', '--full', help='full details', action='store_true',
                             default=False)

    list_parser = subparsers.add_parser(_LIST_CMD, help='list tests',
                                        parents=[common_parser, test_filter_parser])
    list_parser.add_argument('-a', '--all', action='store_true', default=False,
                             help='show hidden tests')
    list_parser.add_argument('--names-only', action='store_true', default=False,
                             help=argparse.SUPPRESS)

    subparsers.add_parser(_GROUPS_CMD, help='list groups', parents=[common_parser])

    dump_parser = subparsers.add_parser(_DUMP_CMD, help='dump a test descriptor')
    dump_subparsers = dump_parser.add_subparsers(help='dump commands', dest='dump_type')
    dump_subparsers.required = True
    dump_test_parser = dump_subparsers.add_parser(_DUMP_TEST_CMD, help='dump test descriptor',
                                                  parents=[conf_file_parser])
    dump_test_parser.add_argument("-t", "--test-name", help="test name", required=True)

    dump_schema_parser = dump_subparsers.add_parser(_DUMP_SCHEMA_CMD, help='dump schema')
    dump_schema_parser.add_argument('-t', '--type', choices=[s.value for s in SchemaType],
                                    default=SchemaType.CONFIG.value, help='schema type')

    dump_config_parser = dump_subparsers.add_parser(_DUMP_CONFIG_CMD, help='dump config',
                                                    parents=[conf_file_parser])
    dump_config_parser.add_argument('-p', '--path', help='dump path', default=None)

    argcomplete.autocomplete(parser, always_complete_options=False)
    args = parser.parse_args()
    if args.subparsers_name == _RUN_CMD:
        if args.test and (args.group or args.require_group or args.exclude_group):
            parser.error("test name and groups are mutually exclusive")
        if args.repeat < 1:
            parser.error("repeat count must be a psitive integer")
        if args.jobs is None:
            args.jobs = os.cpu_count()
            if args.jobs is None or args.jobs < 1:
                pr_warn("Cannot determine number of processors, using 1")
                args.jobs = 1
        elif args.jobs <= 0:
            parser.error("number of jobs must be a positive integer")
    return args


def _tests_criteria(args: argparse.Namespace, check_hidden: bool) -> TestsCriteria:
    return TestsCriteria(
        names=set(args.test),
        exclude_names=set(args.exclude_test),
        fuzzy_names=args.fuzzy_test,
        fuzzy_exclude_names=set(args.fuzzy_exclude_test),
        include_groups=set(args.group),
        require_groups=set(args.require_group),
        exclude_groups=set(args.exclude_group),
        hidden_tests=args.all if check_hidden else False)


def xrun() -> int:
    args = parse_arguments()
    if args.no_colors:
        disable_colors()

    try:
        cmd_name = args.subparsers_name
        if cmd_name == _DUMP_CMD:
            if args.dump_type == _DUMP_SCHEMA_CMD:
                actions.dump_schema(args.type)
            elif args.dump_type == _DUMP_TEST_CMD:
                actions.dump_test(args.conf, args.test_name)
            elif args.dump_type == _DUMP_CONFIG_CMD:
                actions.dump_config(args.conf, args.path)
            return 0
        if args.log_file:
            init_logging("Xeet", args.log_file, args.log_verbosity)
        log_info(f"running command '{args.subparsers_name}'")
        log_info(f"CWD is '{os.getcwd()}'")
        if cmd_name == _RUN_CMD:
            return actions.run_tests(args.conf, args.repeat, args.debug, args.randomize,
                                     _tests_criteria(args, False), args.jobs, args.run_verbosity,
                                     args.summary_opt, args.test_timing)
        if cmd_name == _LIST_CMD:
            actions.list_tests(args.conf, args.names_only, _tests_criteria(args, True))
        elif cmd_name == _GROUPS_CMD:
            actions.list_groups(args.conf)
        elif cmd_name == _INFO_CMD:
            actions.show_test_info(args.conf, args.test_name, args.expand, args.full)
        else:
            raise XeetException(f"Unknown command '{cmd_name}'")
        return 0

    except XeetException as e:
        # flush the stdout buffer
        log_error(f"xeet: {e}")
        return 255


if __name__ == "__main__":
    exit(xrun())
