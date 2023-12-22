import random
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from secrets import token_bytes
from typing import Any, Callable, Dict, Generator, List, Optional

from pydantic import (
    BaseModel,
    Extra,
    Field,
    PositiveFloat,
    PositiveInt,
    PrivateAttr,
    conint,
    constr,
    errors,
    root_validator,
    validator,
)

DEFAULT_CONFIG_PATH = Path(".config.json")


class GroupConfig(BaseModel):
    key: constr(min_length=1, max_length=128)
    name: constr(min_length=1, max_length=128)
    admin: bool = False


class Status(str, Enum):
    correct = "correct"
    incorrect = "incorrect"
    correct_penalized = "correct_penalized"
    incorrect_penalized = "incorrect_penalized"


class Guess(str, Enum):
    birds = "birds"
    chainsaw = "chainsaw"
    fire = "fire"
    handsaw = "handsaw"
    helicopter = "helicopter"
    nothing = "nothing"
    received = "received"
    penalized = "penalized"

    @classmethod
    def possible_values(self):
        return [
            guess
            for guess in Guess
            if guess not in [Guess.nothing, Guess.received, Guess.penalized]
        ]


class Answer(BaseModel):
    guess: Guess
    status: Status = Status.incorrect
    hide: bool = False


class Submission(BaseModel):
    """Holds /submit request from a given group."""

    timestamp: datetime = Field(default_factory=datetime.now)
    round: conint(ge=0)
    lap: conint(ge=0)
    key: str
    guess: Guess
    penalized: bool = False


class RoundConfig(BaseModel):
    name: str = ""
    lap_count: PositiveInt = 16
    lap_duration: PositiveFloat = 13.0
    only_check_for_presence: bool = False
    with_noise: bool = False


def hex_bytes_validator(val: Any) -> bytes:
    if isinstance(val, bytes):
        return val
    elif isinstance(val, bytearray):
        return bytes(val)
    elif isinstance(val, str):
        return bytes.fromhex(val)
    raise errors.BytesError()


class HexBytes(bytes):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., Any], None, None]:
        yield hex_bytes_validator


class SecurityRound(BaseModel):
    key: HexBytes = HexBytes(token_bytes(16))


class SecurityGuess(BaseModel):
    time: str  # Pretty formatted HH:MM time
    score: conint(ge=0, le=100)  # Score is a percentage (integer)
    traces: int  # Number of traces


