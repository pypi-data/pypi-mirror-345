"""
File: DNA_seq.py
Description: DNA-seq analysis pipeline module.
CreateDate: 2025/4/18
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Dict
from os import makedirs
from os.path import abspath
from shutil import which
from pybioinformatic.NGS.base import NGSAnalyser


class GatkSNPCalling(NGSAnalyser):
    def __init__(
            self,
            read1: str,
            read2: str,
            ref_genome: str,
            output_path: str,
            num_threads: int = 10,
            sample_name: str = None,
            exe_path_dict: Dict[str, str] = None
    ):
        super().__init__(read1, read2, ref_genome, output_path, num_threads, sample_name, exe_path_dict)
        self.variant_path = f'{self.output_path}/03.variant/{self.sample_name}'
        self.gvcf = f"{self.variant_path}/{self.bwa_mem_markdup_bam.split('/')[-1]}.gvcf"
        self.vcf = f"{self.variant_path}/{self.bwa_mem_markdup_bam.split('/')[-1]}.vcf"
        self.filtered_vcf = f"{self.variant_path}/{self.bwa_mem_markdup_bam.split('/')[-1]}.filtered.vcf"

    def run_HaplotypeCaller(
            self,
            bam_file: str = None,
            **other_options
    ) -> str:
        gatk = which(self.exe_path_dict['gatk'])
        makedirs(self.variant_path, exist_ok=True)
        if bam_file:
            bam_file = abspath(bam_file)
            out_gvcf = f"{self.variant_path}/{self.sample_name}{bam_file.split('/')[-1].replace(self.sample_name, '')}.gvcf"
        else:
            bam_file = self.bwa_mem_markdup_bam
            out_gvcf = self.gvcf
        cmd = (f'{gatk} HaplotypeCaller '
               f'-ERC GVCF '
               f'-I {bam_file} '
               f'-R {self.ref_genome} '
               f'-O {out_gvcf}')
        return self.other_options(cmd, other_options) if other_options else cmd

    def run_GenotypeGVCFs(
            self,
            gvcf_file: str = None,
            **other_options
    ) -> str:
        gatk = which(self.exe_path_dict['gatk'])
        makedirs(self.variant_path, exist_ok=True)
        if gvcf_file:
            gvcf_file = abspath(gvcf_file)
            out_vcf = f"{self.variant_path}/{self.sample_name}{gvcf_file.split('/')[-1].replace(self.sample_name, '').replace('gvcf', 'vcf')}"
        else:
            gvcf_file = self.gvcf
            out_vcf = self.vcf
        cmd = (
            f'{gatk} GenotypeGVCFs '
            f'-R {self.ref_genome} '
            f'-V {gvcf_file} '
            f'-O {out_vcf}'
        )
        return self.other_options(cmd, other_options) if other_options else cmd

    def run_VariantFiltration(
            self,
            filter_expression: str = 'QD < 2.0 || MQ < 40.0 || FS > 60.0 || SOR > 3.0',
            vcf_file: str = None,
            **other_options
    ) -> str:
        gatk = which(self.exe_path_dict['gatk'])
        makedirs(self.variant_path, exist_ok=True)
        if vcf_file:
            vcf_file = abspath(vcf_file)
            out_vcf = f"{self.variant_path}/{self.sample_name}{vcf_file.split('/')[-1].replace(self.sample_name, '').replace('vcf', 'filtered.vcf')}"
        else:
            vcf_file = self.vcf
            out_vcf = self.filtered_vcf
        cmd = (
            f'{gatk} VariantFiltration '
            f'--filter-name  "HARD_TO_VALIDATE" '
            f'--filter-expression "{filter_expression}" '
            f'-R {self.ref_genome} '
            f'-V {vcf_file} '
            f'-O {out_vcf}'
        )
        return self.other_options(cmd, other_options) if other_options else cmd

    def pipeline(self) -> str:
        cmds = (
            f'{self.run_fastp()}\n\n'
            f'{self.run_bwa_mem()}\n\n'
            f'{self.filter_reads_by_mapQ()}\n\n'
            f'{self.mark_duplicates()}\n\n'
            f'{self.stats_depth()}\n\n'
            f'{self.run_HaplotypeCaller()}\n\n'
            f'{self.run_GenotypeGVCFs()}\n\n'
            f'{self.run_VariantFiltration()}'
        )
        return cmds
