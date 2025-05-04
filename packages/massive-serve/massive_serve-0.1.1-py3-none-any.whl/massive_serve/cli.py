import os
import sys
import subprocess
import click
from .data_utils import prepare_for_upload, prepare_after_download

@click.group()
def cli():
    """Massive Serve CLI"""
    pass

@cli.command()
@click.option('--chunk_size_gb', type=float, default=40, help='Maximum size of each chunk in GB')
def upload_data(chunk_size_gb):
    """Upload data to Hugging Face, automatically splitting large files"""
    # Set datastore path to `~` if it is not already set
    env = os.environ.copy()
    if 'DATASTORE_PATH' not in env:
        env['DATASTORE_PATH'] = '~'
    
    data_dir = os.path.join(os.path.expanduser(env['DATASTORE_PATH']), 'dpr_wiki_contriever')
    
    # Split large files if necessary
    split_files = prepare_for_upload(data_dir, chunk_size_gb)
    if split_files:
        print(f"Split {len(split_files)} files: {split_files}")
    
    # Upload to Hugging Face
    subprocess.run(['huggingface-cli', 'upload', 'rulins/massive_serve_dpr_wiki_contriever', data_dir, '--repo-type', 'dataset'])

@cli.command()
def dpr_wiki():
    """Run the DPR wiki worker node"""
    # Set PYTHONPATH to include the massive-serve directory
    env = os.environ.copy()
    massive_serve_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env['PYTHONPATH'] = massive_serve_dir
    
    # Set datastore path to `~` if it is not already set
    if 'DATASTORE_PATH' not in env:
        env['DATASTORE_PATH'] = '~'
    
    # Download the wiki index dataset
    save_path = os.path.join(os.path.expanduser(env['DATASTORE_PATH']), 'dpr_wiki_contriever')
    subprocess.run(['huggingface-cli', 'download', 'rulins/massive_serve_dpr_wiki_contriever', '--repo-type', 'dataset', '--local-dir', save_path])
    
    # Combine any split files
    print("Combining split files...")
    prepare_after_download(save_path)
    
    # Verify that the index file exists
    index_path = os.path.join(save_path, 'index', 'index_IVFFlat.100000.768.2048.faiss')
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Index file not found at {index_path} after combining split files")
    
    print("Starting DPR wiki server...")
    # Run the worker node script using absolute path
    api_script = os.path.join(massive_serve_dir, 'api', 'serve_dpr_wiki.py')
    subprocess.run(['python', api_script], env=env)

if __name__ == '__main__':
    cli() 