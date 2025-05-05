from abc import ABC, abstractmethod
from bridgepy.bid import Bid
from bridgepy.card import Card
import random
from typing import overload
from typing_extensions import override

from bridgebot.action import Action
from bridgebot.exception import BridgeAgentInvalidObservationType
from bridgebot.observation import Observation


class BridgeAgent(ABC):

    @overload
    def predict(self, observation: dict) -> int: ...

    @overload
    def predict(self, observation: Observation) -> Action: ...
    
    def predict(self, observation: dict | Observation) -> int | Action:
        if isinstance(observation, dict):
            action: Action = self.__predict(Observation.build_from_dict(observation))
            return action.value
        if isinstance(observation, Observation):
            action: Action = self.__predict(observation)
            return action
        raise BridgeAgentInvalidObservationType()

    def __predict(self, observation: Observation) -> Action:
        if observation.bid_phase():
            bid: Bid | None = self._bid(observation)
            return Action.encode_bid(bid)
        if observation.choose_partner_phase():
            card: Card = self._choose_partner(observation)
            return Action.encode_choose_partner(card)
        if observation.trick_phase():
            card: Card = self._trick(observation)
            return Action.encode_trick(card)
        return Action.encode_illegal()

    @abstractmethod
    def _bid(self, observation: Observation) -> Bid | None:
        pass
    
    @abstractmethod
    def _choose_partner(self, observation: Observation) -> Card:
        pass
    
    @abstractmethod
    def _trick(self, observation: Observation) -> Card:
        pass

class BridgeRandomAgent(BridgeAgent):
    
    @override
    def _bid(self, observation: Observation) -> Bid | None:
        valid_bids: list[Bid] = observation.get_valid_bids()
        pass_bid: list[None] = [None]
        bid: Bid | None = random.choice(pass_bid + valid_bids)
        return bid
    
    @override
    def _choose_partner(self, observation: Observation) -> Card:
        valid_partner_cards: list[Card] = observation.get_valid_partner_cards()
        card: Card = random.choice(valid_partner_cards)
        return card
    
    @override
    def _trick(self, observation: Observation) -> Card:
        valid_trick_cards: list[Card] = observation.get_valid_trick_cards()
        card: Card = random.choice(valid_trick_cards)
        return card
