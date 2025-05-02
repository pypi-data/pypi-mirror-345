from prophecy_lineage_extractor.writer.xlxs_writer import XLSXWriter

def get_writer(fmt):
    if fmt == "excel":
        return XLSXWriter
