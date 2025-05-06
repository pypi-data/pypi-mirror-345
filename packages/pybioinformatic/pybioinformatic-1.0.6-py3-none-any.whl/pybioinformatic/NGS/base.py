#!/usr/bin/env python
"""
File: base.py
Description: Next-generation sequencing (NGS) data analysis module.
CreateDate: 2025/4/18
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from typing import Dict
from os import makedirs
from os.path import abspath
from shutil import which
from click import echo
from pybioinformatic import FuncDict


def parse_sample_info(sample_info: str) -> Dict[str, list]:
    d = {}  # {sample_name: [fastq_file1, fastq_file2, comparative_combination], ...}
    with open(sample_info) as f:
        for line in f:
            split = line.strip().split('\t')
            d[split[0]] = split[1:4]
    return d


def build_ref_index(
        fasta_file: str,
        bwa_exe: str = None,
        gatk_exe: str = None,
        samtools_exe: str = None,
        hisat2_build_exe: str = None,
        bowtie_build: str = None,
        bowtie2_build: str = None
) -> str:
    software_list = [
        which(i)
        for i in [bwa_exe, gatk_exe, samtools_exe, hisat2_build_exe, bowtie_build, bowtie2_build]
        if i is not None and which(i)
    ]
    if not software_list:
        echo('\033[33mWaring: No any valid executable file was specified, ignore building any index of fasta file.\033[0m', err=True)
        exit()
    fasta_file = abspath(fasta_file)
    cmd_dict = {
        'bwa': f' index {fasta_file} {fasta_file}',
        'gatk': f' CreateSequenceDictionary -R {fasta_file}',
        'samtools': f' faidx {fasta_file}',
        'hisat2-build': f' {fasta_file} {fasta_file}',
        'bowtie-build': f' {fasta_file} {fasta_file}',
        'bowtie2-build': f' {fasta_file} {fasta_file}',
    }
    try:
        cmd = '\n'.join(
            [
                i + cmd_dict[i.split('/')[-1]]
                for i in software_list
            ]
        )
    except KeyError as s:
        echo(f'\033[31mError: Invalid command {s}.\033[0m', err=True)
        exit()
    return cmd


class NGSAnalyser:
    """
    \033[32mNext-generation sequencing (NGS) data analysis pipeline.\033[0m

    \033[34m:param read1: Pair end read1 fastq file.\033[0m
    \033[34m:param read2: Pair end read2 fastq file.\033[0m
    \033[34m:param ref_genome: Reference genome fasta file.\033[0m
    \033[34m:param output_path: Output path.\033[0m
    \033[34m:param num_threads: Number of threads.\033[0m
    \033[34m:param sample_name: Sample name.\033[0m
    """

    _exe_set = {'fastp', 'bwa', 'samtools', 'hisat2', 'gatk', 'bowtie', 'bowtie2'}

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
        if exe_path_dict is None:
            exe_path_dict = {}
        ## Input file
        self.read1 = abspath(read1)
        self.read2 = abspath(read2)
        self.ref_genome = abspath(ref_genome)
        self.output_path = abspath(output_path)
        self.num_threads = num_threads
        self.sample_name = self.read1.split('/')[-1].split('.')[0] if sample_name is None else sample_name
        self.exe_path_dict = FuncDict(
            {
                k: which(v)
                for k, v in exe_path_dict.items()
                if k in self._exe_set and which(v) is not None
            }
        )
        ## Key output file
        # QC results file
        self.qc_path = f'{self.output_path}/01.QC/{self.sample_name}'
        self.read1_clean = f'{self.qc_path}/{self.sample_name}_1_clean.fq.gz'
        self.read2_clean = f'{self.qc_path}/{self.sample_name}_2_clean.fq.gz'
        self.fastp_json = f'{self.qc_path}/{self.sample_name}.fastp.json'
        self.fastp_html = f'{self.qc_path}/{self.sample_name}.fastp.html'
        # bwa mem results file
        self.mapping_path = f'{self.output_path}/02.mapping/{self.sample_name}'
        self.bwa_mem_raw_bam = f'{self.mapping_path}/{self.sample_name}.bwa.mem.sort.bam'
        self.bwa_mem_filtered_bam = f'{self.mapping_path}/{self.sample_name}.bwa.mem.sort.map30.bam'
        self.bwa_mem_markdup_bam = f'{self.mapping_path}/{self.sample_name}.bwa.mem.sort.map30.markdup.bam'
        # hisat2 results file
        self.hisat2_raw_bam = f'{self.mapping_path}/{self.sample_name}.ht2.sort.bam'

    @staticmethod
    def other_options(cmd: str, other_options: dict):
        other_options = ' '.join([f'{k} {v}' for k, v in other_options.items()])
        cmd += f' {other_options}'
        return cmd

    def run_fastp(
            self,
            read1_clean: str = None,
            read2_clean: str = None,
            **other_options
    ):
        fastp = which(self.exe_path_dict['fastp'])
        read1_clean = abspath(read1_clean) if read1_clean else self.read1_clean
        read2_clean = abspath(read2_clean) if read2_clean else self.read2_clean
        fastp_json = '/'.join(read1_clean.split('/')[:-1]) + f'/{self.sample_name}.fastp.json' if read1_clean else self.fastp_json
        fastp_html = '/'.join(read1_clean.split('/')[:-1]) + f'/{self.sample_name}.fastp.html' if read1_clean else self.fastp_html
        makedirs(self.qc_path, exist_ok=True)
        cmd = (
            f'{fastp} -w {self.num_threads} '
            f'-i {self.read1} -I {self.read2} '
            f'-o {read1_clean} '
            f'-O {read2_clean} '
            f'-j {fastp_json} '
            f'-h {fastp_html}'
        )
        return self.other_options(cmd, other_options) if other_options else cmd

    def run_hisat2(
            self,
            read1_clean: str = None,
            read2_clean: str = None,
            out_bam: str = None,
            **other_options
    ):
        hisat2 = which(self.exe_path_dict['hisat2'])
        samtools = which(self.exe_path_dict['samtools'])
        read1_clean = abspath(read1_clean) if read1_clean else self.read1_clean
        read2_clean = abspath(read2_clean) if read2_clean else self.read2_clean
        out_bam = abspath(out_bam) if out_bam else self.hisat2_raw_bam
        makedirs(self.mapping_path, exist_ok=True)
        hisat2_cmd = (
            f'{hisat2} -p {self.num_threads} '
            f'-x {self.ref_genome} '
            f'-1 {read1_clean} '
            f'-2 {read2_clean} '
            f'--summary-file  {self.mapping_path}/{self.sample_name}.ht2.log'
        )
        hisat2_cmd = self.other_options(hisat2_cmd, other_options) if other_options else hisat2_cmd
        cmd = f'{hisat2_cmd} | {samtools} sort -@ {self.num_threads} -T {self.sample_name} - -o {out_bam}'
        return cmd

    def run_bwa_mem(
            self,
            read1_clean: str = None,
            read2_clean: str = None,
            out_bam: str = None,
            **other_options
    ) -> str:
        bwa = which(self.exe_path_dict['bwa'])
        samtools = which(self.exe_path_dict['samtools'])
        read1_clean = abspath(read1_clean) if read1_clean else self.read1_clean
        read2_clean = abspath(read2_clean) if read2_clean else self.read2_clean
        out_bam = abspath(out_bam) if out_bam else self.bwa_mem_raw_bam
        makedirs(self.mapping_path, exist_ok=True)
        bwa_cmd = (
            fr'{bwa} mem -t {self.num_threads} '
            fr'-R "@RG\tID:{self.sample_name}\tSM:{self.sample_name}\tPL:ILLUMINA" '
            fr'{self.ref_genome} {read1_clean} {read2_clean}'
        )
        bwa_cmd = self.other_options(bwa_cmd, other_options) if other_options else bwa_cmd
        cmd = f'{bwa_cmd} | {samtools} sort -@ {self.num_threads} -T {self.sample_name} -o {out_bam}'
        return cmd

    def filter_reads_by_mapQ(self, bam_file: str = None, map_q: int = 30) -> str:
        if map_q not in range(1, 60):
            echo(f'\033[31mError: Invalid mapping Q value: "{map_q}". It must be an integer between 0 and 60.\033[0m', err=True)
            exit()
        samtools = which(self.exe_path_dict['samtools'])
        makedirs(self.mapping_path, exist_ok=True)
        if bam_file:
            bam_file = abspath(bam_file)
            out_bam = f"{self.mapping_path}/{self.sample_name}{bam_file.split('/')[-1].replace(self.sample_name, '').replace('bam', 'map30.bam')}"
        else:
            bam_file = self.bwa_mem_raw_bam
            out_bam = self.bwa_mem_filtered_bam
        awk = r'''awk '{if($1~/@/){print}else{if( $7 == "=" &&  $5 >= %s ){print $0}}}' ''' % map_q
        cmd = f'{samtools} view -h {bam_file} | {awk}| samtools view -bS -T {self.ref_genome} - -o {out_bam}'
        return cmd

    def mark_duplicates(
            self,
            bam_file: str = None,
            **other_options
    ) -> str:
        gatk = which(self.exe_path_dict['gatk'])
        samtools = which(self.exe_path_dict['samtools'])
        makedirs(self.mapping_path, exist_ok=True)
        if bam_file:
            bam_file = abspath(bam_file)
            out_bam = f"{self.mapping_path}/{self.sample_name}{bam_file.split('/')[-1].replace(self.sample_name, '').replace('bam', 'markdup.bam')}"
            out_metrics = f"{self.mapping_path}/{self.sample_name}{bam_file.split('/')[-1].replace(self.sample_name, '')}.metrics"
        else:
            bam_file = self.bwa_mem_filtered_bam
            out_bam = self.bwa_mem_markdup_bam
            out_metrics = f'{self.bwa_mem_markdup_bam}.metrics'
        cmd = (
            f'{gatk} MarkDuplicates '
            f'-I {bam_file} '
            f'-M {out_metrics} '
            f'-O {out_bam}'
        )
        cmd = self.other_options(cmd, other_options) if other_options else cmd
        cmd += f'\n{samtools} index {out_bam}'
        return cmd

    def stats_depth(self, bam_file: str = None, **other_options) -> str:
        samtools = which(self.exe_path_dict['samtools'])
        makedirs(self.mapping_path, exist_ok=True)
        if bam_file:
            bam_file = abspath(bam_file)
            out_file = f"{self.mapping_path}/{self.sample_name}{bam_file.split('/')[-1].replace(self.sample_name, '')}.depth"
        else:
            bam_file = self.bwa_mem_markdup_bam
            out_file = f"{self.bwa_mem_markdup_bam.split('/')[-1]}.depth"
        cmd = f'{samtools} depth {bam_file} -o {self.mapping_path}/{out_file}'
        return self.other_options(cmd, other_options) if other_options else cmd
