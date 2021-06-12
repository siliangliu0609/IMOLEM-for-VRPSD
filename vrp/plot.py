import os
import pickle
import matplotlib.pyplot as plt

from . import util


def plot_trace(datamaps, modes, labels, titles, save, trace, linestyles):
    for datamap in datamaps:
        print('ploting {}'.format(datamap))

        if not os.path.exists('pic/'+datamap):
            os.mkdir('pic/'+datamap)

        datafiles = []
        for mode in modes:
            datafiles.append('result/{}/{}_trace_{}.txt'.format(datamap, mode, trace))

        trace_lists = []
        for datafile in datafiles:
            f = open(datafile)
            trace_lists.append([])
            for line in f:
                trace_lists[-1].append(tuple(float(x) for x in line.split()))

        axs = []
        for i in range(len(save)):
            plt.figure(datamap+str(i))
            axs.append(plt.subplot())
            axs[i].set_title(titles[i])

        #avg_routes, avg_distance, avg_pay, hv, spacing
        for i in range(len(datafiles)):
            axs[0].plot([x[0] for x in trace_lists[i]], label=labels[i], linestyle=linestyles[i])
            axs[1].plot([x[1] for x in trace_lists[i]], label=labels[i], linestyle=linestyles[i])
            axs[2].plot([x[2] for x in trace_lists[i]], label=labels[i], linestyle=linestyles[i])
            axs[3].plot([x[0]*x[1]*x[2] for x in trace_lists[i]], label=labels[i], linestyle=linestyles[i])
            axs[4].plot([x[1]*x[2] for x in trace_lists[i]], label=labels[i], linestyle=linestyles[i])

        for ax in axs:
            ax.legend()

        for i in range(len(save)):
            plt.figure(datamap+str(i))
            plt.tight_layout()
            plt.savefig('pic/{}/{}_{}.png'.format(datamap, datamap, save[i]))
            plt.close()

    # plt.show()


def plot_population_trace(datamaps, modes):
    for datamap in datamaps:

        if not os.path.exists('pic/'+datamap):
            os.mkdir('pic/'+datamap)
        if not os.path.exists('pic/'+datamap+'/allp'):
            os.mkdir('pic/'+datamap+'/allp')

        for mode in modes:
            print('ploting {} {}'.format(datamap, mode))

            Qf = open('result/{}/{}_population_trace.pickle'.format(datamap, mode), 'rb')
            Q_trace = pickle.load(Qf)

            V = []
            D = []
            R = []
            for Q in Q_trace[:-1]:
                for plan in Q:
                    V.append(len(plan.routes))
                    D.append(plan.distance)
                    R.append(plan.pay)
            V_last = []
            D_last = []
            R_last = []
            for plan in Q_trace[-1]:
                V_last.append(len(plan.routes))
                D_last.append(plan.distance)
                R_last.append(plan.pay)

            plt.figure(datamap+mode+'0')
            ax = plt.axes(projection='3d')
            ax.scatter3D(V, D, R, s=5)
            ax.scatter3D(V_last, D_last, R_last, s=10, color='r')
            ax.set_xlabel('Number of vehicles')
            ax.set_ylabel('Travel distance')
            ax.set_zlabel('Driver remuneration')
            plt.tight_layout()
            plt.savefig('pic/{}/allp/{}_{}_allp_3d.png'.format(datamap, datamap, mode))
            plt.close()

            plt.figure(datamap+mode+'1')
            ax = plt.subplot()
            ax.scatter(D, R, s=5)
            ax.scatter(D_last, R_last, s=10, color='r')
            ax.set_xlabel('Travel distance')
            ax.set_ylabel('Driver remuneration')
            plt.tight_layout()
            plt.savefig('pic/{}/allp/{}_{}_allp_2d_DR.png'.format(datamap, datamap, mode))
            plt.close()

            plt.figure(datamap+mode+'2')
            ax = plt.subplot()
            ax.scatter(D, V, s=5)
            ax.scatter(D_last, V_last, s=10, color='r')
            ax.set_xlabel('Travel distance')
            ax.set_ylabel('Number of Vehicles')
            plt.tight_layout()
            plt.savefig('pic/{}/allp/{}_{}_allp_2d_DV.png'.format(datamap, datamap, mode))
            plt.close()

            plt.figure(datamap+mode+'3')
            ax = plt.subplot()
            ax.scatter(R, V, s=5)
            ax.scatter(R_last, V_last, s=10, color='r')
            ax.set_xlabel('Driver remuneration')
            ax.set_ylabel('Number of Vehicles')
            plt.tight_layout()
            plt.savefig('pic/{}/allp/{}_{}_allp_2d_RV.png'.format(datamap, datamap, mode))
            plt.close()

            # plt.show()


def plot_population_last(datamaps, modes):
    for datamap in datamaps:

        if not os.path.exists('pic/'+datamap):
            os.mkdir('pic/'+datamap)
        if not os.path.exists('pic/'+datamap+'/lastp'):
            os.mkdir('pic/'+datamap+'/lastp')

        for mode in modes:
            print('ploting {} {}'.format(datamap, mode))

            Qf = open('result/{}/{}_population.pickle'.format(datamap, mode), 'rb')
            Q = pickle.load(Qf)
            Q_first = util.pareto_first(Q)
            for plan in Q_first:
                Q.remove(plan)

            V = []
            D = []
            R = []
            for plan in Q:
                V.append(len(plan.routes))
                D.append(plan.distance)
                R.append(plan.pay)
            V_first = []
            D_first = []
            R_first = []
            for plan in Q_first:
                V_first.append(len(plan.routes))
                D_first.append(plan.distance)
                R_first.append(plan.pay)

            plt.figure(datamap+mode+'0')
            ax = plt.axes(projection='3d')
            ax.scatter3D(V, D, R, marker='x', color='b', s=10)
            ax.scatter3D(V_first, D_first, R_first, marker='o', color='r', s=10)
            ax.set_xlabel('Number of vehicles')
            ax.set_ylabel('Travel distance')
            ax.set_zlabel('Driver remuneration')
            plt.tight_layout()
            plt.savefig('pic/{}/lastp/{}_{}_lastp_3d.png'.format(datamap, datamap, mode))
            plt.close()

            plt.figure(datamap+mode+'1')
            ax = plt.subplot()
            ax.scatter(D, R, marker='x', color='b')
            ax.scatter(D_first, R_first, marker='o', color='r')
            ax.set_xlabel('Travel distance')
            ax.set_ylabel('Driver remuneration')
            plt.tight_layout()
            plt.savefig('pic/{}/lastp/{}_{}_lastp_2d_DR.png'.format(datamap, datamap, mode))
            plt.close()

            plt.figure(datamap+mode+'2')
            ax = plt.subplot()
            ax.scatter(D, V, marker='x', color='b')
            ax.scatter(D_first, V_first, marker='o', color='r')
            ax.set_xlabel('Travel distance')
            ax.set_ylabel('Number of Vehicles')
            plt.tight_layout()
            plt.savefig('pic/{}/lastp/{}_{}_lastp_2d_DV.png'.format(datamap, datamap, mode))
            plt.close()

            plt.figure(datamap+mode+'3')
            ax = plt.subplot()
            ax.scatter(R, V, marker='x', color='b')
            ax.scatter(R_first, V_first, marker='o', color='r')
            ax.set_xlabel('Driver remuneration')
            ax.set_ylabel('Number of Vehicles')
            plt.tight_layout()
            plt.savefig('pic/{}/lastp/{}_{}_lastp_2d_RV.png'.format(datamap, datamap, mode))
            plt.close()

            # plt.show()
