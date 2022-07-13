import ninja
from ninja.ninja_syntax import Writer
from fontninja.plumbing import setup_ninja_rules, commands
import tempfile
from pathlib import Path
from fontTools import designspaceLib
from fontmake.font_project import FontProject


class CommandRunner:
    def __init__(self, build_dir, rust=False):
        self.writer = Writer(open("build.ninja", "w"))
        self.build_dir = build_dir
        setup_ninja_rules(self.writer, rust=rust)

    def run(self):
        self.writer.close()
        ninja._program("ninja", [])

    def outfile(self, infile, extension):
        return str(self.build_dir / (Path(infile).stem + extension))

    def __getattr__(self, command):
        command = command.replace("_", "-")

        def _runit(inputs, outputs, args=None, implicit=None):
            variables = {}
            if args:
                variables["args"] = args
            if not isinstance(inputs, list):
                inputs = [inputs]
            if command not in commands:
                raise ValueError(f"Unknown command {command}")
            self.writer.comment(commands[command].__doc__)
            self.writer.build(
                outputs, command, inputs, variables=variables, implicit=implicit
            )
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


def build_ttf_interpolatable(c, ufo_paths, output_dir="."):
    decomposed = [c.outfile(ufo, ".decomposed.ufo") for ufo in ufo_paths]
    cu2qus = [c.outfile(ufo, ".cu2qu.ufo") for ufo in ufo_paths]
    c.cu2qu_interpolatable(decomposed, cu2qus)
    outputs = []

    for ufo in ufo_paths:
        final_ttf = str(Path(output_dir) / (Path(ufo).stem + ".ttf"))

        feature_file = c.writefeatures(ufo, c.outfile(ufo, ".fea"))
        decomposed = c.decompose_mixed(ufo, c.outfile(ufo, ".decomposed.ufo"))
        # Flatten components
        # Remove overlaps
        cu2qu = c.outfile(ufo, ".cu2qu.ufo")
        base_ttf = c.ufo2ttf(cu2qu, c.outfile(ufo, ".base.ttf"))
        c.compile_features([base_ttf, feature_file], final_ttf)
        outputs.append(final_ttf)
    return outputs


def build_variable_ttf(c, ds, ttfs):
    outfile = Path(ds).stem + "-VF.ttf"
    c.varlib_merge(ds, outfile, args=f'--ttf-dir "{c.build_dir}"', implicit=ttfs)


def run(parser):
    parser.add_argument(
        "--rust",
        action="store_true",
        help="Use Rust utilities where possible",
    )
    parser.add_argument(
        "--build-dir",
        metavar="DIRECTORY",
        help="Build directory for intermediate outputs",
    )
    inputGroup = parser.add_argument_group(
        title="Input arguments (flags)",
        description="The following arguments are mutually exclusive (pick only one):",
    )
    xInputGroup = inputGroup.add_mutually_exclusive_group()
    xInputGroup.add_argument(
        "-g", "--glyphs-path", metavar="GLYPHS", help="Path to .glyphs source file"
    )
    xInputGroup.add_argument(
        "-u",
        "--ufo-paths",
        nargs="+",
        metavar="UFO",
        help="One or more paths to UFO files",
    )
    xInputGroup.add_argument(
        "-m",
        "--mm-designspace",
        metavar="DESIGNSPACE",
        help="Path to .designspace file",
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
        choices=("ttf", "ttf-interpolatable", "variable"),
    )

    positionalInputs = parser.add_argument_group(
        title="Input arguments (positonal)",
        description="Alternatively, guess source format from filename extension",
    )
    positionalInputs.add_argument(
        "posargs",
        nargs="*",
        metavar="INPUTS",
        help="Either one *.designspace or *.glyphs file, or one or more *.ufo",
    )
    args = parser.parse_args()
    do_variable = "variable" in args.output

    for filename in args.posargs:
        if filename.endswith(".glyphs"):
            if args.glyphs_path:
                parser.error("Only one *.glyphs source file is allowed")
            args.glyphs_path = filename
        elif filename.endswith(".designspace"):
            if args.mm_designspace:
                parser.error("Only one *.designspace source file is allowed")
            args.mm_designspace = filename
        elif filename.endswith(".ufo"):
            args.ufo_paths.append(filename)
        else:
            parser.error(f"Unknown input file extension: '{filename}'")

    count = sum(bool(p) for p in (args.glyphs_path, args.ufo_paths, args.mm_designspace))
    if count == 0:
        parser.error("No input files specified")
    elif count > 1:
        parser.error(f"Expected 1, got {count} different types of inputs files")


    with tempfile.TemporaryDirectory() as tmpdirname:
        if args.build_dir:
            temp_dir = Path(args.build_dir)
        else:
            temp_dir = Path(tmpdirname)
        c = CommandRunner(temp_dir, rust=args.rust)
        if args.glyphs_path:
            args.mm_designspace = FontProject().build_master_ufos(args.glyphs_path)
        if args.mm_designspace:
            designspace_path = args.mm_designspace
            designspace = designspaceLib.DesignSpaceDocument.fromfile(designspace_path)
            args.ufo_paths = [source.path for source in designspace.sources]

        if "ttf-interpolatable" in args.output or do_variable:
            ttfs = build_ttf_interpolatable(c, args.ufo_paths, output_dir=temp_dir)
            if do_variable:
                build_variable_ttf(c, args.mm_designspace, ttfs)
        elif "ttf" in args.output:
            build_ttf(c, args.ufo_paths)
        c.run()
