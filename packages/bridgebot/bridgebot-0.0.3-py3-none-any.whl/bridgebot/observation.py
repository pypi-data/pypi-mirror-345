from bridgepy.bid import Bid
from bridgepy.card import Card, Rank, Suit
from bridgepy.game import Game, GameTrick
from bridgepy.player import PlayerBid, PlayerHand, PlayerId, PlayerTrick
from dataclasses import dataclass, fields
import numpy as np
from typing import Literal, Type, TypeVar

from bridgebot.action import Action
from bridgebot.dataencoder import BidEncoder, CardEncoder, PlayerHandEncoder
from bridgebot.exception import BridgeObservationGameBidPhaseNotOver, BridgeObservationGameNoBidHasBeenMade


ObservationType = TypeVar("ObservationType", bound = "Observation")

@dataclass
class Observation:
    player_turn: int
    player_hand: np.ndarray[tuple[Literal[52]], np.dtype[np.int8]]
    bid_history: np.ndarray[tuple[Literal[210]], np.dtype[np.int8]]
    game_bid_ready: int
    partner_card: int
    partner: int
    trick_history: np.ndarray[tuple[Literal[104]], np.dtype[np.int8]]

    def bid_phase(self) -> bool:
        return self.game_bid_ready == 0
    
    def choose_partner_phase(self) -> bool:
        return self.game_bid_ready == 1 and self.partner_card == 0
    
    def trick_phase(self) -> bool:
        return self.game_bid_ready == 1 and self.partner_card != 0 and self.trick_history[-2] == 0
    
    def get_player_hand(self) -> PlayerHand:
        return PlayerHand(
            player_id = PlayerId(str(self.player_turn)),
            cards = PlayerHandEncoder.decode(self.player_hand),
        )
    
    def get_bid_history(self) -> list[PlayerBid]:
        return [PlayerBid(
            # replace actual player id with player index
            player_id = PlayerId(str(self.bid_history[2 * i])),
            bid = BidEncoder.decode(self.bid_history[2 * i + 1] - 1),
        ) for i in range(len(self.bid_history) // 2) if self.bid_history[2 * i] != 0]
    
    def get_partner_card(self) -> Card | None:
        if self.partner_card == 0:
            return None
        return CardEncoder.decode(self.partner_card - 1)
    
    def get_partner(self) -> PlayerId | None:
        if self.partner == 0:
            return None
        # replace actual player id with player index
        return PlayerId(str(self.partner))
    
    def get_trick_history(self) -> list[GameTrick]:
        game_tricks: list[GameTrick] = []
        for i in range(0, len(self.trick_history), 8):
            encoded_game_trick = self.trick_history[i : i + 8]
            if encoded_game_trick[0] == 0:
                break
            player_tricks: list[PlayerTrick] = []
            for j in range(0, len(encoded_game_trick), 2):
                encoded_player_id = encoded_game_trick[j]
                if encoded_player_id == 0:
                    break
                encoded_card = encoded_game_trick[j + 1]
                player_tricks.append(PlayerTrick(
                    # replace actual player id with player index
                    player_id = PlayerId(str(encoded_player_id)),
                    trick = CardEncoder.decode(encoded_card - 1),
                ))
            game_tricks.append(GameTrick(
                player_tricks = player_tricks,
            ))
        return game_tricks
    
    def get_valid_bids(self) -> list[Bid]:
        if not self.bid_phase():
            return []
        latest_bid: Bid | None = self.find_latest_bid()
        all_available_bids: list[Bid] = [Bid(level, suit) for level in range(1, 8) for suit in [*Suit, None]]
        if latest_bid is None:
            return all_available_bids
        if latest_bid == Bid(level = 7, suit = None):
            return []
        return [bid for bid in all_available_bids if bid > latest_bid]
    
    def find_latest_bid(self) -> Bid | None:
        for player_bid in reversed(self.get_bid_history()):
            if player_bid.bid is not None:
                return player_bid.bid
        return None
    
    def get_valid_partner_cards(self) -> list[Card]:
        if not self.choose_partner_phase():
            return []
        cards: list[Card] = self.get_player_hand().cards
        all_available_cards: list[Card] = [Card(rank, suit) for rank in Rank for suit in Suit]
        return list(set(all_available_cards) - set(cards))
    
    def get_valid_trick_cards(self) -> list[Card]:
        if not self.trick_phase():
            return []
        trick_history: list[GameTrick] = self.get_trick_history()
        cards: list[Card] = self.get_player_hand().cards
        trump_suit: Suit | None = self.trump_suit()
        if len(trick_history) == 0:
            if trump_suit is None:
                return cards
            if all([card.suit == trump_suit for card in cards]):
                return cards
            return [card for card in cards if card.suit != trump_suit]
        latest_trick: GameTrick = trick_history[-1]
        trump_broken: bool = self.trump_broken()
        if latest_trick.ready_for_trick_winner():
            if trump_suit is None:
                return cards
            if trump_broken:
                return cards
            if all([card.suit == trump_suit for card in cards]):
                return cards
            return [card for card in cards if card.suit != trump_suit]
        first_suit: Suit = latest_trick.first_suit()
        cards_following_first_suit: list[Card] = [card for card in  cards if card.suit == first_suit]
        if trump_suit is None:
            if len(cards_following_first_suit) == 0:
                return cards
            return cards_following_first_suit
        if len(cards_following_first_suit) == 0:
            return cards
        return cards_following_first_suit
    
    def trump_suit(self) -> Suit | None:
        if self.bid_phase():
            raise BridgeObservationGameBidPhaseNotOver()
        latest_bid: Bid | None = self.find_latest_bid()
        if latest_bid is None:
            raise BridgeObservationGameNoBidHasBeenMade()
        return latest_bid.suit
    
    def trump_broken(self) -> bool:
        if not self.trick_phase():
            return False
        trump_suit: Suit | None = self.trump_suit()
        if trump_suit is None:
            return False
        for game_trick in reversed(self.get_trick_history()):
            for player_trick in reversed(game_trick.player_tricks):
                if player_trick.trick.suit == trump_suit:
                    return True
        return False

    @classmethod
    def build(cls: Type[ObservationType], game: Game, player_id: PlayerId | None) -> ObservationType:
        return cls(
            player_turn = Observation.__encode_player_turn(game, player_id),
            player_hand = Observation.__encode_player_hand(game, player_id),
            bid_history = Observation.__encode_bid_history(game),
            game_bid_ready = Observation.__encode_game_bid_ready(game),
            partner_card = Observation.__encode_partner_card(game),
            partner = Observation.__encode_partner(game),
            trick_history = Observation.__encode_trick_history(game),
        )
    
    @classmethod
    def build_from_dict(cls: Type[ObservationType], observation: dict) -> ObservationType:
        field_names = [field.name for field in fields(Observation)]
        obs = {k: v for k, v in observation.items() if k in field_names}
        return cls(**obs)
    
    @classmethod
    def build_dummy(cls: Type[ObservationType]) -> ObservationType:
        return cls(
            player_turn = 0,
            player_hand = np.zeros(52, np.int8),
            bid_history = np.zeros(210, np.int8),
            game_bid_ready = 0,
            partner_card = 0,
            partner = 0,
            trick_history = np.zeros(104, np.int8),
        )
    
    @staticmethod
    def __encode_player_turn(game: Game, player_id: PlayerId | None) -> int:
        """
        0-na, 1-player 1, 2-player 2, 3-player 3, 4-player 4
        """
        if player_id is None:
            return 0
        return Observation.__encode_player_id(game, player_id)
    
    @staticmethod
    def __encode_player_hand(game: Game, player_id: PlayerId | None) -> np.ndarray[tuple[Literal[52]], np.dtype[np.int8]]:
        """
        one-hot encoding list of size 52 where 0-card not on hand, 1-card on hand
        """
        if player_id is None:
            player_hand: list[Card] = []
        else:
            player_hand: list[Card] = game.find_player_hand(player_id).cards
        return PlayerHandEncoder.encode(player_hand)
    
    @staticmethod
    def __encode_bid_history(game: Game) -> np.ndarray[tuple[Literal[210]], np.dtype[np.int8]]:
        """
        a list of 105 bids, each bid is labeled as [player, bid] where
        player is 0-na, 1-player 1, 2-player 2, 3- player 3, 4-player 4 and
        bid is 0-na, 1-pass, 2-1C, 3-1D, 4-1H, 5-1S, 6-1NT, 7-2C, 8-2D, 9-2H, 10-2S, 11-2NT, ..., 36-7NT
        """
        bid_history = np.zeros(210, np.int8)
        actual_bid_history = np.array([(
            Observation.__encode_player_id(game, player_bid.player_id),
            BidEncoder.encode(player_bid.bid) + 1,
        ) for player_bid in game.bids]).flatten()
        bid_history[:len(actual_bid_history)] = actual_bid_history
        return bid_history
    
    @staticmethod
    def __encode_game_bid_ready(game: Game) -> int:
        """
        0-game bid not ready, 1-game bid ready
        """
        return 1 if game.game_bid_ready() else 0
    
    @staticmethod
    def __encode_partner_card(game: Game) -> int:
        """
        0-partner not chosen, 1-2C, 2-2D, 3-2H, 4-2S, 5-3C, 6-3D, 7-3H, 8-3S,..., 52-AS
        """
        if game.partner is None:
            return 0
        return CardEncoder.encode(game.partner) + 1

    @staticmethod
    def __encode_partner(game: Game) -> int:
        """
        0-partner not revealed, 1-player 1, 2-player 2, 3-player 3, 4-player 4
        """
        if game.partner_player_id is None:
            return 0
        return Observation.__encode_player_id(game, game.partner_player_id)
    
    @staticmethod
    def __encode_trick_history(game: Game) -> np.ndarray[tuple[Literal[104]], np.dtype[np.int8]]:
        """
        a list of 52 tricks, each trick is labeled as [player, trick] where
        player is 0-na, 1-player 1, 2-player 2, 3-player 3, 4-player 4 and
        trick is 0-na, 1-2C, 2-2D, 3-2H, 4-2S, 5-3C, 6-3D, 7-3H, 8-3S,..., 52-AS
        """
        trick_history = np.zeros(104, np.int8)
        actual_trick_history = np.array([(
            Observation.__encode_player_id(game, player_trick.player_id),
            CardEncoder.encode(player_trick.trick) + 1,
        ) for game_trick in game.tricks for player_trick in game_trick.player_tricks]).flatten()
        trick_history[:len(actual_trick_history)] = actual_trick_history
        return trick_history
    
    @staticmethod
    def __encode_player_id(game: Game, player_id: PlayerId) -> int:
        """
        1-player 1, 2-player 2, 3-player 3, 4-player 4
        """
        return game.player_ids.index(player_id) + 1

    def get_action_masks(self) -> np.ndarray[tuple[Literal[140]], np.dtype[np.int8]]:
        mask = np.zeros(140, dtype = np.int8)
        if self.bid_phase():
            valid_bids: list[Bid] = self.get_valid_bids()
            pass_bid: list[None] = [None]
            actions: list[Action] = [Action.encode_bid(bid) for bid in pass_bid + valid_bids]
            for action in actions:
                mask[action.value] = 1
        if self.choose_partner_phase():
            cards: list[Card] = self.get_valid_partner_cards()
            actions: list[Action] = [Action.encode_choose_partner(card) for card in cards]
            for action in actions:
                mask[action.value] = 1
        if self.trick_phase():
            cards: list[Card] = self.get_valid_trick_cards()
            actions: list[Action] = [Action.encode_trick(card) for card in cards]
            for action in actions:
                mask[action.value] = 1
        return mask
    
    def get_dummy_action_masks(self) -> np.ndarray[tuple[Literal[140]], np.dtype[np.int8]]:
        return np.zeros(140, dtype = np.int8)