class RoundsConfig(BaseModel):
    rounds: List[RoundConfig] = [
        RoundConfig(name="Functionality", only_check_for_presence=True),
        RoundConfig(name="Communication range", only_check_for_presence=True),
        RoundConfig(name="Power consumption", only_check_for_presence=True),
        RoundConfig(name="Classification accuracy"),
        RoundConfig(name="Classification robustness", with_noise=True),
    ]
    security_round: SecurityRound = SecurityRound()
    seed: PositiveInt = 1234
    start_paused: bool = True
    restart_when_finished: bool = False
    pause_between_rounds = True
    latency_margin: PositiveFloat = 1.0
    delay_before_playing: PositiveFloat = 2.0
    delay_after_playing: PositiveFloat = 1.0
    sound_duration: PositiveFloat = 5.0
    __answers: List[List[Guess]] = PrivateAttr()
    __play_delays: List[List[PositiveFloat]] = PrivateAttr()
    __round_start_time: float = PrivateAttr()
    __time_when_paused: float = PrivateAttr()
    __paused: bool = PrivateAttr()
    __current_round: conint(ge=0) = PrivateAttr()
    __current_lap: conint(ge=0) = PrivateAttr()
    __finished: bool = PrivateAttr()
    __submissions: List[Submission] = PrivateAttr([])
    __security_round_submissions: Dict[str, SecurityGuess] = PrivateAttr({})
    __await_next_round: bool = PrivateAttr(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        random.seed(self.seed)

    @root_validator
    def validate_timing(cls, values):
        rounds = values.get("rounds")
        latency_margin = values.get("latency_margin")
        delay_before_playing = values.get("delay_before_playing")
        delay_after_playing = values.get("delay_after_playing")
        sound_duration = values.get("sound_duration")
        total = (
            latency_margin + delay_before_playing + delay_after_playing + sound_duration
        )

        for round_config in rounds:
            lap_duration = round_config.lap_duration
            assert (
                lap_duration >= total
            ), f"Lap duration is not long enough: {lap_duration} is shorted than {total}"

        return values

    def add_security_round_submission(self, key: str, guess: bytes, traces: int):
        """
        Adds a new submission to the security round.
        """
        correct = bytearray(self.security_round.key)
        guess = bytearray(guess)

        score = 0
        for left, right in zip(correct[::-1], guess[::-1]):
            if left == right:
                score += 1

        score = int(100 * (score / len(correct)))

        self.__security_round_submissions[key] = SecurityGuess(
            score=score, traces=traces, time=time.strftime("%H:%M:%S")
        )

    def get_security_round_submission(self, key: str) -> Optional[SecurityGuess]:
        """
        Returns the security round submission by the given group.
        """
        return self.__security_round_submissions.get(key, None)

    def add_submission(self, submission: Submission):
        """
        Adds a new submissions to the list.
        """
        self.__submissions.append(submission)

    def get_submissions(
        self, key: str, round: Optional[int], lap: Optional[int]
    ) -> List[Guess]:
        """
        Returns the guesses submitted by a group for a given round and lap.

        If no guesses were submitted, [Guess.nothing] is returned.

        Guesses are sorted with earliest first, oldest last.
        """
        guesses = (
            submissions.guess
            for submissions in self.__submissions[::-1]
            if submissions.key == key
            and (submissions.round == round or round is None)
            and (submissions.lap == lap or lap is None)
        )

        return list(guesses) or [Guess.nothing]

    def get_submissions_as_dict(
        self, key: str, round: Optional[int], lap: Optional[int]
    ) -> List[dict]:
        """
        Returns the submissions as dictonaries by a group for a given round and lap.
        """
        return list(
            submissions.dict()
            for submissions in self.__submissions
            if submissions.key == key
            and (submissions.round == round or round is None)
            and (submissions.lap == lap or lap is None)
        )

    def delete_submissions(self, key: str, round: Optional[int], lap: Optional[int]):
        """
        Deletes the guesses submitted by a group for a given round and lap.
        """
        self.__submissions = [
            submissions
            for submissions in self.__submissions
            if submissions.key != key
            and submissions.round != round
            and submissions.lap != lap
        ]

    def get_last_submission(self, key: str, round: int, lap: int) -> Guess:
        """
        Returns the last guess submitted by a group for a given round and lap.

        If no guesses were submitted, Guess.nothing is returned.
        """
        guesses = (
            submissions.guess
            for submissions in self.__submissions[::-1]
            if submissions.key == key
            and submissions.round == round
            and submissions.lap == lap
        )

        return next(guesses, Guess.nothing)

    def is_penalized(self, key: str, round: int, lap: int) -> bool:
        """
        Returns true if a group was penalized for a given round and lap.
        """
        return any(
            submissions.penalized
            for submissions in self.__submissions
            if submissions.key == key
            and submissions.round == round
            and submissions.lap == lap
        )

    def restart(self):
        self.__submissions.clear()

        possibles_answers = Guess.possible_values()

        self.__answers = [
            random.choices(possibles_answers, k=round_config.lap_count)
            for round_config in self.rounds
        ]
        total = (
            self.latency_margin
            + self.delay_before_playing
            + self.delay_after_playing
            + self.sound_duration
        )
        start = self.delay_before_playing

        self.__play_delays = [
            [
                start + random.random() * (round_config.lap_duration - total)
                for _ in range(round_config.lap_count)
            ]
            for round_config in self.rounds
        ]

        self.__round_start_time = time.time()
        self.__time_when_paused = self.__round_start_time
        self.__paused = True
        self.__current_round = 0
        self.__finished = False

        if not self.start_paused:
            self.play()

    def time(self) -> float:
        if self.__paused:
            return self.__time_when_paused

        return time.time()

    def get_current_round_config(self) -> RoundConfig:
        return self.rounds[self.get_current_round()]

    def get_current_time_within_lap(self) -> float:
        elapsed = self.time() - self.__round_start_time
        lap_duration = self.get_current_round_config().lap_duration

        return elapsed % lap_duration

    def get_current_play_delay(self) -> float:
        return self.__play_delays[self.get_current_round()][self.get_current_lap()]

    def accepts_submissions(self) -> bool:
        current_time = self.get_current_time_within_lap()
        current_play_delay = self.get_current_play_delay()

        return (
            current_play_delay
            <= current_time
            <= current_play_delay + self.sound_duration + self.latency_margin
        )

    def play(self):
        if not self.__paused:
            return

        self.__await_next_round = False
        self.__round_start_time += time.time() - self.__time_when_paused
        self.__paused = False

    def pause(self):
        if self.__paused:
            return

        self.__time_when_paused = time.time()
        self.__paused = True

    def get_current_round(self) -> int:
        if self.__await_next_round:
            return self.__current_round - 1
        else:
            return self.__current_round

    def get_current_lap(self) -> int:
        if self.__await_next_round:
            return self.get_current_number_of_laps() - 1

        elapsed = self.time() - self.__round_start_time
        lap_duration = self.rounds[self.get_current_round()].lap_duration

        current_lap = elapsed // lap_duration

        if current_lap >= self.get_current_number_of_laps():
            if self.get_current_round() + 1 == self.get_number_of_rounds():
                if self.restart_when_finished:
                    self.restart()
                    return 0
                else:
                    self.__finished = True
                    self.pause()
                    return self.get_current_number_of_laps() - 1
            else:
                self.__current_round += 1
                self.__round_start_time = time.time()

                if self.pause_between_rounds:
                    self.__await_next_round = True
                    self.pause()
                    return self.get_current_number_of_laps() - 1

                return 0  # First lap of next round

        return int(current_lap)

    def get_current_correct_guess(self) -> Guess:
        return self.__answers[self.get_current_round()][self.get_current_lap()]

    def get_number_of_rounds(self) -> int:
        return len(self.rounds)

    def get_current_number_of_laps(self) -> int:
        return self.rounds[self.get_current_round()].lap_count

    def get_current_round_answers(self) -> List[Guess]:
        return self.__answers[self.get_current_round()]

    def is_paused(self) -> bool:
        return self.__paused

    def time_before_next_lap(self) -> float:
        if self.__finished or self.__await_next_round:
            return 0.0

        elapsed = self.time() - self.__round_start_time
        lap_duration = self.rounds[self.get_current_round()].lap_duration

        return lap_duration - elapsed % lap_duration

    def time_before_playing(self) -> float:
        if self.__finished:
            return -1.0

        elapsed = self.time() - self.__round_start_time
        lap_duration = self.rounds[self.get_current_round()].lap_duration
        play_delay = self.get_current_play_delay()

        return play_delay - elapsed % lap_duration

    def is_finished(self) -> bool:
        return self.__finished


class LeaderboardRow(BaseModel):
    name: str
    answers: List[Answer]
    score: float
    security_round: Optional[SecurityGuess]


class LeaderboardStatus(BaseModel):
    round_name: str
    current_correct_guess: Guess
    current_with_noise: bool
    current_round: conint(ge=0)
    current_lap: conint(ge=0)
    number_of_rounds: conint(ge=0)
    number_of_laps: conint(ge=0)
    paused: bool
    time_before_next_lap: float
    time_before_playing: float
    finished: bool
    leaderboard: List[LeaderboardRow]

    class Config:
        extra = Extra.forbid


class Config(BaseModel):
    group_configs: List[GroupConfig] = []
    rounds_config: RoundsConfig = RoundsConfig()

    class Config:
        extra = Extra.forbid
        json_encoders = {bytes: lambda bs: bs.hex()}

    @validator("group_configs")
    def unique_names_and_keys(cls, v):
        keys = set()
        names = set()

        for group_config in v:
            key = group_config.key
            name = group_config.name

            if key in keys:
                raise ValueError(f"duplicate key found: `{key}`")
            keys.add(key)

            if name in names:
                raise ValueError(f"duplicate name found: `{name}`")
            names.add(name)

        return v

    def clear(self):
        self.__submissions.clear()

    def save_to(self, path: str):
        with open(path, "w") as f:
            f.write(self.json(indent=2))

    def get_group_by_name(self, name: str) -> GroupConfig:
        try:
            return next(
                filter(
                    lambda group_config: group_config.name == name, self.group_configs
                )
            )
        except StopIteration:
            raise IndexError(f"name `{name}` not found")

    def get_group_by_key(self, key: str) -> GroupConfig:
        try:
            return next(
                filter(lambda group_config: group_config.key == key, self.group_configs)
            )
        except StopIteration:
            raise IndexError(f"key `{key}` not found")

    def get_leaderboard_status(self) -> LeaderboardStatus:
        current_correct_guess = self.rounds_config.get_current_correct_guess()
        current_with_noise = self.rounds_config.get_current_round_config().with_noise
        current_round = self.rounds_config.get_current_round()
        current_lap = self.rounds_config.get_current_lap()
        number_of_rounds = self.rounds_config.get_number_of_rounds()
        number_of_laps = self.rounds_config.get_current_number_of_laps()
        paused = self.rounds_config.is_paused()
        time_before_next_lap = self.rounds_config.time_before_next_lap()
        time_before_playing = self.rounds_config.time_before_playing()
        finished = self.rounds_config.is_finished()

        correct_answers = self.rounds_config.get_current_round_answers()

        rows = []
        for group_config in self.group_configs:
            answers = []
            score = 0.0
            for lap, correct_answer in enumerate(correct_answers):
                # Getting last submission
                guess = self.rounds_config.get_last_submission(
                    group_config.key, current_round, lap
                )

                if self.rounds_config.get_current_round_config().only_check_for_presence:
                    if guess != Guess.nothing:
                        guess = Guess.received
                        correct = True
                    else:
                        correct = False
                else:
                    correct = guess == correct_answer

                if correct:
                    status = Status.correct
                    score += 1.0
                else:
                    status = Status.incorrect

                if self.rounds_config.is_penalized(
                    group_config.key, current_round, lap
                ):
                    score -= 0.5

                    if correct:
                        status = Status.correct_penalized
                    else:
                        status = Status.incorrect_penalized

                hide = lap > current_lap

                answers.append(Answer(guess=guess, status=status, hide=hide))

            rows.append(
                LeaderboardRow(
                    name=group_config.name,
                    answers=answers,
                    score=score,
                    security_round=self.rounds_config.get_security_round_submission(
                        group_config.key
                    ),
                )
            )

        return LeaderboardStatus(
            round_name=self.rounds_config.get_current_round_config().name,
            current_correct_guess=current_correct_guess,
            current_with_noise=current_with_noise,
            current_round=current_round,
            current_lap=current_lap,
            number_of_rounds=number_of_rounds,
            number_of_laps=number_of_laps,
            paused=paused,
            time_before_next_lap=time_before_next_lap,
            time_before_playing=time_before_playing,
            finished=finished,
            leaderboard=rows,
        )
