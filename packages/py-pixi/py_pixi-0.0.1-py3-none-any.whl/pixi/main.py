import os
import logging
import click
from . import static_analyzer
from . import __version__
from .logger import setup_logger
from .utils import clone_required
from .setup_llvm import SetupLLVM

here = os.path.abspath(os.path.dirname(__file__))
logger = None  # Will be initialized in cli function

@click.group()
@click.version_option(version=__version__)
@click.option('--enable-file-logging', is_flag=True, help='Enable logging to a file', default=False)
@click.option('--log-file', default=None, type=str, help='Custom log file path. Only used if file logging is enabled')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output (DEBUG level)', default=False)
def cli(enable_file_logging, log_file, verbose):
    """
    Pixi is a program analysis and custom instruction generation framework.
    """
    global logger
    logger = setup_logger('pixi', enable_file_logging, log_file)
    
    # Set console handler level based on verbose flag
    if verbose and logger.handlers:
        logger.handlers[0].setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

@cli.command()
@click.option('--cores', '-c', type=int, default=None, help='Number of CPU cores to use for parallel build')
def setup(cores):
    """
    Compiler and environment setup for the experiment.
    """
    # Clone required repositories
    clone_required()
    # Setup LLVM with specified number of cores (or auto-detect if not specified)
    setup_llvm_inst = SetupLLVM(llvm_dir="llvm", cores=cores)
    setup_llvm_inst.setup()

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for analysis results')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'csv']), default='text',
              help='Output format for analysis results')
@click.option('--detailed', '-d', is_flag=True, help='Generate detailed analysis report')
def run_analyzer(input_file, output, format, detailed):
    """
    Run the analyzer engine to generate useful statistics on the program.
    
    Analyzes the input file to identify potential areas for hardware acceleration
    and generates statistics about computation patterns.
    """
    analyzer = static_analyzer.StaticAnalyzer(input_file)
    analyzer.analyze()
    if detailed:
        logger.info("Generating detailed performance metrics...")

    logger.info("Analysis complete")

if __name__ == "__main__":
    cli()
