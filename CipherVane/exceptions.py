import inspect


class BaseExcept(Exception):
    """Clase base de excepción."""

    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg
        self.file = "<unknown file>"
        self.file_name = "<unknown file>"
        self.context()

    def context(self) -> None:
        """Extrae el contexto del archivo que originó la excepción."""
        frame = inspect.currentframe()
        if frame is None:
            return
        try:
            files = __file__
            while frame is not None and frame.f_code.co_filename == files:
                frame = frame.f_back
            if frame is not None:
                code = frame.f_code
                self.file_name = code.co_filename
        finally:
            del frame

    def __str__(self) -> str:
        """Define qué se muestra al hacer print(error) o str(error)."""
        return f"{self.msg} (Ocurrido en: {self.file_name})"

    def __repr__(self) -> str:
        """Define qué se muestra en la consola interactiva, listas o logs de depuración."""
        return f"<{self.__class__.__name__} msg={self.msg!r} file={self.file_name!r}>"


class PassError(BaseExcept):
    """Fallo al derivar la clave con Argon2."""


class EncryptErrno(BaseExcept):
    """Fallo al cifrar con ChaCha20-Poly1305."""


class DecryptErr(BaseExcept):
    """Fallo al descifrar o verificar la integridad."""


class keyGenerateError(BaseExcept):
    """Fallo al generar o serializar las claves PEM."""
