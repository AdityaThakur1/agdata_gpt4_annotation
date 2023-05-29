#!/bin/bash
#SBATCH --nodes=1                        
#SBATCH --ntasks-per-node=1              
#SBATCH --cpus-per-task=8                
#SBATCH --time=20:00:00
#SBATCH --mem=16GB
#SBATCH --job-name=ag-data6
#SBATCH --output=run_2478.out


eval "$(conda shell.bash hook)"
conda activate /scratch/at4932/projects/nenv1
module purge
module load anaconda3/2020.07
pip install openai
pip install python-dotenv

time python annotation_script.py --startrow=2478 --endrow=3000 --csv_file='mapping_order.csv'