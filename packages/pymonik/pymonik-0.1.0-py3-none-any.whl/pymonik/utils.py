from typing import Optional

import grpc
from armonik.common.channel import create_channel

def create_grpc_channel(endpoint: str, certificate_authority: Optional[str] = None, client_certificate: Optional[str] = None, client_key: Optional[str] = None) -> grpc.Channel:
    """
    Create a gRPC channel based on the configuration.
    """
    cleaner_endpoint = endpoint
    if cleaner_endpoint.startswith("http://"):
        cleaner_endpoint = cleaner_endpoint[7:]
    if cleaner_endpoint.endswith("/"):
        cleaner_endpoint = cleaner_endpoint[:-1]
    if certificate_authority:
        # Create grpc channel with tls
        channel = create_channel(
            cleaner_endpoint,
            options=(("grpc.ssl_target_name_override", "armonik.local"),),
            certificate_authority=certificate_authority,
            client_certificate=client_certificate,
            client_key=client_key,
        )
    else:
        # Create insecure grpc channel
        channel = grpc.insecure_channel(cleaner_endpoint)
    return channel
