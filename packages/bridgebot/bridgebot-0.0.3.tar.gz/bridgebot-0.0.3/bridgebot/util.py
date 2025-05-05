from bridgepy.game import Game
from bridgepy.player import PlayerId


class GameUtil:

    @staticmethod
    def get_next_player_id(game: Game) -> PlayerId | None:
        dealt: bool = game.dealt()
        game_bid_ready: bool = game.game_bid_ready()
        game_finished: bool = game.game_finished()
        bid_winner = game.bid_winner() if dealt and game_bid_ready else None

        player_id = None
        if dealt and not game_bid_ready:
            player_id = game.next_bid_player_id()
        if bid_winner is not None and game.partner is None:
            player_id = bid_winner.player_id
        if dealt and game_bid_ready and game.partner is not None and not game_finished:
            player_id = game.next_trick_player_id()
        return player_id
    
    @staticmethod
    def trick_finished(game: Game) -> bool:
        return len(game.tricks) > 0 and game.tricks[-1].ready_for_trick_winner()

    @staticmethod
    def get_trick_winner(game: Game) -> PlayerId | None:
        if not GameUtil.trick_finished(game):
            return None
        return game.tricks[-1].trick_winner(game.trump_suit())
