from app.channels.base import ChannelAdapter
from app.channels.rahulcoolgram import RahulCoolGramAdapter
from app.models.enums import ChannelType

ADAPTERS: dict[str, ChannelAdapter] = {ChannelType.RAHULCOOLGRAM: RahulCoolGramAdapter()}
