#!python
import argparse
import traceback

import sys

from kuhl_haus.canary.env import (
    DEFAULT_CANARY_INVOCATION_INTERVAL,
    DEFAULT_CANARY_INVOCATION_COUNT,
)

__author__ = "Tom Pounders"
__copyright__ = "Tom Pounders"
__license__ = "MIT"


def parse_args(args):
    parser = argparse.ArgumentParser(description="Kuhl Haus Canary")
    parser.add_argument(
        "-s", "--script",
        dest="script",
        help="Script to run"
    )
    parser.add_argument(
        "-d", "--delay",
        dest="delay",
        default=DEFAULT_CANARY_INVOCATION_INTERVAL,
        type=int,
        help="Amount of time to delay between calls, in seconds.  i.e., sleep between invocations."
    )
    parser.add_argument(
        "-c", "--count",
        dest="count",
        default=DEFAULT_CANARY_INVOCATION_COUNT,
        type=int,
        help="Stop invocation after this many calls. Use -1 to run indefinitely, which is the default."
    )

    return parser.parse_args(args)


def main(args):
    parsed_args = parse_args(args)
    from kuhl_haus.metrics.recorders.graphite_logger import GraphiteLogger, GraphiteLoggerOptions
    from kuhl_haus.metrics.env import (
        CARBON_CONFIG,
        LOG_LEVEL,
        METRIC_NAMESPACE,
        NAMESPACE_ROOT,
        THREAD_POOL_SIZE,
        POD_NAME,
    )
    graphite_logger = GraphiteLogger(GraphiteLoggerOptions(
        application_name='canary',
        log_level=LOG_LEVEL,
        carbon_config=CARBON_CONFIG,
        thread_pool_size=THREAD_POOL_SIZE,
        namespace_root=NAMESPACE_ROOT,
        metric_namespace=METRIC_NAMESPACE,
        pod_name=POD_NAME,
    ))

    try:
        from kuhl_haus.canary.handlers import script_handler
        script_handler(parsed_args.script)(
            recorder=graphite_logger,
            delay=parsed_args.delay,
            count=parsed_args.count,
        )
    except KeyboardInterrupt:
        graphite_logger.logger.info("Received interrupt, exiting")
    except Exception as e:
        graphite_logger.logger.error(
            f"Unhandled exception raised running script {parsed_args.script} ({repr(e)})\r\n"
            f"{traceback.format_exc()}"
        )


def run():
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`

    This function can be used as entry point to create console scripts with setuptools.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html

    # After installing your project with pip, users can also run your Python
    # modules as scripts via the ``-m`` flag, as defined in PEP 338::
    #
    #     python -m kuhl_haus.canary.app 42
    #
    run()
