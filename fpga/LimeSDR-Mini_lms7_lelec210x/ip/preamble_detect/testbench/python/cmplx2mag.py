import numpy as np
import matplotlib.pyplot as plt

N = 101
angle = np.linspace(0,1,N) * np.pi / 2.0
x = np.cos(angle)
y = np.sin(angle)

mag_est = np.zeros_like(angle)
for i in range(len(mag_est)):
  abs_i = np.abs(x[i])
  abs_q = np.abs(y[i])

  maxi = max(abs_i,abs_q)
  mini = min(abs_i,abs_q)

  mag_est[i] = maxi + (mini / 4)

print('RMSE: {:.2f}%'.format(100 * np.sum(np.square(mag_est - 1.0) / N)))
print('MAE: {:.2f}%'.format(100 * np.sum(np.abs(mag_est - 1.0)) / N))
print('Peak Error: {:.2f}%'.format(100 * np.max(np.abs(mag_est - 1.0))))

plt.figure()
plt.plot(x, y,label='trigonometric circle')
plt.plot(x * mag_est, y * mag_est,label='estimator')
plt.gca().set_aspect('equal', 'box')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.draw()

plt.figure()
plt.plot(angle, np.ones_like(angle),label='magnitude')
plt.plot(angle, mag_est, label='estimator')
plt.xlabel('angle [radian]')
plt.legend()
plt.show()
