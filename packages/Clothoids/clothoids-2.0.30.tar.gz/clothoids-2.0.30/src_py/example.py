import Clothoids
import numpy as np
import matplotlib.pyplot as plt

curve = Clothoids.ClothoidCurve("curve")
curve.build_G1(0.0, 0.0, 0.0, 4.0, 4.0, 0.0)

pydict = {"string": "Hello, World!", "number": 42}
print(curve.get_gc())
curve.set_gc(pydict)

values = np.arange(0, curve.length(), 0.01, dtype=np.float64)
points = np.zeros((values.size, 2))

for i in range(values.size):
    points[i, :] = curve.eval(values[i])

plt.plot(points[:, 0], points[:, 1])
plt.show()

curve_list = Clothoids.ClothoidList("curve_list")
interp_point_x = np.array([0.0, 1.0, 1.0, 0.0], dtype=np.float64)
interp_point_y = np.array([0.0, 0.0, 1.0, 1.0], dtype=np.float64)
curve_list.build_G1(interp_point_x, interp_point_y)

values = np.arange(0, curve_list.length(), 0.01, dtype=np.float64)
points = np.zeros((values.size, 2))

for i in range(values.size):
    points[i, :] = curve_list.eval(values[i])

plt.plot(points[:, 0], points[:, 1])
plt.show()
