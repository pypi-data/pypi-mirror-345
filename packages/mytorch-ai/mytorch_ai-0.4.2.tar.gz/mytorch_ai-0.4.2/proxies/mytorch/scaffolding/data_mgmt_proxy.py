from gRPC_impl.mytorch.scaffolding import data_mgmt_pb2, data_mgmt_pb2_grpc
from connection_utils.server_connection import ServerConnection, wrap_with_error_handler
from utils.logger import Logger
import os
from pathlib import Path
from tqdm import tqdm
import time

class DataMgmtProxy:
    def __init__(self):
        self.channel = ServerConnection.get_active_connection()
        self.stub = data_mgmt_pb2_grpc.DataMgmtServiceStub(self.channel)
        self.logger = Logger.get_logger()

    @wrap_with_error_handler
    def folder_exists_on_server(self, relative_path) -> bool:
        response = self.stub.FolderExistsOnServer(data_mgmt_pb2.RelativePath(path=relative_path))
        return response.value

    @wrap_with_error_handler
    def upload_folder(self, folder_path) -> int:
        """
        Uploads the specified folder and its contents, including subfolders.

        For example, if the folder path is '/home/Users/gduda/mytorch/test_data/resnet_infer', the folder 'resnet_infer' and all its contents
        will be uploaded to the server. On the server, the folder `resnet_infer` will be created in the base path where files are saved.

        Args:
            folder_path (str): The path to the folder to upload, can be relative (from the current working directory).
        """
        # Resolve absolute path from the relative path (if given) and ensure the base path is the parent directory
        folder_path = os.path.abspath(folder_path)
        base_path = os.path.dirname(folder_path)  # Use the parent directory as the base
        trailing_folder = os.path.basename(folder_path)
        self.logger.info(f"Uploading folder: {folder_path} to <server data dir>/{trailing_folder} on server")

        # Collect all files to upload
        files_to_upload = [(file_path.as_posix(), os.path.relpath(file_path.as_posix(), start=base_path))
                           for root, _, files in os.walk(folder_path)
                           for file_path in [Path(root).joinpath(filename) for filename in files]]

        start_time = time.time()  # Start timing the upload process

        # Initialize tqdm progress bar
        with tqdm(total=len(files_to_upload), unit='files', desc=f"Uploading Files from {folder_path}",
                  bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}") as progress_bar:
            def generate_file_stream():
                for file_path, relative_path in files_to_upload:
                    with open(file_path, 'rb') as file:
                        content = file.read()
                        yield data_mgmt_pb2.FileUploadRequest(filepath=relative_path, content=content)
                    progress_bar.update(1)  # Update progress bar per file uploaded

            # Perform the upload and get response
            response = self.stub.UploadFolder(generate_file_stream())

        # Calculate total time taken
        total_time = time.time() - start_time

        # Print final message with total files uploaded and total time taken
        self.logger.info(f"Total files uploaded: {response.count}")
        self.logger.info(f"Total time taken: {total_time:.2f} seconds")
        return response.count