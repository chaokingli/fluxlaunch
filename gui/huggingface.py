"""
HuggingFace Model Downloader
Download GGUF models from HuggingFace Hub
"""

import requests
import os
import re
from typing import List, Dict, Optional, Tuple, Callable
from pathlib import Path
import threading


class HuggingFaceDownloader:
    """Download GGUF models from HuggingFace"""

    def __init__(self, download_dir: Optional[Path] = None):
        self.download_dir = download_dir or (Path.home() / "llama" / "models")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.cancel_flag = threading.Event()

    def set_cancel(self):
        """Signal to cancel current download"""
        self.cancel_flag.set()

    def clear_cancel(self):
        """Clear the cancel flag"""
        self.cancel_flag.clear()

    def parse_huggingface_url(self, url: str) -> Optional[Tuple[str, str, str]]:
        """
        Parse HuggingFace URL and return (repo_id, filename, branch)

        Supported formats:
        - https://huggingface.co/TheBloke/Llama-2-7B-GGUF/resolve/main/llama-2-7b.Q4_K_M.gguf
        - https://huggingface.co/TheBloke/Llama-2-7B-GGUF/blob/main/llama-2-7b.Q4_K_M.gguf
        - TheBloke/Llama-2-7B-GGUF/llama-2-7b.Q4_K_M.gguf
        """
        # Handle full URLs
        if url.startswith("http"):
            # Pattern: huggingface.co/{repo_id}/resolve/{branch}/{filename}
            match = re.search(
                r"huggingface\.co/([^/]+/[^/]+)/(?:resolve|blob)/([^/]+)/(.+)", url
            )
            if match:
                return match.group(1), match.group(3), match.group(2)
            return None

        # Handle short format: {repo_id}/{filename}
        if "/" in url:
            parts = url.split("/")
            if len(parts) >= 2:
                repo_id = parts[0]
                filename = "/".join(parts[1:])
                return repo_id, filename, "main"

        return None

    def get_model_info(
        self, repo_id: str, filename: str, branch: str = "main"
    ) -> Optional[Dict]:
        """Get model file info from HuggingFace API"""
        api_url = f"https://huggingface.co/api/models/{repo_id}/tree/{branch}"

        try:
            # For root level files
            response = self.session.get(api_url, timeout=30)
            if response.status_code != 200:
                return None

            files = response.json()
            for file_info in files:
                if file_info.get("path") == filename:
                    return file_info

            # Try nested path
            path_parts = filename.split("/")
            if len(path_parts) > 1:
                subdir = "/".join(path_parts[:-1])
                api_url = f"https://huggingface.co/api/models/{repo_id}/tree/{branch}/{subdir}"
                response = self.session.get(api_url, timeout=30)
                if response.status_code == 200:
                    files = response.json()
                    file_name = path_parts[-1]
                    for file_info in files:
                        if (
                            file_info.get("path") == file_name
                            or file_info.get("name") == file_name
                        ):
                            return file_info

            return None
        except Exception as e:
            print(f"Error getting model info: {e}")
            return None

    def get_download_url(
        self, repo_id: str, filename: str, branch: str = "main"
    ) -> str:
        """Get the direct download URL for a model file"""
        return f"https://huggingface.co/{repo_id}/resolve/{branch}/{filename}"

    def list_available_models(
        self, repo_id: str, branch: str = "main", pattern: str = "*.gguf"
    ) -> List[str]:
        """List all GGUF files in a repository"""
        api_url = f"https://huggingface.co/api/models/{repo_id}/tree/{branch}"

        try:
            response = self.session.get(api_url, timeout=30)
            if response.status_code != 200:
                return []

            files = response.json()
            gguf_files = []
            for file_info in files:
                path = file_info.get("path", "")
                if path.endswith(".gguf"):
                    gguf_files.append(path)

            return sorted(gguf_files)
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def download(
        self,
        url: str,
        callback: Optional[Callable[[int, int], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> Tuple[bool, str]:
        """
        Download a model file from HuggingFace

        Returns: (success, message)
        """
        self.clear_cancel()

        parsed = self.parse_huggingface_url(url)
        if not parsed:
            return False, _("dialogs.invalid_url")

        repo_id, filename, branch = parsed

        def log(msg):
            if log_callback:
                log_callback(msg)
            else:
                print(msg)

        log(f"解析 URL: repo={repo_id}, file={filename}, branch={branch}")

        # Get file info
        file_info = self.get_model_info(repo_id, filename, branch)
        if file_info:
            file_size = file_info.get("size", 0)
            log(f"文件大小：{self._format_size(file_size)}")

        # Prepare download
        download_url = self.get_download_url(repo_id, filename, branch)
        output_path = self.download_dir / Path(filename).name

        log(f"下载目标：{output_path}")
        log("开始下载...")

        try:
            headers = {}
            response = self.session.get(
                download_url, stream=True, headers=headers, timeout=30
            )

            if response.status_code != 200:
                return False, f"下载失败：HTTP {response.status_code}"

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 8192

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self.cancel_flag.is_set():
                        log("下载已取消")
                        # Clean up partial file
                        if output_path.exists():
                            output_path.unlink()
                        return False, "下载已取消"

                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if callback and total_size > 0:
                            callback(downloaded, total_size)

            log(f"下载完成：{output_path}")
            if total_size > 0:
                log(f"总大小：{self._format_size(output_path.stat().st_size)}")

            return True, str(output_path)

        except requests.exceptions.Timeout:
            return False, "下载超时"
        except requests.exceptions.ConnectionError:
            return False, "网络连接失败"
        except requests.exceptions.RequestException as e:
            return False, f"下载错误：{e}"
        except Exception as e:
            return False, f"未知错误：{e}"

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"

    def get_popular_gguf_repos(self) -> List[Dict[str, str]]:
        """Return a list of popular GGUF model repositories"""
        return [
            {"name": "Llama 3.2 (Meta)", "repo": "unsloth/Llama-3.2-3B-Instruct-GGUF"},
            {"name": "Qwen 2.5 (Alibaba)", "repo": "Qwen/Qwen2.5-7B-Instruct-GGUF"},
            {"name": "Gemma 2 (Google)", "repo": "bartowski/gemma-2-9b-it-GGUF"},
            {"name": "Mistral 7B", "repo": "TheBloke/Mistral-7B-Instruct-v0.3-GGUF"},
            {
                "name": "Phi-3 (Microsoft)",
                "repo": "bartowski/Phi-3.5-mini-instruct-GGUF",
            },
            {"name": "Yi 1.5 (01.AI)", "repo": "bartowski/Yi-1.5-9B-Chat-GGUF"},
        ]
