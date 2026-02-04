from typing import Optional
from pydantic import BaseModel


class PlayEvent(BaseModel):
    # Core timing
    eventType: str
    startTime: str   
    endTime: str

    # Team / players
    team: Optional[str] = None
    ballCarrier: Optional[int] = None
    passer: Optional[int] = None
    receiver: Optional[int] = None
    intendedReceiver: Optional[int] = None

    # Rushing
    rushType: Optional[str] = None
    rushDirection: Optional[str] = None
    runGap: Optional[str] = None
    rushScheme: Optional[str] = None
    rushingYards: Optional[int] = None
    rushingAttemptResult: Optional[str] = None

    # Passing
    passType: Optional[str] = None
    passDirection: Optional[str] = None
    passResult: Optional[str] = None
    passAttemptResult: Optional[str] = None
    airYards: Optional[int] = None
    passingYards: Optional[int] = None
    yardsAfterCatch: Optional[int] = None
    incompletionReason: Optional[str] = None

    # Tackles
    tackleType: Optional[str] = None
    primaryTackler: Optional[int] = None
    tackler2: Optional[int] = None
    tackler3: Optional[int] = None
    tackleForLoss: Optional[bool] = None
    yardsLost: Optional[int] = None
    sack: Optional[bool] = None
    safety: Optional[bool] = None

    # Fumbles
    fumbleBy: Optional[int] = None
    fumbleCause: Optional[str] = None
    forcedFumble: Optional[bool] = None
    forcedBy: Optional[int] = None
    recoveryTeam: Optional[str] = None
    recoveredBy: Optional[int] = None
    fumbleRecoveryYards: Optional[int] = None
    recoveryTouchdown: Optional[bool] = None

    # Place kicks
    placekickType: Optional[str] = None
    placeKickDistance: Optional[int] = None
    placeKicker: Optional[int] = None
    longSnapper: Optional[int] = None
    placeKickFailedReason: Optional[str] = None
    holder: Optional[int] = None
    blockedBy: Optional[int] = None
    blockedRecoveryTeam: Optional[str] = None
    recoveryYards: Optional[int] = None
    returnedBy: Optional[int] = None
    returnYards: Optional[int] = None
    placeKickResult: Optional[str] = None
    returnTouchdown: Optional[bool] = None

    # Punts
    puntResult: Optional[str] = None
    grossPuntYardage: Optional[int] = None
    puntDirection: Optional[str] = None
    punter: Optional[int] = None
    inside20: Optional[bool] = None
    puntReturner: Optional[int] = None
    puntReturnYards: Optional[int] = None
    puntReturnTouchdown: Optional[bool] = None

    # Kickoffs
    kicker: Optional[int] = None
    kickoffType: Optional[str] = None
    kickDirection: Optional[str] = None
    kickDepth: Optional[str] = None
    kickDistance: Optional[int] = None
    kickOffResult: Optional[str] = None
    kickReturner: Optional[int] = None
    kickReturnYards: Optional[int] = None
    kickReturnTouchdown: Optional[bool] = None
    oneSideKickRecoveredBy: Optional[int] = None

    # Penalties
    timing: Optional[str] = None
    penaltyType: Optional[str] = None
    penalizedPlayer: Optional[int] = None
    penaltyChoice: Optional[str] = None
    penaltyYardage: Optional[int] = None
    enforcementSpot: Optional[str] = None
    penaltyResult: Optional[str] = None

    # Timeouts
    timeoutType: Optional[str] = None

class PlayRow(BaseModel):
    videoTitle: str
    events: list[PlayEvent]