class DecomposeMixed:
    """Convert decompose mixed component/contour glyphs within a UFO"""

    @classmethod
    def setup_parser(cls, parser):
        parser.add_argument(
            "--layer",
            help="Layer name",
        )
        parser.add_argument("input", metavar="INPUT", help="Input UFO file")
        parser.add_argument("output", metavar="OUTPUT", help="Output UFO file")

    @classmethod
    def run_python(cls, args):
        from ufo2ft.filters.decomposeComponents import DecomposeComponentsFilter
        import ufoLib2
        from ufo2ft.util import _GlyphSet

        ufo = ufoLib2.Font.open(args.input)
        filter = DecomposeComponentsFilter(include=lambda g: len(g))
        glyphSet = _GlyphSet.from_layer(ufo, args.layer, copy=False)
        filter(ufo, glyphSet)
        ufo.save(args.output)


    @classmethod
    def run_rust(cls, args):
        import subprocess

        subprocess.run(["ufo-decompose", args.input, args.output], check=True)

    run = run_python
