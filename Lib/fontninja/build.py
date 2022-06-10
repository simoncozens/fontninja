import ninja
from ninja.ninja_syntax import Writer
from fontninja.plumbing import setup_ninja_rules
import tempfile
from pathlib import Path


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
        choices=("ttf",),
    )

    # TTF

    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = Path(tmpdirname)
        w = Writer(open("build.ninja", "w"))
        setup_ninja_rules(w)

        for ufo in args.ufo_paths:
            ufo = Path(ufo)

            w.comment("Make a full feature file")
            feature_file = temp_dir / (ufo.stem + ".fea")
            w.build(str(feature_file), "writefeatures", str(ufo))

            w.comment("Decompose mixed glyphs")
            decomposed = temp_dir / (ufo.stem + ".decomposed.ufo")
            w.build(str(decomposed), "decompose-mixed", str(ufo))

            # Flatten components
            # Remove overlaps

            w.comment("Convert cubic to quadratic")
            cu2qu = temp_dir / (ufo.stem + ".cu2qu.ufo")
            w.build(str(cu2qu), "cu2qu", str(decomposed))

            w.comment("Compile base TTF")
            basettf = temp_dir / (ufo.stem + ".base.ttf")
            w.build(str(basettf), "ufo2ttf", str(cu2qu))

            w.comment("Compile final TTF")
            final_ttf = ufo.stem + ".ttf"
            w.build(
                str(final_ttf), "compilefeatures", [str(basettf), str(feature_file)]
            )
            w.default(str(final_ttf))

            # Process glyph names

        w.close()
        ninja._program("ninja", [])
