import matplotlib.pyplot as plt

plt.figure()
plt.rcParams['font.sans-serif']=['SimHei']
ax = plt.subplot(111, projection='3d')

#ax.grid(linestyle='-')
ax.xaxis._axinfo["grid"]['linestyle'] = '--'
ax.yaxis._axinfo["grid"]['linestyle'] = '--'
ax.zaxis._axinfo["grid"]['linestyle'] = '--'

ax.set_xlabel('行驶距离')
ax.set_ylabel('司机报酬')
ax.set_zlabel('车辆数')

ax.set_xlim(0, 2)
ax.set_ylim(0, 2)
ax.set_zlim(0, 2)

ax.set_yticks([0,0.5,1,1.5,2])
ax.set_xticks([0,0.5,1,1.5,2])
ax.set_zticks([0,0.5,1,1.5,2])

ax.scatter3D(1,1,1,color='red')

ax.plot3D([0,0],[0,0],[0,1],color='blue')
ax.plot3D([0,0],[0,1],[0,0],color='blue')
ax.plot3D([0,1],[0,0],[0,0],color='blue')

ax.plot3D([1,0],[1,1],[1,1],color='blue')
ax.plot3D([1,1],[1,0],[1,1],color='blue')
ax.plot3D([1,1],[1,1],[1,0],color='blue')

ax.plot3D([0,1],[0,0],[1,1],color='blue')
ax.plot3D([0,0],[0,1],[1,1],color='blue')

ax.plot3D([1,0],[1,1],[0,0],color='blue')
ax.plot3D([1,1],[1,0],[0,0],color='blue')

ax.plot3D([1,1],[0,0],[0,1],color='blue')
ax.plot3D([0,0],[1,1],[0,1],color='blue')

plt.show()