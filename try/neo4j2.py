import time

from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'snow-2158'))
session = driver.session()

# session.run('match(n) detach delete n')

time1 = time.time()

# bulk create
# for stability in range(100):
#     with session.begin_transaction() as tx:
#         for j in range(100):
#             tx.run("CREATE (a:Memory) "
#                    "SET a.stability = $stability ", stability=stability)
#         tx.commit()

time2 = time.time()
print(f'process 1 used time:{(time2 - time1) * 1000}')

session.run('match(n{stability:3})return count(n)')
time3 = time.time()
print(f'process 2 used time:{(time3 - time2) * 1000}')

session.run('match(n{stability:3})return n limit 100')
time4 = time.time()
print(f'process 3 used time:{(time4 - time3) * 1000}')

driver.close()
