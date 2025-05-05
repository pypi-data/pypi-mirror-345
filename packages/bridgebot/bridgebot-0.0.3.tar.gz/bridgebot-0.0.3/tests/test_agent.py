from unittest import TestCase, main
from bridgepy.game import Game, GameId
from bridgepy.player import PlayerId

from bridgebot.agent import BridgeRandomAgent
from bridgebot.env import BridgeEnv
from bridgebot.util import GameUtil


class TestAgent(TestCase):

    def test_BridgeRandomAgent(self):
        # create game with 4 players
        game_id = GameId("1")
        player_id1 = PlayerId("1")
        player_id2 = PlayerId("2")
        player_id3 = PlayerId("3")
        player_id4 = PlayerId("4")
        game = Game(id = game_id, player_ids = [player_id1])
        game.add_player(player_id2)
        game.add_player(player_id3)
        game.add_player(player_id4)

        # create bridge environment
        env = BridgeEnv(game)

        # create bridge random agent
        agent = BridgeRandomAgent()

        # play game until done
        obs, _ = env.reset()
        done = False
        while not done:
            player_id: PlayerId | None = GameUtil.get_next_player_id(env.game)
            if player_id is None:
                break
            action = agent.predict(obs[player_id.value])
            obs, rewards, dones, _, _ = env.step({player_id.value: action})
            # all actions should be valid, no negative rewards expected
            self.assertTrue(all(reward >= 0 for reward in rewards.values()))
            done = dones["__all__"]

if __name__ == '__main__':
    main()
