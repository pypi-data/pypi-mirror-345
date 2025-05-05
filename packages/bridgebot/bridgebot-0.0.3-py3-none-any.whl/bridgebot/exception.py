from bridgepy.exception import BizException


class BridgeEnvGameNotReadyToStart(BizException):
    def __init__(self):
        super().__init__(11001, "Game not ready to start!")

class BridgeActionInvalid(BizException):
    def __init__(self):
        super().__init__(11002, "Invalid action!")

class BridgeEnvGameAlreadyTerminalState(BizException):
    def __init__(self):
        super().__init__(11003, "Game already terminal state!")

class BridgeObservationGameBidPhaseNotOver(BizException):
    def __init__(self):
        super().__init__(11004, "Game bid phase not over!")

class BridgeObservationGameNoBidHasBeenMade(BizException):
    def __init__(self):
        super().__init__(11005, "Game no bid has been made!")

class BridgeAgentInvalidObservationType(BizException):
    def __init__(self):
        super().__init__(11006, "Invalid observation type!")

class BridgeActionCannotChoosePartnerAsSelf(BizException):
    def __init__(self):
        super().__init__(11007, "Cannot choose partner as self!")
