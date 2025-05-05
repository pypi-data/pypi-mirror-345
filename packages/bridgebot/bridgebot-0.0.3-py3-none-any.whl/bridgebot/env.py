from typing import Any
from bridgepy.exception import BizException
from bridgepy.game import Game
from bridgepy.player import PlayerId
from dataclasses import asdict
import gymnasium as gym
from gymnasium.spaces.utils import flatten, flatten_space
from ray.rllib.env.multi_agent_env import MultiAgentEnv
import torch

from bridgebot.action import Action
from bridgebot.exception import BridgeEnvGameAlreadyTerminalState, BridgeEnvGameNotReadyToStart
from bridgebot.observation import Observation
from bridgebot.util import GameUtil
        

class BridgeEnv(MultiAgentEnv):
    """
    Floating bridge environment

    Parameters
    :param game: bridgepy ``Game`` object, must have 4 players

    Attributes
    - :attr:`action_spaces`: 4 x 140 discrete actions labeled 0, 1, 2, ..., 139
        - bid: labeled 0-pass, 1-1C, 2-1D, 3-1H, 4-1S, 5-1NT, 6-2C, 7-2D, 8-2H, 9-2S, 10-2NT, ..., 35-7NT
        - choose partner: labeled 36-2C, 37-2D, 38-2H, 39-2S, 40-3C, 41-3D, 42-3H, 43-3S, ..., 87-AS
        - trick: labeled 88-2C, 89-2D, 90-2H, 91-2S, 92-3C, 93-3D, 94-3H, 95-3S,..., 139-AS
    - :attr:`observation_spaces`: 4 x dictionary of 7 spaces
        - player turn: 5 discrete observations labeled 0-na, 1-player 1, 2-player 2, 3-player 3, 4-player 4
        - player hand: 52 multi-discrete observations labeled 0-card not on hand, 1-card on hand
        - bid history: 210 multi-discrete observations consisting of 105 (player, bid) pairs where
        player is 0-na, 1-player 1, 2-player 2, 3- player 3, 4-player 4 and
        bid is 0-na, 1-pass, 2-1C, 3-1D, 4-1H, 5-1S, 6-1NT, 7-2C, 8-2D, 9-2H, 10-2S, 11-2NT, ..., 36-7NT
        - game bid ready: 2 discrete observations labeled 0-game bid not ready, 1-game bid ready
        - partner card: 53 discrete observations labeled 0-partner not chosen,
        1-2C, 2-2D, 3-2H, 4-2S, 5-3C, 6-3D, 7-3H, 8-3S, ..., 52-AS
        - partner: 5 discrete observations labeled 0-partner not revealed, 1-player 1, 2-player 2, 3-player 3, 4-player 4
        - trick history: 104 multi discrete observations consisting of 52 (player, trick) pairs where
        player is 0-na, 1-player 1, 2-player 2, 3-player 3, 4-player 4 and
        trick is 0-na, 1-2C, 2-2D, 3-2H, 4-2S, 5-3C, 6-3D, 7-3H, 8-3S, ..., 52-AS
        - action masks: 140 multi-discrete observations labeled 0-illegal action, 1-legal action
    """

    def __init__(self, game: Game) -> None:
        super().__init__()
        if not game.dealt():
            raise BridgeEnvGameNotReadyToStart()
        self.game = game
        self.possible_agents: list[str] = [player_id.value for player_id in game.player_ids]
        self.agents: list[str] = self.possible_agents
        self.observation_spaces = {agent: self.get_observation_space(agent) for agent in self.possible_agents}
        self.action_spaces = {agent: self.get_action_space(agent) for agent in self.possible_agents}
    
    def get_observation_space(self, agent_id: str) -> gym.Space:
        return gym.spaces.Dict({
            "player_turn": gym.spaces.Discrete(4 + 1),
            "player_hand": gym.spaces.MultiBinary(52),
            "bid_history": gym.spaces.MultiDiscrete([4 + 1, 36 + 1] * 105),
            "game_bid_ready": gym.spaces.Discrete(1 + 1),
            "partner_card": gym.spaces.Discrete(52 + 1),
            "partner": gym.spaces.Discrete(4 + 1),
            "trick_history": gym.spaces.MultiDiscrete([4 + 1, 52 + 1] * 52),
            "action_masks": gym.spaces.MultiBinary(139 + 1),
        })
    
    def get_action_space(self, agent_id: str) -> gym.Space:
        return gym.spaces.Discrete(139 + 1)
    
    def reset(self, *, seed: int | None = None, options: dict | None = None) -> tuple[dict, dict]:
        super().reset(seed = seed, options = options)
        self.game.reset_game()
        player_id: PlayerId | None = GameUtil.get_next_player_id(self.game)
        obs = {}
        for agent in self.agents:
            if player_id is not None and agent == player_id.value:
                obs[agent] = self._get_obs(agent)
            else:
                obs[agent] = self._get_dummy_obs(agent)
        return obs, {}
    
    def _get_obs(self, agent_id: str) -> Any:
        observation = Observation.build(self.game, PlayerId(agent_id))
        action_masks = observation.get_action_masks()
        return asdict(observation) | {"action_masks": action_masks}
    
    def _get_dummy_obs(self, agent_id: str) -> Any:
        observation = Observation.build_dummy()
        action_masks = observation.get_dummy_action_masks()
        return asdict(observation) | {"action_masks": action_masks}
    
    def step(self, action_dict: dict[str, int]) -> tuple[dict, dict, dict, dict, dict]:
        player_id: PlayerId | None = GameUtil.get_next_player_id(self.game)
        if player_id is None:
            raise BridgeEnvGameAlreadyTerminalState()

        action: int = action_dict[player_id.value]
        penalty: int = 0
        try:
            Action(action).apply(self.game, player_id)
        except BizException as e:
            print(e)
            penalty = 100
        
        obs, rewards, dones, truncateds, infos = {}, {}, {}, {}, {}
        next_player_id: PlayerId | None = GameUtil.get_next_player_id(self.game)
        for agent in self.agents:
            obs[agent] = self._get_dummy_obs(agent)
            rewards[agent] = 0
            dones[agent] = False
            truncateds[agent] = False
            infos[agent] = {}

            if agent == player_id.value:
                # provide penalty for current player if any
                rewards[agent] -= penalty

            if next_player_id is not None and agent == next_player_id.value:
                # provide new observation only for the next player
                obs[agent] = self._get_obs(agent)
        
        trick_winner: PlayerId | None = GameUtil.get_trick_winner(self.game)
        if trick_winner is not None:
            # trick finished
            rewards[trick_winner.value] += 1
        
        if self.game.game_finished():
            # game finished
            dones = {agent: True for agent in self.agents}
            dones["__all__"] = True
        else:
            dones["__all__"] = False

        return obs, rewards, dones, truncateds, infos

class FlattenObservationBridgeEnv(BridgeEnv):

    def __init__(self, game: Game) -> None:
        super().__init__(game)
    
    def get_observation_space(self, agent_id: str) -> gym.Space:
        return flatten_space(super().get_observation_space(agent_id))
    
    def _get_obs(self, agent_id: str) -> Any:
        obs = flatten(super().get_observation_space(agent_id), super()._get_obs(agent_id))
        return torch.tensor(obs, dtype = torch.float32)
    
    def _get_dummy_obs(self, agent_id: str) -> Any:
        obs = flatten(super().get_observation_space(agent_id), super()._get_dummy_obs(agent_id))
        return torch.tensor(obs, dtype = torch.float32)
