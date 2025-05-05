#!/bin/bash

#SBATCH --job-name=ollama_batch
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH -p lem-gpu
#SBATCH --gres=gpu:hopper:1
#SBATCH --mem=128G
#SBATCH --time=1:00:00

# Define model name
MODEL_NAME="llama3.2-vision:11b"

# Parse command line arguments
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <input_file>"
    exit 1
fi

# Define variables
INPUT_PATH="$HOME/$1"
INPUT_FILE="$TMPDIR/input_file.jsonl"
OUTPUT_FILE="$TMPDIR/output_file.jsonl"
LOG_FILE="$TMPDIR/log_file.log"

# Load necessary modules
source /usr/local/sbin/modules.sh
module load Python/3.12.3-GCCcore-13.3.0

# Prepare files
cp "$HOME/storage_space-hpc-marmys5267/scripts/ollama.py" "$TMPDIR"
cp "$HOME/storage_space-hpc-marmys5267/containers/ollama_latest.sif" "$TMPDIR"
cp "$INPUT_PATH" "$INPUT_FILE"
cd "$TMPDIR"

# Create virtual environment
python3 -m venv vllm-batch
source vllm-batch/bin/activate
pip install --upgrade pip
pip install openai

# Start Ollama in background inside Apptainer
apptainer instance start --nv ollama_latest.sif ollama-$SLURM_JOB_ID

apptainer exec instance://ollama-$SLURM_JOB_ID nohup ollama serve > /tmp/ollama-$SLURM_JOB_ID.log 2>&1 &

# Wait a few seconds to ensure Ollama server is up
sleep 10

apptainer exec instance://ollama-$SLURM_JOB_ID ollama pull "$MODEL_NAME"

# Run your inference script
python3 ollama.py "$INPUT_FILE" "$OUTPUT_FILE" "$LOG_FILE" --model "$MODEL_NAME"

# Copy results back to home directory
mkdir -p "$HOME/results/llama3.2-vision-11b-$SLURM_JOB_ID"
cp "$INPUT_FILE" "$HOME/results/llama3.2-vision-11b-$SLURM_JOB_ID/llama3.2-vision-11b_input.jsonl"
cp "$OUTPUT_FILE" "$HOME/results/llama3.2-vision-11b-$SLURM_JOB_ID/llama3.2-vision-11b_output.jsonl"
cp "$LOG_FILE" "$HOME/results/llama3.2-vision-11b-$SLURM_JOB_ID/llama3.2-vision-11b_log.log"
cp /tmp/ollama-$SLURM_JOB_ID.log "$HOME/results/llama3.2-vision-11b-$SLURM_JOB_ID/ollama.log"

# Deactivate virtual environment
deactivate

# Stop Ollama server
apptainer instance stop ollama-$SLURM_JOB_ID