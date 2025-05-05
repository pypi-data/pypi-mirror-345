import json
import os
import nbformat
from nbformat.reader import NotJSONError

class NotebookParser:
    def parse_notebook(self, notebook_path):
        try:
            try:
                notebook = nbformat.read(notebook_path, as_version=4)
                cells = []
                for i, cell in enumerate(notebook.cells):
                    if cell.cell_type == 'code' and cell.metadata.get('language', 'python') == 'python':
                        cells.append({
                            'cell_number': i + 1,
                            'content': cell.source,
                            'metadata': cell.metadata
                        })
                return cells

            except (NotJSONError, FileNotFoundError):
                with open(notebook_path, 'r', encoding='utf-8') as f:
                    notebook_data = json.load(f)
                cells = []
                for i, cell in enumerate(notebook_data.get('cells', [])):
                    if cell.get('cell_type') == 'code' and cell.get('metadata', {}).get('language', 'python') == 'python':
                        content = cell.get('source', '')
                        if isinstance(content, list):
                            content = ''.join(content)
                        cells.append({
                            'cell_number': i + 1,
                            'content': content,
                            'metadata': cell.get('metadata', {})
                        })
                return cells

        except Exception as e:
            raise ValueError(f"Error parsing notebook: {str(e)}")

    def get_current_notebook_path(self):
        try:
            import ipykernel
            import requests
            from jupyter_server import serverapp
            connection_file = os.path.basename(ipykernel.get_connection_file())
            kernel_id = connection_file.split('-')[1].split('.')[0]

            for server in serverapp.list_running_servers():
                try:
                    response = requests.get(
                        url=f"{server['url']}api/sessions",
                        headers={"Authorization": f"Token {server.get('token', '')}"}
                    )
                    for session in response.json():
                        if session['kernel']['id'] == kernel_id:
                            return os.path.join(server['notebook_dir'], session['notebook']['path'])
                except Exception:
                    continue

            raise RuntimeError("could not determine current notebook path from server sessions.")

        except Exception as e:
            raise ValueError(f"Error retrieving notebook path: {str(e)}")