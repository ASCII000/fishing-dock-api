"""
Entities related to blob
"""

from datetime import datetime
from typing import Optional

from dataclasses import dataclass, field


@dataclass
class BlobEntity:
    """
    Entity for file
    """
    provedor: str
    provedor_id: str
    nome: str
    extensao: str
    id: Optional[int] = None
    link: Optional[str] = None
    criado_em: Optional[datetime] = field(default=None)
