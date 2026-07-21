from models import BattleEvent, EventType

be1 = BattleEvent(
    15.123,
    EventType.DAMAGE,
    "Knight",
    "Orc",
    tags={'crical', 'armor'}
)

print(be1)

# be2 = BattleEvent(
#     13.1521,
#     EventType.DEATH,
#     actor='Orc',
#     target='Unknown'
# )

# be3 = BattleEvent(
#     -13.1521,
#     EventType.DEATH,
#     actor='Orc',
#     target='Unknown'
# )

# be4 = BattleEvent(
#     13.1521,
#     EventType.DEATH,
#     actor='',
#     target='Unknown'
# )

# be5 = BattleEvent(
#     13.1521,
#     EventType.DEATH,
#     actor='Orc',
#     target=None
# )

# be6 = BattleEvent(
#     13.1521,
#     EventType.DEATH,
#     actor='Orc',
#     target='Unknown'
# )

# print(be1)
# print(be2)
# print(be2 == be1)
# print(be6 == be2)