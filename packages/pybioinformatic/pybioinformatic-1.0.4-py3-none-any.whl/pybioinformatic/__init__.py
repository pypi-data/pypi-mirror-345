from pybioinformatic.bed import Bed
from pybioinformatic.biomatplotlib import generate_unique_colors
from pybioinformatic.biomysql import BioMySQL
from pybioinformatic.blast import Blast
from pybioinformatic.decompressing_file import ungz
from pybioinformatic.fasta import Fasta
from pybioinformatic.fastq import Fastq
from pybioinformatic.genotype import GenoType
from pybioinformatic.gff import Gff
from pybioinformatic.gtf import Gtf
from pybioinformatic.sequence import Sequence, Nucleotide, Protein, Reads
from pybioinformatic.show_info import Displayer
from pybioinformatic.task_manager import TaskManager
from pybioinformatic.timer import Timer
from pybioinformatic.util import FuncDict
from pybioinformatic.vcf import VCF

from pybioinformatic.NGS import (
    parse_sample_info,
    build_ref_index,
    GatkSNPCalling,
    RNASeqAnalyser,
    LncRNAPredictor,
    LncRNATargetPredictor,
    LncRNAClassification
)

from pybioinformatic.biopandas import (
    display_set,
    read_file_as_dataframe_from_stdin,
    read_in_gene_expression_as_dataframe,
    merge_duplicate_indexes,
    filter_by_min_value,
    get_FPKM,
    get_TPM,
    dfs_to_excel,
    dataframe_to_str,
    interval_stat
)

__version__ = '1.0.4'
__all__ = [
    'Bed',
    'Blast',
    'BioMySQL',
    'parse_sample_info',
    'build_ref_index',
    'GatkSNPCalling',
    'RNASeqAnalyser',
    'LncRNAPredictor',
    'LncRNATargetPredictor',
    'LncRNAClassification',
    'ungz',
    'Fasta',
    'Fastq',
    'GenoType',
    'Gff',
    'Gtf',
    'Sequence',
    'Nucleotide',
    'Protein',
    'Reads',
    'Displayer',
    'Timer',
    'TaskManager',
    'VCF',
    'FuncDict',
    'display_set',
    'read_file_as_dataframe_from_stdin',
    'read_in_gene_expression_as_dataframe',
    'merge_duplicate_indexes',
    'filter_by_min_value',
    'get_TPM',
    'get_FPKM',
    'dfs_to_excel',
    'dataframe_to_str',
    'interval_stat',
    'generate_unique_colors'
]
