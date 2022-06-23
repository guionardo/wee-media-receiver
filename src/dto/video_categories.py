from pydantic import BaseModel


class VideoCategory(BaseModel):
    drawings: float = 0.0
    hentai: float = 0.0
    neutral: float = 0.0
    porn: float = 0.0
    sexy: float = 0.0

    def values(self) -> dict:
        s = {}
        if self.drawings > 0:
            s['drawings'] = str(self.drawings)
        if self.hentai > 0:
            s['hentai'] = str(self.hentai)
        if self.neutral > 0:
            s['neutral'] = str(self.neutral)
        if self.porn > 0:
            s['porn'] = str(self.porn)
        if self.sexy > 0:
            s['sexy'] = str(self.sexy)
        return s

    def __str__(self) -> str:
        s = self.values()
        if not s:
            s['unidentified'] = 0
        return str(s)
