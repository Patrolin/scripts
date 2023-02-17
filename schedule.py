from dataclasses import dataclass

time = 0.0

@dataclass
class Process:
    last_run: float
    duration: float
    period: float

    def should_run(self) -> bool:
        return time >= self.last_run + self.period

processes = [Process(0, 0.002, 0.5), Process(0, 0.015, 1 / 60)]

def schedule() -> Process | None:
    acc = None
    for p in processes:
        if p.should_run() and (acc == None or p.duration < acc.duration):
            acc = p
    return acc

def run(seconds: float):
    global time
    while time < seconds:
        p = schedule()
        if p:
            print(p)
            p.last_run = time
            time += p.duration
        else:
            time += 0.001

if __name__ == "__main__":
    run(33 / 60)
