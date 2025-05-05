# Installation
WT_2 requires Python 3.10 environment. It is recommended to create a virtual environment using conda:


conda create --name WT2 python=3.10
conda activate WT2
pip install WT_2
Data Preparation
Each sample requires 10 raw MGF files
Place MGF files of the same sample in a folder named after the sample
Multiple samples should be placed in separate folders with distinct names
Refer to the format in test_data for data organization
Usage Guide
# 1. Peak Extraction
import os
from WT_2 import MultiprocessingManager

## Set parameters
sample_folder = "./test_datas/CRL_SIF_P_1" 
outer_max_workers = 1  # External parallelism
inner_max_workers = 8  # Internal parallelism
out_dir = "./out"      # Output directory

## Execute peak extraction
manager = MultiprocessingManager(
    outer_max_workers=outer_max_workers,
    inner_max_workers=inner_max_workers,
    mgf_folder=sample_folder,
    out_dir=out_dir
)
manager.process_mgf_files()
Parameter Description
RT_start=30: Retention time start value (seconds)
RT_end=720: Retention time end value (seconds)
fp_wid=6: Peak width parameter
fp_sigma=2: Peak sigma parameter
fp_min_noise=200: Minimum noise threshold
group_wid=6: Peak grouping width
group_sigma=0.5: Peak grouping sigma
Output
Automatically generates db and result folders under out_dir
# 2. Deduplication
from WT_2 import Deduplicator

## Set parameters
sample_name = os.path.basename(sample_folder)
msdial_path = "./test_datas/CRL_SIF_P_1/CRL_SIF_1_Q1_peak_df.csv"

## Execute deduplication
deduplicator = Deduplicator(
    peak_result_dir=os.path.join(out_dir, "result"),
    msdial_out_path=msdial_path,
    sample_name=sample_name,
    useHrMs1=False
)
deduplicator.remove_msdial_duplicate()
peak_outpath, group_outpath = deduplicator.filter_p3_group()
Parameter Description
useHrMs1=False: Whether to use high-resolution MS1 data
# 3. Qualitative Analysis
from WT_2 import MspGenerator, MspFileLibraryMatcher
import pandas as pd

## Generate MSP file
df = pd.read_csv(group_outpath)
out_msp_path = os.path.join(out_dir, "result", sample_name + ".msp")
msp_generator = MspGenerator(df, out_msp_path, useHrMs1=True)
msp_generator.generate()

## Library matching (requires MSP format library files)
library_matcher = MspFileLibraryMatcher(
    query_msp_path=out_msp_path,
    library_msp_path="./test_datas/library_msp",
    out_path="./test_datas/match_library_out.csv"
)
library_matcher.match()
Parameter Description
useHrMs1=False: Whether to use high-resolution MS1 data
Num=3: Number of matched results to retain
# 4. Quantitative Analysis
from WT_2 import SampleQuantity

## Set parameters
quantity_folder = "./path/to/samples/folder"  # Folder containing deduplication results of multiple samples

## Execute quantitative analysis
quantifier = SampleQuantity(
    quantity_folder=quantity_folder,
    ref_file=None,
    useHrMs1=True,
    uesSampleAligmentmodel=True,
    SampleAligmentmodel_path="../test_data/model/samplealigment.pth"
)
quantifier.quantity_processor()
Parameter Description
ref_file=None: Reference file path
useHrMs1=True: Whether to use high-resolution MS1 data
uesSampleAligmentmodel=True: Whether to use sample alignment model
SampleAligmentmodel_path: Path to sample alignment model
Notes
Peak extraction generates large temporary files - ensure sufficient disk space
Prepare input data according to test_data format before use
Library matching requires pre-prepared MSP format library files