from typing import Dict, Optional, List, Union

from fi.api.auth import APIKeyAuth, ResponseHandler
from fi.api.types import HttpMethod, RequestConfig
from fi.kb.types import KnowledgeBaseConfig

from fi.utils.errors import InvalidAuthError
from fi.utils.routes import Routes
from fi.utils.errors import FileNotFoundException, UnsupportedFileType

import os

class KBResponseHandler(ResponseHandler[Dict, KnowledgeBaseConfig]):

    @classmethod
    def _parse_success(cls, response) -> Dict:
        """Handles responses for prompt requests"""
        data = response.json()

        if response.request.method == HttpMethod.POST.value and response.url.endswith(
            Routes.knowledge_base.value
        ):
            return data["result"]
        
        if response.request.method == HttpMethod.PATCH.value and response.url.endswith(
            Routes.knowledge_base.value
        ):
            return data["result"]
        
        if response.request.method == HttpMethod.DELETE.value:
            return data
        
        return data
    
    @classmethod
    def _handle_error(cls, response) -> None:
        if response.status_code == 403:
            raise InvalidAuthError()
        else:
            response.raise_for_status()

class KnowledgeBaseClient(APIKeyAuth):

    def __init__(
        self,
        kbase: Optional[KnowledgeBaseConfig] = None,
        fi_api_key: Optional[str] = None,
        fi_secret_key: Optional[str] = None,
        fi_base_url: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            fi_api_key=fi_api_key,
            fi_secret_key=fi_secret_key,
            fi_base_url=fi_base_url,
            **kwargs,
        )
        self.kb = None
        if kbase and not kbase.id:
            try:
                self.kb = self._get_kb_from_name(kbase.name)
            except Exception:
                print("Knowlege Base not found in backend. Create a new knowledge base before running.")
        else:
            self.kb = kbase
            if self.kb:
                print(
                    f"Current Knowledge Base: {self.kb.id} does not exist in the backend. Please create it first before running."
                )
        
    def update_kb(self, name : Optional[str] = None, file_paths: Optional[Union[str, List[str]]] = []):
        """
        Update name of Knowledge Base and/or add files to it.
        
        Args:
            name Optional[str]: Name of the Knowledge Base
            file_path Union[str, List[str]]: List of file paths or a directory path
        
        Returns:
            self for chaining
        """
        try:
            import requests  
            
            if not self.kb:
                print("No kb provided. Please provide or create a kb before running.")
                return None

            if file_paths:
                if not self._check_file_paths(file_paths):
                    return FileNotFoundException(file_path=file_paths)
            url = self._base_url + "/" + Routes.knowledge_base.value
            
            data = {}
            if name or self.kb:
                data.update({
                    "name": self.kb.name if not name else name,
                    "kb_id": str(self.kb.id)
                })
            
            files = []
            
            try:
                if self._valid_file_paths:
                    for file_path in self._valid_file_paths:
                        file_name = file_path.split('/')[-1]
                        file_ext = file_path.split('.')[-1].lower()
                        
                        if file_ext not in ['pdf', 'docx', 'txt', 'rtf']:
                            raise UnsupportedFileType(file_ext=file_ext, file_name=file_name)
                        try:
                            files.append(('file', (file_name, open(file_path, 'rb'), self._get_content_type(file_ext))))
                        except Exception:
                            raise Exception(f"Invalid {file_ext} file. File is either password protected or corrupted.")
                
                headers = {
                    'Accept': 'application/json',
                    'X-Api-Key': self._fi_api_key,
                    'X-Secret-Key': self._fi_secret_key,
                }
                
                response = requests.patch(
                    url=url,
                    data=data,
                    files=files,  
                    headers=headers,
                    timeout=300
                )
                
                if response.status_code != 200:
                    raise Exception(f"Request failed with status code {response.status_code}")
                
                result = response.json()['result']
                if 'notUploaded' in result.keys():
                    raise Exception(f"Files not uploaded: {result['files']}")
                
                response_data = response.json()
                result = response_data.get("result", {})
                
                if result:
                    self.kb.id = result.get("id", self.kb.id)
                    self.kb.name = result.get("name", self.kb.name)
                    if "files" in result:
                        self.kb.files = result["files"]

                return self
            
            finally:
                for file_tuple in files:
                    if hasattr(file_tuple[1][1], 'close'):
                        file_tuple[1][1].close()
            
        except Exception as e:
            print(f"Failed to add files to the Knowledge Base: {str(e)}")
            return None

    def delete_files_from_kb(self, file_names):
        """
        Delete files from the Knowledge Base.
        
        Args:
            file_names List[str]: List of file names to be deleted
        
        Returns:
            self for chaining
        """
        try:
            if not self.kb:
                print("No knowledge base provided. Please provide a knowledge base before running.")
                return None
                
            if not file_names:
                print("Files to be deleted not found. Please provide correct File Names.")
                return self
                
            method = HttpMethod.DELETE
            url = self._base_url + "/" + Routes.knowledge_base_files.value
            
            data = {
                "file_names": file_names,
                "kb_id": str(self.kb.id)
            }
            
            response = self.request(
                config=RequestConfig(
                    method=method,
                    url=url,
                    json=data,
                    headers={'Content-Type': 'application/json'}
                ),
                response_handler=KBResponseHandler,
            )


            return self
        
        except Exception as e:
            print(f"Failed to delete files from Knowledge Base: {str(e)}")
            return None

    def delete_kb(self, kb_ids : Optional[str] = None):
        """
        Delete a Knowledge Base and return the Knowledge Base client.
        
        Args:
            name Optional[str]: Name of the Knowledge Base
            kb_ids Optional[Union[str, List[str]]]: List of kb_ids to delete
        
        """
        try:        
            if not self.kb and not kb_ids:
                print("No knowledge base provided. Please provide a knowledge base before running.")
                return None
            
            method = HttpMethod.DELETE
            url = self._base_url + "/" + Routes.knowledge_base.value       
            json = {
                "kb_ids": [str(self.kb.id)] if not kb_ids else [str(kb_id) for kb_id in kb_ids]
            }
            
            response = self.request(
                config=RequestConfig(
                    method=method,
                    url=url,
                    json=json,
                    headers={'Content-Type': 'application/json'}
                ),
                response_handler=KBResponseHandler,
            )

            self.kb = None
            
            return self
        
        except Exception as e:
            print(f"Failed to delete Knowledge Base: {str(e)}")
            return None

    def create(self, name : Optional[str] = None, file_paths : Optional[Union[str, List[str]]] = []):
        """
        Create a Knowledge Base and return the Knowledge Base client.
        
        Args:
            name Optional[str]: Name of the Knowledge Base
            file_paths Optional[Union[str, List[str]]]: List of file paths or a directory path
        
        Returns:
            self for chaining
        """
        import requests
        
        if self.kb and self.kb.id:
            print(
                f"Knowledge Base, {self.kb.name}, already exists in the backend. Please use a different name to create a new Knowledge Base."
            )
            return self
        
        data = {}
        if name or self.kb:
            data.update({
                "name": self.kb.name if not name else name
            })
            
        method = HttpMethod.POST
        url = self._base_url + "/" + Routes.knowledge_base.value
        
        files = []
        
        try:
            if file_paths:
                if not self._check_file_paths(file_paths):
                    raise FileNotFoundException(file_path = file_paths)
                for file_path in self._valid_file_paths:
                    file_name = file_path.split('/')[-1]
                    file_ext = file_path.split('.')[-1].lower()
                    
                    if file_ext not in ['pdf', 'docx', 'txt', 'rtf']:
                        raise UnsupportedFileType(file_ext=file_ext, file_name=file_name)
                    try:
                        files.append(('file', (file_name, open(file_path, 'rb'), self._get_content_type(file_ext))))
                    except Exception as e:
                        raise(f"Error opening file {file_path}: {str(e)}")
            
            headers = {
                'Accept': 'application/json',
                'X-Api-Key': self._fi_api_key,
                'X-Secret-Key': self._fi_secret_key,
            }
            
            response = requests.post(
                url=url,
                data=data,
                files=files,  
                headers=headers,
                timeout=300
            )
            
            if response.status_code != 200:
                raise Exception(f"Request failed with status code {response.status_code}")

            result = response.json()['result']
            if 'notUploaded' in result.keys():
                raise Exception(f"Files not uploaded: {result['files']}")
                
            response_data = response.json()
            result = response_data.get("result", {})
            
            self.kb = KnowledgeBaseConfig(
                id=result.get("kbId"), 
                name=result.get("kbName"), 
                files=result.get("fileIds", [])
            )
            return self
            
        finally:
            for file_tuple in files:
                if hasattr(file_tuple[1][1], 'close'):
                    file_tuple[1][1].close()

    def _check_file_paths(self, file_paths: Union[str, List[str]]) -> bool:
        """
        Validates the given file paths or directory path.
        
        Args:
            file_paths (Union[str, List[str]]): List of file paths or a directory path
        
        Returns:
            bool: True if all files exist or directory contains valid files, else False
        """
        if isinstance(file_paths, str):

            if os.path.isdir(file_paths):
                
                all_files = [
                    os.path.join(file_paths, f)
                    for f in os.listdir(file_paths)
                    if os.path.isfile(os.path.join(file_paths, f))
                ]
                self._valid_file_paths = all_files
                return len(all_files) > 0
            else:
                raise FileNotFoundError(f"The provided path '{file_paths}' is not a valid directory.")
        
        elif isinstance(file_paths, list):
            valid_paths = [path for path in file_paths if os.path.isfile(path)]
            if len(valid_paths) == len(file_paths):
                self._valid_file_paths = valid_paths
                return True
            else:
                raise FileNotFoundError(
                    f"Some file paths are invalid or do not exist: {file_paths}"
                )
        
        return False

    def _get_content_type(self, file_ext):
        """
        Get the correct content type for a file extension
        
        Args:
            file_ext (str): File extension
        Returns:
            str: Content type
        """
        content_types = {
            "pdf": "application/pdf",
            "rtf": "application/rtf",
            "txt": "text/plain",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
        return content_types.get(file_ext, "application/octet-stream")

    def _get_kb_from_name(self, kb_name):
        """
        Validates the given file paths or directory path.
        
        Args:
            kb_name (str): Name of the Knowledge Base
        
        Returns:
            Knowledge BaseConfig: Knowledge Base Config object 
        """
        response = self.request(
            config=RequestConfig(
                method=HttpMethod.GET,
                url=self._base_url + "/" + Routes.knowledge_base_list.value,
                params={"search": kb_name},
            ),
            response_handler=KBResponseHandler,
        )
        data = response['result'].get('tableData')
        return KnowledgeBaseConfig(id=data[0].get("id"), name= data[0].get("name"))