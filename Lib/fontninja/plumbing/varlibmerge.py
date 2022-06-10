class VarlibMerge:
    """Merge binary files and a designspace file into a variable font"""

    @classmethod
    def setup_parser(cls, parser):
        parser.add_argument("--ttf-dir", metavar="TMPDIR", help="Location of")
        parser.add_argument("ds", metavar="DESIGNSPACE", help="Input DS file")
        parser.add_argument("output", metavar="TTF", help="Output TTF file")

    @classmethod
    def run(cls, args):
        from fontTools.varLib import MasterFinder, build
        import ufoLib2

        finder = MasterFinder(args.ttf_dir+"/{stem}.ttf")

        vf, _, _ = build(
            args.ds,
            finder,
            # exclude=args.exclude,
            # optimize=args.optimize
        )
        vf.save(args.output)

