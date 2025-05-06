from pydantic import BaseModel, SecretStr, field_serializer


class LookerStudioCredentials(BaseModel):
    """
    Looker Studio Credentials match the Service Account credentials JSON
    but with an additional admin_email field.
    """

    admin_email: str
    auth_provider_x509_cert_url: str
    auth_uri: str
    client_email: str
    client_id: str
    client_x509_cert_url: str
    private_key: SecretStr
    private_key_id: str
    project_id: str
    token_uri: str
    type: str

    @field_serializer("private_key")
    def dump_secret(self, pk):
        """When using model_dump, show private_key value"""
        return pk.get_secret_value()
