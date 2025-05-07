#-------------------------------------------------------------------------------
# file: src/cryptolion/exits.py
#-------------------------------------------------------------------------------
from core.exits import (
    ChandelierExit,
    ProfitTargetExit,
    RSIExit,
    TimeExit,
)
from core.exits_atr import ATRStopExit

# alias expected by tests
TakeProfitExit = ProfitTargetExit