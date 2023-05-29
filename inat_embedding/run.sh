#!/bin/bash
#SBATCH --nodes=1                        
#SBATCH --ntasks-per-node=1              
#SBATCH --cpus-per-task=4                
#SBATCH --time=18:00:00
#SBATCH --mem=32GB
#SBATCH --job-name=inat-test
#SBATCH --gres=gpu:rtx8000:1
#SBATCH --output=inat_embed_all_val_rtx8000_1.out


eval "$(conda shell.bash hook)"
conda activate /scratch/at4932/projects/nenv1
module purge
module load anaconda3/2020.07
module load cuda/11.6.2    #if you need to use GPU
module load python/intel/3.8.6
module load openmpi/intel/4.0.5

time python inat_class.py