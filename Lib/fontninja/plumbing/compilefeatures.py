class CompileFeatures:
    """Compile a feature file into a font file"""
    @classmethod
    def setup_parser(cls, parser):
        parser.add_argument("input", metavar="INPUT", help="Input TTF file")
        parser.add_argument("features", metavar="FEA", help="Input FEA file")
        parser.add_argument("output", metavar="OUTPUT", help="Output TTF file")

    @classmethod
    def run(cls, args):
        from fontTools.feaLib.builder import addOpenTypeFeatures
        from fontTools.ttLib import TTFont

        font = TTFont(args.input)
        addOpenTypeFeatures(font, args.features)
        font.save(args.output)
