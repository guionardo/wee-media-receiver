class MediaNotification:
    """Dados enviados ao backend sobre a mídia processada"""

    __slots__ = ('media_id', 'new_media_id', 'status', 'post_id', 'metadata')

    def __init__(self, media_id: str, new_media_id: str,
                 status: str, post_id: int, metadata: dict):
        self.media_id = media_id
        self.new_media_id = new_media_id
        self.status = status
        self.post_id = post_id
        if not isinstance(metadata, dict):
            metadata = {}
        new_metadata = {}
        for k, v in metadata.items():
            k = k.lower().replace('_', '-')
            try:
                v = round(float(v), 3)
            except:
                ...
            finally:
                new_metadata[k] = v

        self.metadata = new_metadata

    def as_dict(self) -> dict:
        return dict(
            media_id=self.media_id,
            new_media_id=self.new_media_id,
            status=self.status,
            post_id=self.post_id,
            metadata=self.metadata
        )
