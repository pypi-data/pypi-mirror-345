"""
Command-line interface for BARX.

This module provides the `barx` command-line tool for
running and compiling BARX programs.
"""

import argparse
import os
import sys
import logging
from typing import List, Optional

def compile_command(args):
    """
    Handler for the 'compile' command.
    
    Args:
        args: Command-line arguments
    """
    from .ir.parser import Lexer, Parser
    from .ir.optimizer import PassManager, ConstantFolding, OperatorFusion
    
    input_file = args.input_file
    output_file = args.output_file or input_file.replace('.py', '.bx')
    
    logging.info(f"Compiling {input_file} to {output_file}")
    
    # Read input file
    with open(input_file, 'r') as f:
        source = f.read()
        
    # For demonstration, we'll just create a simple bytecode file
    # In a real implementation, this would:
    # 1. Parse the source code
    # 2. Generate an IR
    # 3. Run optimization passes
    # 4. Generate bytecode
    
    # Write output file
    with open(output_file, 'w') as f:
        f.write(f"# BARX compiled bytecode\n")
        f.write(f"# Source: {input_file}\n")
        f.write(f"# Bytecode version: 1\n\n")
        f.write(f"# This is a placeholder for real bytecode\n")
        
    logging.info(f"Compilation complete: {output_file}")

def run_command(args):
    """
    Handler for the 'run' command.
    
    Args:
        args: Command-line arguments
    """
    input_file = args.input_file
    pure_mode = args.pure
    
    logging.info(f"Running {input_file} (pure mode: {pure_mode})")
    
    # Check if it's a Python file or a bytecode file
    if input_file.endswith('.py'):
        # For Python files, we can just execute them
        # with the appropriate environment setup
        
        # Add the current directory to the path
        sys.path.insert(0, os.getcwd())
        
        # Set a flag for pure mode if requested
        if pure_mode:
            os.environ['BARX_PURE'] = '1'
        else:
            os.environ.pop('BARX_PURE', None)
            
        # Execute the file
        with open(input_file, 'r') as f:
            code = compile(f.read(), input_file, 'exec')
            exec(code, {'__file__': input_file})
            
    elif input_file.endswith('.bx'):
        # For bytecode files, we would need to load and interpret them
        # This is a placeholder for a real bytecode interpreter
        logging.info(f"Running bytecode file: {input_file}")
        
        with open(input_file, 'r') as f:
            bytecode = f.read()
            
        if '# BARX compiled bytecode' not in bytecode:
            logging.error("Not a valid BARX bytecode file")
            sys.exit(1)
            
        logging.info("This is a placeholder for a real bytecode interpreter")
        
    else:
        logging.error(f"Unsupported file type: {input_file}")
        sys.exit(1)

def main(args: Optional[List[str]] = None):
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments (default: None, uses sys.argv)
    """
    parser = argparse.ArgumentParser(
        description="BARX - Fast CPU-only AI framework",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile a BARX program')
    compile_parser.add_argument('input_file', help='Input Python file')
    compile_parser.add_argument('-o', '--output', dest='output_file', help='Output bytecode file')
    compile_parser.add_argument('--emit', choices=['bytecode', 'ir'], default='bytecode',
                              help='Output format')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run a BARX program')
    run_parser.add_argument('input_file', help='Input Python or bytecode file')
    run_parser.add_argument('--pure', action='store_true', default=False,
                          help='Run in pure mode (no Python fallback)')
    
    # Parse arguments
    args = parser.parse_args(args)
    
    # Handle commands
    if args.command == 'compile':
        compile_command(args)
    elif args.command == 'run':
        run_command(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
