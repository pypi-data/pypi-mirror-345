from loguru import logger
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import app.rag.config as cfn
import app.rag.api as api
import app.rag.cli as cli

# Main parser
parser = ArgumentParser(
    formatter_class = ArgumentDefaultsHelpFormatter,
    description = """
        Pilot of On-Premise RAG.
    """,
    parents = [cfn.top_parser, cfn.common_parser],
    add_help = False,
)

# Command definitions
commands = {
    # name: help, description, function, extra_parsers
    "serve"  : ("Start the RAG server",     "Run a FastAPI-based RAG server",              api.serve,  []),
    "chat"   : ("Chat with the RAG system", "Run an interactive chat with the RAG system", cli.chat,   [cfn.chat_parser]),
    "train"  : ("Train the RAG system",     "Run a pipeline to train the RAG system",      cli.train,  []),
    "test"   : ("Test the RAG system",      "Run a pipeline to test the RAG system",       cli.test,   []),
    "doctor" : ("Diagnose the RAG system",  "Run a pipeline to diagnose the RAG system",   cli.doctor, [cfn.doctor_parser]),
}

# Add command parsers
subparsers = parser.add_subparsers(title="commands", dest="command")
for name, (help, description, _, extra_parsers) in commands.items():
    subparsers.add_parser(
        name = name,
        help = help,
        description = description,
        parents = [cfn.common_parser] + extra_parsers,
        add_help = False,
    )

def main():
    args = parser.parse_args()
    cfn.setup_logger(cfn.LOG_LEVEL, cfn.LOG_SAVE, cfn.LOG_DIR)
    logger.debug(f"Parsed arguments: {args}")

    if command_info := commands.get(args.command):
        func, extra_parsers = command_info[2], command_info[3]
        
        # Create parser options dict from extra_parsers
        extra_options = {}
        if extra_parsers:
            for parser_obj in extra_parsers:
                for action in parser_obj._actions:
                    if action.dest == 'help':
                        continue
                    if hasattr(args, action.dest) and getattr(args, action.dest) != action.default:
                        extra_options[action.dest] = getattr(args, action.dest)
        
        # Run the command with the extra parser options
        func(extra_options)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
