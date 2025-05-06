from typing import Optional, Tuple, Union, TYPE_CHECKING
import os

from lattica_common.app_api import LatticaAppAPI

from lattica import interface_query as toolkit_interface
from lattica_query.worker_api import LatticaWorkerAPI


def _write_byte_arrays_to_file(file_path, byte_array1, byte_array2):
    with open(file_path, 'wb') as f:
        # Write the length of the first byte array
        f.write(len(byte_array1).to_bytes(4, byteorder='little'))
        # Write the first byte array
        f.write(byte_array1)
        # Write the length of the second byte array
        f.write(len(byte_array2).to_bytes(4, byteorder='little'))
        # Write the second byte array
        f.write(byte_array2)


def read_byte_arrays_from_file(file_path):
    with open(file_path, 'rb') as f:
        # Read the length of the first byte array
        len1 = int.from_bytes(f.read(4), byteorder='little')
        # Read the first byte array
        byte_array1 = f.read(len1)
        # Read the length of the second byte array
        len2 = int.from_bytes(f.read(4), byteorder='little')
        # Read the second byte array
        byte_array2 = f.read(len2)

    return byte_array1, byte_array2


def user_client_init(
        worker_api_client: LatticaWorkerAPI,
        app_client:  LatticaAppAPI,
        secret_key_file_path: Union[str, os.PathLike] = 'my_secret_key.lsk',
     ) -> None:

    serialized_context, serialized_homseq = worker_api_client.get_user_init_data()

    print(f'Creating client FHE keys...')
    serialized_secret_key, serialized_public_key = toolkit_interface.generate_key(
        serialized_homseq, serialized_context)

    # Store locally for later use file
    _write_byte_arrays_to_file(secret_key_file_path, *serialized_secret_key)

    print(f'Registering FHE public key...')
    temp_filename = 'my_pk.lpk'
    # Store as temp file
    with open(temp_filename, 'wb') as handle:
        handle.write(serialized_public_key)
    # Upload to server
    app_client.upload_user_file(temp_filename)
    # Delete temp file
    os.remove(temp_filename)
    print(f'Preprocessing public key...')
    worker_api_client.preprocess_pk()
