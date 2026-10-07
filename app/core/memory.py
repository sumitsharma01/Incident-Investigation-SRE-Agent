from dataclasses import dataclass, field


@dataclass
class InvestigationMemory:
    service: str
    description: str
    observations: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add_observation(self, observation: str) -> None:
        self.observations.append(observation)

    def add_note(self, note: str) -> None:
        self.notes.append(note)
