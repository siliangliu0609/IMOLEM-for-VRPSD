import math
import random
import numpy as np


class Evo_param:
    def __init__(self, size, maxiter, N=10, trace=False, MOmode='DRV', spec_init=True, spec_inst=True, no_tree=False):
        self.size = size
        self.maxiter = maxiter
        self.N = N
        self.trace = trace
        self.MOmode = MOmode
        self.spec_init = spec_init
        self.spec_inst = spec_inst
        self.no_tree = no_tree


class Problem:
    def __init__(self, map_file, map_type, normal_hours=8, normal_salary=10, over_salary=20, standard_deviation_file=None, standard_deviation_target=None, customers=None, capacity=None, time_bound=None, name=None):
        self.map_file = map_file
        self.map_type = map_type
        self.standard_deviation_file = standard_deviation_file
        self.standard_deviation_target = standard_deviation_target

        self.customers = customers
        self.capacity = capacity
        self.time_bound = time_bound

        self.normal_hours = normal_hours
        self.normal_salary = normal_salary
        self.over_salary = over_salary

        self.name = name

    def __read_standard_deviation(self):
        fp = open(self.standard_deviation_file)
        for line in fp.readlines():
            if line.split()[0] == self.standard_deviation_target:
                sd = [float(x) for x in line.split()[1:]]
                return sd
        fp.close()
        assert('no standard deviation instance for {}'.format(self.standard_deviation_target))

    def __read_solomon_data(self):
        fp = open(self.map_file)
        sd = self.__read_standard_deviation()
        self.customers = []
        for num, line in enumerate(fp.readlines()):
            if num == 4:
                self.capacity = int(line.split()[1])
            if num <= 8:  # 跳过无关行
                continue
            cus_no, x_coord, y_coord, demand, _, due_date, service_time = [float(x) for x in line.split()]
            # if cus_no == 11:
            #   break
            # if cus_no == 0:
            #    self.time_bound = 0.8*due_date
            if cus_no == 0:
                service_time = 10
            else:
                service_time = demand-10 if demand-10 >= 1 else 1
            standard_deviation = sd[int(cus_no)]
            cus = Customer(int(cus_no), x_coord, y_coord, demand, standard_deviation, service_time)
            self.customers.append(cus)
        self.time_bound = math.ceil(self.cal_time_bound())
        fp.close()

    def __read_dt86_data(self):
        fp = open(self.map_file)
        self.time_bound = 212
        self.customers = []
        for num, line in enumerate(fp.readlines()):
            if num == 0:
                self.capacity = int(line.strip())
            if num <= 1:  # 跳过无关行
                continue
            cus_no, x_coord, y_coord, demand, variance = [float(x) for x in line.split()]
            if cus_no == 0:
                service_time = 10
            else:
                service_time = demand-10 if demand-10 >= 1 else 1
            cus = Customer(int(cus_no), x_coord, y_coord, demand, variance**0.5, service_time)
            self.customers.append(cus)
        fp.close()

    def read_data(self):
        if self.map_type == 'dt86':
            self.__read_dt86_data()
        elif self.map_type == 'solomon':
            self.__read_solomon_data()
        else:
            assert('wrong map type')

    def cal_time_bound(self, show=False):
        xs = []
        ys = []

        for cus in self.customers:
            xs.append(cus.x)
            ys.append(cus.y)

        max_x = max(xs)
        max_y = max(ys)

        double_diagonal = (max_x**2+max_y**2)**0.5*2

        if show:
            print('max_x = {}\nmax_y = {}\ndouble_diagonal = {}'.format(max_x, max_y, double_diagonal))
        return double_diagonal


class Customer:
    def __init__(self, id, x, y, mean, standard_deviation, servicetime):
        self.id = id
        self.x = x
        self.y = y
        self.mean = mean
        self.standard_deviation = standard_deviation
        self.servicetime = servicetime

    def __repr__(self):
        return "customer {} at {}".format(self.id, id(self))

    def __str__(self):
        return "{}".format(self.id)

    def generate_actual_demand(self, N):
        self.actual_demand = np.random.normal(self.mean, self.standard_deviation, N)
        for i in range(N):
            if self.actual_demand[i] < 0.1:
                self.actual_demand[i] = 0.1

    def get_distance(self, other):
        return ((self.x-other.x)**2+(self.y-other.y)**2)**0.5


