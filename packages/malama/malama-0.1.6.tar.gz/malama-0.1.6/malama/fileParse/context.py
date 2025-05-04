# malama/pdfqa/context.py

class PDFContext:
    _text = None

    @classmethod
    def set_text(cls, text):
        cls._text = text

    @classmethod
    def get_text(cls):
        return cls._text

    @classmethod
    def is_loaded(cls):
        return cls._text is not None
