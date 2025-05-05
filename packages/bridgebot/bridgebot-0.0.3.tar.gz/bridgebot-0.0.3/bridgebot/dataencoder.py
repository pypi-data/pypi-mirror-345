from abc import ABC, abstractmethod
from bridgepy.bid import Bid
from bridgepy.card import Card, Rank, Suit, _rank_order, _suit_order
import numpy as np
from typing import Generic, Literal, TypeVar
from typing_extensions import override


T = TypeVar("T")
R = TypeVar("R")

class DataEncoder(ABC, Generic[T, R]):

    @staticmethod
    @abstractmethod
    def encode(data: T) -> R:
        pass

    @staticmethod
    @abstractmethod
    def decode(value: R) -> T:
        pass

class BidEncoder(DataEncoder[Bid | None, int]):
    """
    0-pass, 1-1C, 2-1D, 3-1H, 4-1S, 5-1NT, 6-2C, 7-2D, 8-2H, 9-2S, 10-2NT, ..., 35-7NT
    """

    @staticmethod
    @override
    def encode(data: Bid | None) -> int:
        if data is None:
            value: int = 0
        else:
            value: int = (data.level - 1) * 5 + _suit_order[data.suit] + 1 if data.suit is not None else data.level * 5
        return value

    @staticmethod
    @override
    def decode(value: int) -> Bid | None:
        if value == 0:
            return None
        bid_index: int = value - 1
        level: int = bid_index // 5 + 1
        suit_index: int = bid_index % 5
        suit: Suit | None = list(Suit)[suit_index] if suit_index < 4 else None
        return Bid(level, suit)

class CardEncoder(DataEncoder[Card, int]):
    """
    0-1C, 1-1D, 2-1H, 3-1S, 4-2C, 5-2D, 6-2H, 7-2S,..., 51-AS
    """

    @staticmethod
    @override
    def encode(data: Card) -> int:
        value: int = _rank_order[data.rank] * 4 + _suit_order[data.suit]
        return value

    @staticmethod
    @override
    def decode(value: int) -> Card:
        rank: Rank = list(Rank)[value // 4]
        suit: Suit = list(Suit)[value % 4]
        return Card(rank, suit)

class PlayerHandEncoder(DataEncoder[list[Card], np.ndarray[tuple[Literal[52]], np.dtype[np.int8]]]):
    """
    one-hot encoding list of size 52 where 0-card not on hand, 1-card on hand, and index follow :class:`CardEncoder`
    """

    @staticmethod
    @override
    def encode(data: list[Card]) -> np.ndarray[tuple[Literal[52]], np.dtype[np.int8]]:
        one_hot_player_hand = np.zeros(52, dtype=np.int8)
        for card in data:
            one_hot_player_hand[CardEncoder.encode(card)] = 1
        return one_hot_player_hand

    @staticmethod
    @override
    def decode(value: np.ndarray[tuple[Literal[52]], np.dtype[np.int8]]) -> list[Card]:
        return [CardEncoder.decode(v) for v in np.argwhere(value == 1).flatten()]