class Route:
    def __init__(self, customer_list, restock_time=None):
        self.customer_list = customer_list[:]
        self.restock_time = restock_time
        self.set_mean_demand()

    def __repr__(self):
        retstr = 'Route: '+' -> '.join([str(cus) for cus in self.customer_list])
        if self.restock_time != None:
            return retstr+' , restock time={}'.format(self.restock_time)
        else:
            return retstr

    def __getitem__(self, i):
        return self.customer_list[i]

    def copy(self):
        # 这里使用copy.deepcopy会导致客户内容也被复制
        new_route = type(self)(self.customer_list, self.restock_time)  # list没有复制是因为构造时会复制，复制到客户引用即可，不必复制客户内容
        return new_route

    def rand_seg_copy(self):
        while True:
            start = random.randint(1, len(self.customer_list)-2)
            end = random.randint(start+1, len(self.customer_list)-1)
            if start == 1 and end == len(self.customer_list)-1:
                continue
            break
        new_route_customerlist = [self.customer_list[0]]+self.customer_list[start:end]+[self.customer_list[0]]
        new_route = type(self)(new_route_customerlist)
        return new_route

    def set_mean_demand(self):
        self.actual_demand_list = []
        for customer in self.customer_list:
            self.actual_demand_list.append(customer.mean)

    def set_one_actual_demand(self, i):
        self.actual_demand_list = []
        for customer in self.customer_list:
            self.actual_demand_list.append(customer.actual_demand[i])

    def distance_time_consume(self, problem, show=False):
        sum_distance = 0
        sum_time = 0
        restock_time = 0
        remain_goods = problem.capacity
        now = 0
        goto = 1
        while goto < len(self.customer_list):
            if self.actual_demand_list[goto] < remain_goods:
                sum_distance += self.customer_list[goto].get_distance(self.customer_list[now])
                sum_time += self.customer_list[goto].get_distance(self.customer_list[now])+self.customer_list[goto].servicetime
                remain_goods -= self.actual_demand_list[goto]
                if show:
                    print("from {} to {},remain:{}".format(now, goto, remain_goods))
                now = goto
                goto += 1
            elif self.actual_demand_list[goto] == remain_goods:
                sum_distance += self.customer_list[goto].get_distance(self.customer_list[now])+self.customer_list[goto].get_distance(self.customer_list[0])
                sum_time += self.customer_list[goto].get_distance(self.customer_list[now])+self.customer_list[goto].servicetime+self.customer_list[goto].get_distance(self.customer_list[0])+self.customer_list[0].servicetime
                remain_goods = problem.capacity
                if show:
                    print("from {} to {},remain:{}".format(now, goto, 0))
                    print("from {} to {},remain:{}".format(goto, 0, problem.capacity))
                now = 0
                restock_time += 1
                goto += 1
            else:
                sum_distance += self.customer_list[goto].get_distance(self.customer_list[now])+self.customer_list[goto].get_distance(self.customer_list[0])
                sum_time += self.customer_list[goto].get_distance(self.customer_list[now])+self.customer_list[goto].servicetime+self.customer_list[goto].get_distance(self.customer_list[0])+self.customer_list[0].servicetime
                self.actual_demand_list[goto] -= remain_goods
                remain_goods = problem.capacity
                if show:
                    print("from {} to {},remain:{}".format(now, goto, 0))
                    print("from {} to {},remain:{}".format(goto, 0, problem.capacity))
                now = 0
                restock_time += 1
                # goto不变，因为需要回去继续服务
        #self.restock_time = restock_time
        return sum_distance, sum_time, restock_time

    def pay_consume(self, problem):
        _, time_consume, *_ = self.distance_time_consume(problem)
        if time_consume <= problem.time_bound:
            pay = problem.normal_hours/problem.time_bound*time_consume*problem.normal_salary
        else:
            pay = problem.normal_hours*problem.normal_salary+(problem.normal_hours/problem.time_bound*time_consume-problem.normal_hours)*problem.over_salary
        return pay

    def find_customer(self, cus_ids):
        for cus in self.customer_list:
            if cus.id in cus_ids:
                return cus
        return None

    def random_shuffle(self):
        tmp = self.customer_list[1:-1]
        random.shuffle(tmp)
        self.customer_list = [self.customer_list[0]]+tmp+[self.customer_list[0]]

    def cal_restock_time_with_mean_demand(self, problem):
        backup = self.actual_demand_list[:]
        self.set_mean_demand()
        *_, restock_time = self.distance_time_consume(problem)
        self.restock_time = restock_time
        self.actual_demand_list = backup


