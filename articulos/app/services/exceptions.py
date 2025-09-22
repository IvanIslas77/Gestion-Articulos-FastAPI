"""Excepciones del dominio de servicios para artículos."""

class ArticleNotFoundError(Exception):
    """Se levanta cuando no se encuentra un artículo solicitado."""


class ArticleAlreadyExistsError(Exception):
    """Se levanta cuando la combinación (title, author) ya está registrada."""
