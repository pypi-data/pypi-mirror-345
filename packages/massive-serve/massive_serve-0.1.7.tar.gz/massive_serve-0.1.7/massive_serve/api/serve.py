import os
import json
import traceback
import datetime
import hydra
import socket
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import queue
import time
import hydra
from omegaconf import OmegaConf
from hydra.core.global_hydra import GlobalHydra

from massive_serve.api.api_index import get_datastore

# ANSI color codes
CYAN = '\033[36m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
WHITE = '\033[37m'
RESET = '\033[0m'

class DPRWikiDatastore():
    def __init__(self, ):
        super().__init__()
        self.domain_name = 'dpr_wiki_contriever'
        self.query_encoder = 'facebook/contriever-msmarco'
        self.query_tokenizer = 'facebook/contriever-msmarco'
        self.data_root = os.environ.get('MASSIVE_SERVE_DATASTORE_PATH', '~')
        self.index_type = 'IVFFlat'
        self.per_gpu_batch_size = 128
        self.question_maxlength = 512
        self.nprobe = 128

class DemoDatastore():
    def __init__(self, ):
        super().__init__()
        self.domain_name = 'demo'
        self.query_encoder = 'facebook/contriever-msmarco'
        self.query_tokenizer = 'facebook/contriever-msmarco'
        self.data_root = os.environ.get('MASSIVE_SERVE_DATASTORE_PATH', '~')
        self.index_type = 'IVFFlat'
        self.per_gpu_batch_size = 128
        self.question_maxlength = 512
        self.nprobe = 128
        

datastore_cfg_map = {
    'dpr_wiki_contriever': DPRWikiDatastore(),
    'demo': DemoDatastore(),
}


datastore_domain_name = os.environ.get('MASSIVE_SERVE_DOMAIN_NAME', 'demo')
ds_cfg = datastore_cfg_map[datastore_domain_name]
        

app = Flask(__name__)
CORS(app)


class Item:
    def __init__(self, query=None, query_embed=None, domains=ds_cfg.domain_name, n_docs=1) -> None:
        self.query = query
        self.query_embed = query_embed
        self.domains = domains
        self.n_docs = n_docs
        self.searched_results = None
    
    def get_dict(self,):
        dict_item = {
            'query': self.query,
            'query_embed': self.query_embed,
            'domains': self.domains,
            'n_docs': self.n_docs,
            'searched_results': self.searched_results,
        }
        return dict_item


class SearchQueue:
    def __init__(self, log_queries=False):
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.current_search = None
        self.datastore = get_datastore(ds_cfg)

        self.log_queries = log_queries
        self.query_log = 'cached_queries.jsonl'
    
    def search(self, item):
        with self.lock:
            if self.current_search is None:
                self.current_search = item
                if self.log_queries:
                    now = datetime.datetime.now()
                    formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
                    with open(self.query_log, 'a+') as fin:
                        fin.write(json.dumps({'time': formatted_time, 'query': item.query})+'\n')
                results = self.datastore.search(item.query, item.n_docs)
                self.current_search = None
                return results
            else:
                future = threading.Event()
                self.queue.put((item, future))
                future.wait()
                return item.searched_results
    
    def process_queue(self):
        while True:
            item, future = self.queue.get()
            with self.lock:
                self.current_search = item
                item.searched_results = self.datastore.search(item)
                self.current_search = None
            future.set()
            self.queue.task_done()

search_queue = SearchQueue()
threading.Thread(target=search_queue.process_queue, daemon=True).start()

@app.route('/search', methods=['POST'])
def search():
    try:
        item = Item(
            query=request.json['query'],
            domains=request.json['domains'],
            n_docs=request.json['n_docs'],
        )
        # Perform the search synchronously with 60s timeout
        timer = threading.Timer(60.0, lambda: (_ for _ in ()).throw(TimeoutError('Search timed out after 60 seconds')))
        timer.start()
        try:
            results = search_queue.search(item)
            timer.cancel()
            print(results)
            return jsonify({
                "message": f"Search completed for '{item.query}' from {item.domains}",
                "query": item.query,
                "n_docs": item.n_docs,
                "results": results,
            }), 200
        except TimeoutError as e:
            timer.cancel()
            return jsonify({
                "message": str(e),
                "query": item.query,
                "error": "timeout"
            }), 408
    except Exception as e:
        tb_lines = traceback.format_exception(e.__class__, e, e.__traceback__)
        error_message = f"An error occurred: {str(e)}\n{''.join(tb_lines)}"
        return jsonify({"message": error_message}), 500

@app.route('/current_search')
def current_search():
    with search_queue.lock:
        current = search_queue.current_search
        if current:
            return jsonify({
                "current_search": current.query,
                "domains": current.domains,
                "n_docs": current.n_docs,
            }), 200
        else:
            return jsonify({"message": "No search currently in progress"}), 200

@app.route('/queue_size')
def queue_size():
    size = search_queue.queue.qsize()
    return jsonify({"queue_size": size}), 200

@app.route("/")
def home():
    return jsonify("Hello! What you are looking for?")


def find_free_port():
    with socket.socket() as s:
        s.bind(("", 0))  # Bind to a free port provided by the host.
        return s.getsockname()[1]  # Return the port number assigned.


def main():
    port = find_free_port()
    server_id = socket.gethostname()
    domain_name = ds_cfg.domain_name
    serve_info = {'server_id': server_id, 'port': port}
    endpoint = f'rulin@{server_id}:{port}/search'  # replace with your username
    
    # Create a beautiful banner
    banner = f"""
{CYAN}╔════════════════════════════════════════════════════════════╗
║{GREEN}                    MASSIVE SERVE SERVER                    {CYAN}║
╠════════════════════════════════════════════════════════════╣
║{YELLOW} Domain: {WHITE}{domain_name:<45}{CYAN}║
║{YELLOW} Server: {WHITE}{server_id:<45}{CYAN}║
║{YELLOW} Port:   {WHITE}{port:<45}{CYAN}║
║{YELLOW} Endpoint: {WHITE}{endpoint:<41}{CYAN}║
╚════════════════════════════════════════════════════════════╝{RESET}
"""
    print(banner)
    
    # Print test request with colors
    test_request = f"""
{GREEN}Test your server with this curl command:\n{RESET}
{CYAN}curl -X POST {endpoint} -H "Content-Type: application/json" -d '{YELLOW}{{"query": "Tell me more about the stories of Einstein.", "n_docs": 1, "domains": "{domain_name}"}}{CYAN}'{RESET}
"""
    print(test_request)
    
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()