class Plan:
    def __init__(self, routes, distance=None, pay=None):
        self.routes = routes[:]

        self.distance = distance
        self.pay = pay

    def copy(self):
        return type(self)([route.copy() for route in self.routes], self.distance, self.pay)

    def __repr__(self):
        num = len(self.routes)
        retstr = 'Plan: 1 route' if num == 1 else 'Plan: {} routes'.format(num)
        for route in self.routes:
            retstr += '\n'+' '*4+str(route)
        retstr += '\ndistance={}\npay={}'.format(self.distance, self.pay)
        return retstr

    def __getitem__(self, i):
        return self.routes[i]

    def arrange(self):
        self.routes = sorted(self.routes, key=lambda route: route.customer_list[1].id)

    def arrange_dis(self):
        self.routes = sorted(self.routes, key=lambda route: route.customer_list[1].dis_index, reverse=True)

    def equal(self, other):
        if len(self.routes) != len(other.routes):
            return False
        self.arrange()
        other.arrange()
        for self_route, other_route in zip(self.routes, other.routes):
            for sel_cus, oth_cus in zip(self_route.customer_list, other_route.customer_list):
                if sel_cus.id != oth_cus.id:
                    return False
        return True

    def equal_objective(self, other):
        if len(self.routes) == len(other.routes) and self.pay == other.pay and self.distance == other.distance:
            return True
        else:
            return False

    def local_search_exploitation_SPS(self, problem):
        for route in self.routes:
            route.set_mean_demand()
        for index, route in enumerate(self.routes):
            old_distance, *_ = route.distance_time_consume(problem)
            new_route_customer_list = route.customer_list[1:-1]
            new_route_customer_list = sorted(new_route_customer_list, key=lambda customer: customer.get_distance(route.customer_list[0]), reverse=True)
            new_route_customer_list = [route.customer_list[0]]+new_route_customer_list+[route.customer_list[0]]
            new_route = Route(new_route_customer_list)
            new_distance, *_ = new_route.distance_time_consume(problem)
            if new_distance < old_distance:
                self.routes[index] = new_route

    def local_search_exploitation_WDS(self, problem):
        for route in self.routes:
            route.set_mean_demand()
        for index, route in enumerate(self.routes):
            old_distance, *_ = route.distance_time_consume(problem)
            new_route_customer_list = route.customer_list[:]
            new_route_customer_list.reverse()
            new_route = Route(new_route_customer_list)
            new_distance, *_ = new_route.distance_time_consume(problem)
            if new_distance < old_distance:
                self.routes[index] = new_route

    def __remove_duplicated_customers(self, base):
        del_cus_id = []
        for customer in self.routes[base].customer_list[1:-1]:
            del_cus_id.append(customer.id)
        for route in self.routes[:-1]:
            while route.find_customer(del_cus_id):
                route.customer_list.remove(route.find_customer(del_cus_id))
                if len(route.customer_list) == 2:
                    self.routes.remove(route)

    def route_crossover(self, other_plan, random_shuffling_rate):
        if len(self.routes) != 1:
            r1 = self.routes[random.randint(0, len(self.routes)-1)].copy()
        else:
            r1 = self.routes[0].rand_seg_copy()
        if len(other_plan.routes) != 1:
            r2 = other_plan.routes[random.randint(0, len(other_plan.routes)-1)].copy()
        else:
            r2 = other_plan.routes[0].rand_seg_copy()
        self.routes.append(r2)
        other_plan.routes.append(r1)
        self.__remove_duplicated_customers(-1)
        other_plan.__remove_duplicated_customers(-1)

        for route in self.routes:
            if len(route.customer_list) == 2:
                self.routes.remove(route)
        for route in other_plan.routes:
            if len(route.customer_list) == 2:
                other_plan.routes.remove(route)

        for i in range(len(self.routes)-1):
            if random.random() < random_shuffling_rate:
                self.routes[i].random_shuffle()
        for i in range(len(other_plan.routes)-1):
            if random.random() < random_shuffling_rate:
                other_plan.routes[i].random_shuffle()
        #self.routes[random.randint(0, len(self.routes)-1)].random_shuffle()
        #other_plan.routes[random.randint(0, len(other_plan.routes)-1)].random_shuffle()

    def __partial_swap(self):
        if len(self.routes) == 1:
            return
        swap_route_1 = random.randint(0, len(self.routes)-1)
        swap_route_2 = random.randint(0, len(self.routes)-1)
        while swap_route_2 == swap_route_1:
            swap_route_2 = random.randint(0, len(self.routes)-1)

        route_1_part_start = random.randint(1, len(self.routes[swap_route_1].customer_list)-2)
        route_1_part_end = random.randint(2, len(self.routes[swap_route_1].customer_list)-1)
        while route_1_part_end <= route_1_part_start:
            route_1_part_end = random.randint(2, len(self.routes[swap_route_1].customer_list)-1)
        route_2_part_start = random.randint(1, len(self.routes[swap_route_2].customer_list)-2)
        route_2_part_end = random.randint(2, len(self.routes[swap_route_2].customer_list)-1)
        while route_2_part_end <= route_2_part_start:
            route_2_part_end = random.randint(2, len(self.routes[swap_route_2].customer_list)-1)

        tmp = self.routes[swap_route_1].customer_list[route_1_part_start:route_1_part_end]
        self.routes[swap_route_1].customer_list[route_1_part_start:route_1_part_end] = self.routes[swap_route_2].customer_list[route_2_part_start:route_2_part_end]
        self.routes[swap_route_2].customer_list[route_2_part_start:route_2_part_end] = tmp

    def __merge_shortest_route(self, problem):
        if len(self.routes) == 1:
            return
        for route in self.routes:
            route.set_mean_demand()
        sorted_routes = sorted(self.routes, key=lambda route: route.distance_time_consume(problem)[0])
        sorted_routes[0].customer_list.pop(-1)
        sorted_routes[1].customer_list.pop(0)
        sorted_routes[0].customer_list.extend(sorted_routes[1].customer_list)
        self.routes.remove(sorted_routes[1])

    def __split_longest_route(self, problem):
        for route in self.routes:
            route.set_mean_demand()
        sorted_routes = sorted(self.routes, key=lambda route: route.distance_time_consume(problem)[0], reverse=True)
        if len(sorted_routes[0].customer_list) == 3:
            return
        break_first_end = random.randint(2, len(sorted_routes[0].customer_list)-2)
        second_cus_list = [sorted_routes[0].customer_list[0]] + sorted_routes[0].customer_list[break_first_end:]
        self.routes.append(Route(second_cus_list))
        sorted_routes[0].customer_list[break_first_end:-1] = []

    def mutation(self, problem, mutation_rate, elastic_rate, squeeze_rate, shuffle_rate):
        if random.random() < mutation_rate:
            if random.random() < elastic_rate:
                self.__partial_swap()
            elif random.random() < squeeze_rate:
                self.__merge_shortest_route(problem)
            else:
                self.__split_longest_route(problem)
            for route in self.routes:
                if random.random() < shuffle_rate:
                    route.random_shuffle()

    def RSM(self, N, problem):
        sum_distance = 0
        sum_pay = 0
        for i in range(N):
            for route in self.routes:
                route.set_one_actual_demand(i)
                distance, *_ = route.distance_time_consume(problem)
                pay = route.pay_consume(problem)
                sum_distance += distance
                sum_pay += pay
        distance = sum_distance/N
        pay = sum_pay/N
        self.distance = distance
        self.pay = pay

    def get_objective(self):
        return (self.distance, self.pay, len(self.routes))  # DRV

    def cal_difference(self, other_plan):
        objective1 = np.array(self.get_objective())
        objective2 = np.array(other_plan.get_objective())
        diff_vec = objective1-objective2
        return np.linalg.norm(diff_vec)


class VectorPlan:
    # 气泡优先级编码
    def __init__(self, customers, plan=None, vector=None):
        if plan != None:
            plan.arrange()
            route_num = len(plan.routes)
            max_priority = len(customers)-1 + route_num-1
            self.vector = [0]*(len(customers)-1)
            for route in plan.routes:
                for cus in route.customer_list:
                    if cus.id != 0:
                        self.vector[cus.id-1] = max_priority
                        max_priority -= 1
                max_priority -= 1

        else:
            if vector != None:
                self.vector = vector

    def backto_plan(self, customers):
        max_priority = max(self.vector)
        routes = []
        customer_list = [customers[0]]
        while max_priority >= 0:
            try:
                cus_id = self.vector.index(max_priority)+1
                customer_list.append(customers[cus_id])
                max_priority -= 1
            except(ValueError):
                max_priority -= 1
                customer_list.append(customers[0])
                if len(customer_list) > 2:
                    routes.append(Route(customer_list))
                customer_list = [customers[0]]
        plan = Plan(routes)

        return plan
