import ninja
from ninja.ninja_syntax import Writer
from fontninja.plumbing import setup_ninja_rules, commands
import tempfile
from pathlib import Path


class CommandRunner:
    def __init__(self, build_dir):
        self.writer = Writer(open("build.ninja", "w"))
        self.build_dir = build_dir
        setup_ninja_rules(self.writer)

    def run(self):
        self.writer.close()
        ninja._program("ninja", [])

    def outfile(self, infile, extension):
        return str(self.build_dir / (Path(infile).stem + extension))

    def __getattr__(self, command):
        command = command.replace("_", "-")

        def _runit(inputs, outputs, args=None):
            if not isinstance(inputs, list):
                inputs = [inputs]
            if command not in commands:
                raise ValueError(f"Unknown command {command}")
            self.writer.comment(commands[command].__doc__)
            self.writer.build(outputs, command, inputs)
            return outputs

        return _runit


def build_ttf(c, ufo_paths):
    for ufo in ufo_paths:
        final_ttf = Path(ufo).stem + ".ttf"

        feature_file = c.writefeatures(ufo, c.outfile(ufo, ".fea"))
        decomposed = c.decompose_mixed(ufo, c.outfile(ufo, ".decomposed.ufo"))
        # Flatten components
        # Remove overlaps
        cu2qu = c.cu2qu(decomposed, c.outfile(ufo, ".cu2qu.ufo"))
        base_ttf = c.ufo2ttf(cu2qu, c.outfile(ufo, ".base.ttf"))
        c.compile_features([base_ttf, feature_file], final_ttf)


def build_ttf_interpolatable(c, ufo_paths):
    decomposed = [c.outfile(ufo, ".decomposed.ufo") for ufo in ufo_paths]
    cu2qus = [c.outfile(ufo, ".cu2qu.ufo") for ufo in ufo_paths]
    c.cu2qu_interpolatable(decomposed, cu2qus)

    for ufo in ufo_paths:
        final_ttf = Path(ufo).stem + ".ttf"

        feature_file = c.writefeatures(ufo, c.outfile(ufo, ".fea"))
        decomposed = c.decompose_mixed(ufo, c.outfile(ufo, ".decomposed.ufo"))
        # Flatten components
        # Remove overlaps
        cu2qu = c.outfile(ufo, ".cu2qu.ufo")
        base_ttf = c.ufo2ttf(cu2qu, c.outfile(ufo, ".base.ttf"))
        c.compile_features([base_ttf, feature_file], final_ttf)


def run(parser):
    inputGroup = parser.add_argument_group(
        title="Input arguments (flags)",
        description="The following arguments are mutually exclusive (pick only one):",
    )
    xInputGroup = inputGroup.add_mutually_exclusive_group()
    xInputGroup.add_argument(
        "-u",
        "--ufo-paths",
        nargs="+",
        metavar="UFO",
        help="One or more paths to UFO files",
    )
    outputGroup = parser.add_argument_group(title="Output arguments")
    outputGroup.add_argument(
        "-o",
        "--output",
        nargs="+",
        default="ttf",
        metavar="FORMAT",
        help="Output font formats. Choose 1 or more from: %(choices)s. Default: otf, ttf. "
        "(No file paths).",
        choices=("ttf", "ttf-interpolatable"),
    )

    # TTF

    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = Path(tmpdirname)
        c = CommandRunner(temp_dir)
        if "ttf" in args.output:
            build_ttf(c, args.ufo_paths)
        elif "ttf-interpolatable" in args.output:
            build_ttf_interpolatable(c, args.ufo_paths)

        c.run()
