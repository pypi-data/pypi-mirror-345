from brynq_sdk_brynq import BrynQ
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_account_sas, ResourceTypes, AccountSasPermissions
from typing import Union, List, Tuple
from datetime import datetime, timedelta


class BlobStorage(BrynQ):
    def __init__(self, label: Union[str, List]):
        super().__init__()
        self.blob_service_client = self.__get_authentication(label=label)

    def __get_authentication(self, label):
        credentials = self.get_system_credential(system='azure-blob-storage', label=label)
        storage_account_name = credentials['storage_account_name']
        storage_account_key = credentials['storage_account_key']
        sas_token = generate_account_sas(
            account_name=storage_account_name,
            account_key=storage_account_key,
            resource_types=ResourceTypes(service=True, container=True, object=True),
            permission=AccountSasPermissions(read=True, write=True, list=True, delete=True, add=True, create=True, update=True, process=True),
            expiry=datetime.utcnow() + timedelta(hours=1)
        )
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_account_name}.blob.core.windows.net",
            credential=sas_token
        )

        return blob_service_client

    def get_containers(self):
        all_containers = self.blob_service_client.list_containers(include_metadata=True)
        container_list = []
        for container in all_containers:
            container_info = {
                'name': container.name,
                'last_modified': container.last_modified,
                'etag': container.etag,
                'lease_state': container.lease,
                'has_immutability_policy': container.has_immutability_policy,
                'has_legal_hold': container.has_legal_hold,
                'metadata': container.metadata
            }
            container_list.append(container_info)

        return container_list

    def get_container(self, container_name: str):
        """
        Get a container from the blob storage
        """
        container = self.blob_service_client.get_container_client(container_name)
        return container

    def create_container(self, container_name: str):
        """
        Create a container in the blob storage
        """
        response = self.blob_service_client.create_container(container_name)
        return response

    def update_container(self):
        pass

    def delete_container(self):
        pass

    def get_folders(self, container_name: str):
        """
        Retrieves a list of 'folders' in the specified container.
        Since Azure Blob Storage uses a flat namespace, folders are simulated using prefixes.

        :param container_name: The name of the container.
        :return: A list of folder names.
        """
        container_client = self.get_container(container_name)
        blobs_list = container_client.list_blobs()

        folder_set = set()
        for blob in blobs_list:
            if '/' in blob.name:
                folder = blob.name.split('/')[0]
                folder_set.add(folder)
        folders = list(folder_set)
        return folders

    def create_folder(self, container_name: str, folder_name: str):
        """
        Create a file with a 0 as content. Because the file is created, the folder is also created. After that the file and the folder are created,
        delete the file so the folder will stay. According to the azure docs, it should be possible to create empty files, but this is not working.
        """
        # Split the url and add the container and folder name in between the url
        original_url = self.blob_service_client.url.split('?')
        url = f"{original_url[0]}/{container_name}/{folder_name}/empty_file?{original_url[1]}"
        blob = BlobClient.from_blob_url(blob_url=url)

        # Now create the file and delete it so the folder will stay
        response = blob.upload_blob(b"0", blob_type='AppendBlob')
        blob.delete_blob()
        return response

    def delete_folder(self, container_name: str, folder_name: str):
        """
        Deletes all the blobs (files) within a folder, effectively deleting the folder.
        :param container_name: The name of the container.
        :param folder_name: The name of the folder to delete.
        """
        container_client = self.get_container(container_name)
        blobs = container_client.list_blobs(name_starts_with=f"{folder_name}/")
        for blob in blobs:
            blob_client = container_client.get_blob_client(blob)
            blob_client.delete_blob()
        return f"Deleted folder {folder_name} and all its contents."

    def get_files(self, container_name: str, folder_name: str = ""):
        """
        Retrieves all files in a container, optionally filtered by folder.
        :param container_name: The name of the container.
        :param folder_name: The name of the folder (optional). If provided, only files in this folder will be listed.
        :return: A list of file names in the container or folder.
        """
        container_client = self.get_container(container_name)
        blobs_list = container_client.list_blobs(name_starts_with=f"{folder_name}/" if folder_name else "")

        file_list = []
        for blob in blobs_list:
            if not blob.name.endswith('/'):  # Exclude folder markers
                file_list.append(blob.name)

        return file_list

    def upload_file(self, container_name: str, blob_name: str, file_path: str, overwrite: bool = False):
        """
        Uploads a single file to Azure Blob Storage.
        :param container_name: The name of the container to upload to.
        :param blob_name: The name of the blob (the file name in blob storage).
        :param file_path: The local path to the file to upload.
        :param overwrite: Whether to overwrite an existing blob. Default is False.
        """
        # Get the container client
        container_client = self.get_container(container_name)

        # Get the blob client
        blob_client = container_client.get_blob_client(blob_name)

        # Open the file and upload
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=overwrite)

        print(f"Successfully uploaded {file_path} to {blob_client.url}")
        return blob_client.url

    def upload_files(self, container_name: str, files: List[Tuple[str, str]], overwrite: bool = False):
        """
        Uploads multiple files to Azure Blob Storage.
        :param container_name: The name of the container to upload to.
        :param files: A list of tuples (blob_name, file_path), where blob_name is the name of the blob in storage, and file_path is the local file path.
        :param overwrite: Whether to overwrite existing blobs. Default is False.
        """
        success = True
        for blob_name, file_path in files:
            result = self.upload_file(container_name, blob_name, file_path, overwrite=overwrite)
            if result is None:
                success = False
        return success

    def delete_file(self, container_name: str, blob_name: str):
        """
        Deletes a specific file from Azure Blob Storage.
        :param container_name: The name of the container.
        :param blob_name: The name of the blob (the file) to delete.
        """
        container_client = self.get_container(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()
        return f"Deleted file {blob_name} from container {container_name}."
