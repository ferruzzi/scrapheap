import matplotlib.pyplot as plt

fig = plt.figure()


points = [
    (0, 0),
    (5, 5),
    (2, 0),
]

bar = [
    (3, 2),
    (1, 0),
    (4, 5),
]

plt.plot([points[0][0], points[1][0]], [points[0][1], points[1][1]], 'bo', linestyle="--")
plt.plot([points[1][0], points[2][0]], [points[1][1], points[2][1]], 'bo', linestyle="--")
plt.plot([points[2][0], points[0][0]], [points[2][1], points[0][1]], 'bo', linestyle="--")

plt.plot([bar[0][0], bar[1][0]], [bar[0][1], bar[1][1]], 'red', linestyle='solid')
plt.plot([bar[1][0], bar[2][0]], [bar[1][1], bar[2][1]], 'red', linestyle='solid')
plt.plot([bar[2][0], bar[0][0]], [bar[2][1], bar[0][1]], 'red', linestyle='solid')




plt.show()
