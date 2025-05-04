# malama/pdfqa/exceptions.py

class FileNotFoundErrorCustom(Exception):
    def __init__(self, message="The specified file path was not found."):
        super().__init__(message)

class FileTypeNotSupportedError(Exception):
    def __init__(self, message="Only PDF, DOCX, and XLSX files are supported."):
        super().__init__(message)

class EmptyFileError(Exception):
    def __init__(self, message="The file is empty."):
        super().__init__(message)

class NoFileFound(Exception):
    def __init__(self, message="No File has been loaded yet."):
        super().__init__(message)

class EmptyQueryError(Exception):
    def __init__(self, message="The query is empty."):
        super().__init__(message)

class GeminiAPIEmptyError(Exception):
    def __init__(self, message="API key for Gemini must be provided."):
        super().__init__(message)

class MissingModelError(Exception):
    def __init__(self, message="No model name provided. Model name is required."):
        super().__init__(message)

class InvalidModelError(Exception):
    def __init__(self, message="The model name that you have provide is not available"):
        super().__init__(message)

class MissingAPIKeyError(Exception):
    def __init__(self, message="No api key is provided. Api key is required."):
        super().__init__(message)


