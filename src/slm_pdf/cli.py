import argparse
import json
import logging
import sys

from slm_pdf.pipeline import Pipeline


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="SLM-PDF: Extract structured data from PDFs using a vision-language model"
    )
    parser.add_argument("path", help="Path to the PDF file")
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file path (default: stdout)",
        default=None,
    )
    parser.add_argument(
        "--model",
        default="qwen2.5-vl:3b",
        help="Ollama model name (default: qwen2.5-vl:3b)",
    )
    parser.add_argument(
        "--endpoint",
        default="http://localhost:11434",
        help="Ollama API endpoint (default: http://localhost:11434)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout in seconds per page (default: 120)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Render DPI (default: 300)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug-level logging",
    )
    parser.add_argument(
        "--log-file",
        help="Write logs to a file instead of stderr",
        default=None,
    )
    return parser.parse_args(argv)


def _setup_logging(verbose: bool, log_file: str | None) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    if log_file:
        logging.basicConfig(filename=log_file, level=level, format=fmt)
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(fmt))
        logging.basicConfig(level=level, handlers=[handler])
    logging.getLogger("httpx").setLevel(logging.WARNING)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    _setup_logging(args.verbose, args.log_file)

    pipeline = Pipeline(
        model=args.model,
        endpoint=args.endpoint,
        timeout=args.timeout,
        dpi=args.dpi,
    )
    result = pipeline.run(args.path)
    output = result.model_dump()

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(json.dumps(output, indent=2))
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
