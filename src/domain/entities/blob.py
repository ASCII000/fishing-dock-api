"""
Entities related to blob
"""

from typing import Optional

from dataclasses import dataclass


@dataclass
class FileEntity:
    """
    Entity for file
    """
    id: Optional[int] = None
    provedor: str
    provedor_id: str
    link: Optional[str]
    nome: str
    extensao: str
