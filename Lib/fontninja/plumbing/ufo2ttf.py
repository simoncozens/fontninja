class Ufo2Ttf:
    """Compile a UFO to a TTF file (no features)"""

    @classmethod
    def setup_parser(cls, parser):
        parser.add_argument(
            "--layer",
            help="Layer name",
        )
        parser.add_argument("input", metavar="INPUT", help="Input UFO file")
        parser.add_argument("output", metavar="OUTPUT", help="Output TTF file")

    @classmethod
    def run_python(cls, args):
        import ufoLib2
        from ufo2ft.util import _GlyphSet
        from ufo2ft import compileTTF_args, call_outline_compiler, init_kwargs

        ufo = ufoLib2.Font.open(args.input)
        glyphSet = _GlyphSet.from_layer(ufo, args.layer, copy=False)
        kwargs = init_kwargs(dict(), compileTTF_args)
        otf = call_outline_compiler(ufo, glyphSet, **kwargs)
        otf.save(args.output)

    @classmethod
    def run_rust(cls, args):
        import subprocess
        
        subprocess.run(["fonticulus", args.input, args.output], check=True)

    run = run_python
