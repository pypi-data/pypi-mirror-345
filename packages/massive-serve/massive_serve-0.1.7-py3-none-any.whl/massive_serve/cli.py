import os
import sys
import subprocess
import click
from .data_utils import prepare_for_upload, prepare_after_download

@click.group()
def cli():
    """Massive Serve CLI"""
    pass

@cli.command(name='upload-data')
@click.option('--chunk_size_gb', type=float, default=40, help='Maximum size of each chunk in GB')
@click.option('--domain_name', type=str, default='dpr_wiki_contriever', help='Domain name')
def upload_data(chunk_size_gb, domain_name):
    """Upload data to Hugging Face, automatically splitting large files"""
    # Set datastore path to `~` if it is not already set
    env = os.environ.copy()
    if 'DATASTORE_PATH' not in env:
        env['DATASTORE_PATH'] = '~'
    
    data_dir = os.path.join(os.path.expanduser(env['DATASTORE_PATH']), domain_name)
    
    # Split large files if necessary
    split_files = prepare_for_upload(data_dir, chunk_size_gb)
    if split_files:
        print(f"Split {len(split_files)} files: {split_files}")
    
    # Upload to Hugging Face
    subprocess.run(['huggingface-cli', 'upload', f'rulins/massive_serve_{domain_name}', data_dir, '--repo-type', 'dataset'])

@cli.command(name='serve')
@click.option('--domain_name', type=str, default='dpr_wiki_contriever', help='Domain name')
def serve(domain_name):
    """Run the worker node"""
    # Set the domain name
    os.environ['MASSIVE_SERVE_DOMAIN_NAME'] = domain_name
    
    # Set datastore path to `~` if it is not already set
    env = os.environ.copy()
    if 'DATASTORE_PATH' not in env:
        env['DATASTORE_PATH'] = '~'
    
    # Add package root to PYTHONPATH
    package_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if package_root not in sys.path:
        sys.path.insert(0, package_root)
    
    # Download the wiki index dataset
    save_path = os.path.join(os.path.expanduser(env['DATASTORE_PATH']), domain_name)
    subprocess.run(['huggingface-cli', 'download', f'rulins/massive_serve_{domain_name}', '--repo-type', 'dataset', '--local-dir', save_path])
    
    # Combine any split files
    print("Combining split files...")
    prepare_after_download(save_path)
    
    # Verify that the index file exists
    index_path = os.path.join(save_path, 'index', 'index_IVFFlat.100000.768.2048.faiss')
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Index file not found at {index_path} after combining split files")
    
    print("Starting DPR wiki server...")
    # Run the worker node script
    from .api.serve import main as serve_main
    serve_main()

if __name__ == '__main__':
    cli() 