class Cu2QuInterpolatable:
    """Convert curves from cubic to quadratic across multiple UFOs at once"""

    ninja_args = "$args --output $out -- $in"

    @classmethod
    def setup_parser(cls, parser):
        parser.add_argument(
            "--reverse-direction",
            help="Reverse curve direction",
            type=bool,
            default=False,
        )
        parser.add_argument(
            "--remember-curve-type", help="Store the curve type in a private lib key"
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument("--max-err", help="Maximum error in font units")
        group.add_argument(
            "--max-err-em", help="Maximum error in fractions of the em square"
        )

        parser.add_argument(
            "--output", metavar="OUTPUT", help="Output UFO files", nargs="+"
        )
        parser.add_argument("input", metavar="INPUT", help="Input UFO files", nargs="+")

    @classmethod
    def run_python(cls, args):
        from cu2qu.ufo import fonts_to_quadratic
        import ufoLib2

        assert len(args.input) == len(args.output)
        ufos = [ufoLib2.Font.open(ufo) for ufo in args.input]
        fonts_to_quadratic(
            ufos,
            max_err_em=args.max_err_em,
            max_err=args.max_err,
            reverse_direction=args.reverse_direction,
            remember_curve_type=args.remember_curve_type,
        )
        for outfile, ufo in zip(args.output, ufos):
            ufo.save(outfile)

    @classmethod
    def run_rust(cls, args):
        import subprocess

        subprocess.run(
            ["ufo-cu2qu", "--output"] + args.output + ["--"] + args.input, check=True
        )

    run = run_rust
