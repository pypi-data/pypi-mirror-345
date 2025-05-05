from loguru import logger
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

import app.rag.config as cfn
import app.rag.api as api
import app.rag.cli as cli

# Command definitions
commands = {
    "serve"  : ("Start the RAG server",     "Run a FastAPI-based RAG server",              api.serve),
    "chat"   : ("Chat with the RAG system", "Run an interactive chat with the RAG system", cli.chat),
    "train"  : ("Train the RAG system",     "Run a pipeline to train the RAG system",      cli.train),
    "test"   : ("Test the RAG system",      "Run a pipeline to test the RAG system",       cli.test),
    "doctor" : ("Diagnose the RAG system",  "Run a pipeline to diagnose the RAG system",   cli.doctor),
}

# Main parser
parser = ArgumentParser(
    formatter_class = ArgumentDefaultsHelpFormatter,
    description = """
        Pilot of On-Premise RAG.
    """,
    parents = [cfn.top_parser, cfn.common_parser],
    add_help = False,
)

# Add command parsers
subparsers = parser.add_subparsers(title="commands", dest="command")
for name, (help, description, _) in commands.items():
    subparsers.add_parser(
        name = name,
        help = help,
        description = description,
        parents = [cfn.common_parser],
        add_help = False,
    )

def main():
    args = parser.parse_args()
    cfn.setup_logger(cfn.LOG_LEVEL, cfn.LOG_SAVE, cfn.LOG_DIR)
    logger.debug(f"Parsed arguments: {args}")

    if func := commands.get(args.command):
        func[-1]()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
