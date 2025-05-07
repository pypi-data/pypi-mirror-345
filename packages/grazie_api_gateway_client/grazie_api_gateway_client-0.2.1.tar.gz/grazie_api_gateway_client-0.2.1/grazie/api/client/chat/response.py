from decimal import Decimal
from enum import Enum
from typing import Optional

import attrs

from grazie.api.client.chat.prompt import ChatPrompt
from grazie.api.client.utils import typ, typ_or_none


@attrs.define(auto_attribs=True)
class LLMChatEventV5:
    type: str
    content: str
    name: Optional[str] = None


class LLMChatEventType(str, Enum):
    Content = "Content"
    FunctionCall = "FunctionCall"
    QuotaMetadata = "QuotaMetadata"


@attrs.define(auto_attribs=True)
class Credit:
    amount: Decimal


@attrs.define(auto_attribs=True)
class QuotaID:
    quotaId: str


@attrs.define(auto_attribs=True)
class Quota:
    license: str  # Deprecated
    until: int
    current: Credit = typ(Credit)
    maximum: Credit = typ(Credit)
    quotaID: QuotaID = typ(QuotaID)


@attrs.define(auto_attribs=True)
class LLMChatEventV6:
    type: LLMChatEventType = attrs.field(
        converter=LLMChatEventType  # pyright: ignore [reportGeneralTypeIssues]
    )
    content: str = ""
    name: Optional[str] = None
    updated: Optional[Quota] = typ_or_none(Quota)
    spent: Optional[Credit] = typ_or_none(Credit)


@attrs.define(auto_attribs=True, frozen=True)
class ChatResponse:
    prompt: ChatPrompt
    content: str
    function_call: Optional[str] = None
    updated: Optional[Quota] = None
    spent: Optional[Credit] = None


@attrs.define(auto_attribs=True, frozen=True)
class ChatResponseStream:
    chunk: str
    function_call: Optional[str] = None
    updated: Optional[Quota] = None
    spent: Optional[Credit] = None
