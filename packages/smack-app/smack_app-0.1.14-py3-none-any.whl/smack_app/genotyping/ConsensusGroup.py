from collections import namedtuple
import pysam
from utils.utils import UMI_Mode
from typing import Optional

DNA_LETTERS = ["A", "C", "G", "T", "N"]
DNA_BASES = ["A", "C", "G", "T"]

ReadPair = namedtuple("ReadPair", "read_name fwd_read rev_read")
ConsensusCallResult = namedtuple(
    "ConsensusCallResult", "encoding_vector rows quality_coverage_count"
)

DNA_LETTERS = ["A", "C", "G", "T", "N"]
DNA_BASES = ["A", "C", "G", "T"]


# Low-memory transformation of pysam AlignedSegment
class MinimalAlignedSegment:
    def __init__(
        self,
        aligned_segment_object: pysam.libcalignedsegment.AlignedSegment,
        mode: UMI_Mode,
        barcode_tag: str,
        umi_tag: Optional[str],
    ) -> None:

        self.is_reverse = aligned_segment_object.is_reverse

        if aligned_segment_object.has_tag(barcode_tag):
            self.barcode = aligned_segment_object.get_tag(barcode_tag)
        else:
            self.barcode = None

        if mode == UMI_Mode.UMI and aligned_segment_object.has_tag(umi_tag):
            self.umi = aligned_segment_object.get_tag(umi_tag)
        else:
            self.umi = None

        self.tlen = aligned_segment_object.tlen
        self.pos = aligned_segment_object.pos
        self.mapping_quality = aligned_segment_object.mapping_quality
        self.aligned_pairs = aligned_segment_object.get_aligned_pairs(
            matches_only=True, with_seq=False
        )
        self.query_qualities = aligned_segment_object.query_qualities
        self.seq = aligned_segment_object.seq


class ConsensusGroup:

    def __init__(self) -> None:
        self.readpairs = []
        self.key = None
        self.group_type = None

    def add_readpair(self, read: ReadPair) -> None:
        self.readpairs.append(read)
