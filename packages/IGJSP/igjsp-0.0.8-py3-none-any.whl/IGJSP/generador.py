import copy
import json
import multiprocessing
import os
import pickle
import random
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from itertools import combinations, product
from pathlib import Path
import networkx as nx
import numpy as np
from scipy.stats import expon, norm, uniform
from pprint import pprint


def f(x):
    return int(np.exp(-int(x)/100)*100)

def g(x):
    return 90*x + 10

def t(c):
    return 4.0704 * np.log(2) / np.log(1 + (c* 2.5093)**3)

class JSP:
    def __init__(self, jobs, machines, ProcessingTime=np.array([]), EnergyConsumption=np.array([]), ReleaseDateDueDate=np.array([]), Orden=np.array([])) -> None:       
        self.numJobs = jobs
        self.numMchs = machines
        self.speed = ProcessingTime.shape[-1] if ProcessingTime.size else 0
        self.ProcessingTime = ProcessingTime
        self.EnergyConsumption = EnergyConsumption
        self.Orden = Orden
        self.rddd = ReleaseDateDueDate.ndim - 1 if ReleaseDateDueDate.size else 0
        
    def fill_random_values(self, speed, rddd, distribution, seed, tpm=[]):
        np.random.seed(seed)
        self.rddd = rddd
        self.speed = speed
        if not tpm:
            if distribution == "uniform":
                tpm = np.random.uniform(10, 100, self.numMchs)
            elif distribution == "normal":
                tpm = [max(10, data) for data in np.random.normal(50, 20, self.numMchs)]
            else:
                tpm = expon(loc=10, scale=20).rvs(self.numMchs)
        
        energyPer, timePer = self._particionate_speed_space(speed)
        self._generate_standar_operation_cost(distribution)

        self.ProcessingTime = np.zeros((self.numJobs, self.numMchs, self.speed), dtype=int)
        self.EnergyConsumption = np.zeros((self.numJobs, self.numMchs, self.speed), dtype=int)
        self.Orden = np.zeros((self.numJobs, self.numMchs), dtype=int)

        if self.rddd == 0:
            release_date_tasks = np.array([0] * self.numJobs)
        
        elif self.rddd == 1:
            release_date_tasks = np.random.choice(range(0, 101, 10), self.numJobs)
            release_date_tasks = release_date_tasks - release_date_tasks.min()
            self.ReleaseDueDate = np.zeros((self.numJobs, 2), dtype=int)

        elif self.rddd == 2:
            release_date_tasks = np.random.choice(range(0, 101, 10), self.numJobs)
            release_date_tasks = release_date_tasks - release_date_tasks.min()
            self.ReleaseDueDate = np.zeros((self.numJobs, self.numMchs, 2), dtype=int)

        self._jobToMachine(release_date_tasks, timePer, distribution)
        self.generate_maxmin_objective_values()

    def _particionate_speed_space(self, speed):
        energyPer = np.linspace(0.5, 3, speed) if speed > 1 else [1]
        timePer = [t(c) for c in energyPer]
        return energyPer, timePer

    def _generate_standar_operation_cost(self, distribution):
        if distribution == "uniform":
            self.operationCost = np.random.uniform(10, 100, (self.numJobs, self.numMchs))
        elif distribution == "normal":
            self.operationCost = np.array([max(10, x) for x in np.random.normal(50, 20, (self.numJobs, self.numMchs)).reshape(-1)]).reshape(self.numJobs, self.numMchs)
        elif distribution == "exponential":
            self.operationCost = np.random.exponential(10, (self.numJobs, self.numMchs))

    def _jobToMachine(self, release_date_tasks, timePer, distribution):
        for job in range(self.numJobs):
            machines = np.random.choice(range(self.numMchs), self.numMchs, replace=False)
            self.Orden[job] = machines
            releaseDateTask = release_date_tasks[job]
            initial = releaseDateTask
            for machine in machines:
                for S, (proc, energy) in enumerate(self._genProcEnergy(job, machine, timePer)):
                    self.ProcessingTime[job, machine, S] = proc
                    self.EnergyConsumption[job, machine, S] = energy
                if self.rddd == 2:
                    self.ReleaseDueDate[job, machine, 0] = releaseDateTask
                    releaseDateTask += int(self._release_due(np.median(self.ProcessingTime[job, machine, :]), distribution))
                    self.ReleaseDueDate[job, machine, 1] = releaseDateTask
                else:
                    releaseDateTask += np.median(self.ProcessingTime[job, machine, :])
            if self.rddd == 1:
                self.ReleaseDueDate[job] = [initial, int(self._release_due(releaseDateTask, distribution))]

    def _genProcEnergy(self, job, machine, timePer):        
        ans = []  
        for tper in timePer:
            time = max(1, self.operationCost[job, machine] * tper)
            ans.append((time, max(1, f(time))))
        return ans

    def _release_due(self, duration, distribution):
        if distribution == "uniform":
            return uniform(duration, 2*duration).rvs()
        elif distribution == "normal":
            return max(duration, norm(loc=2*duration, scale=duration/2).rvs())
        else:
            return expon(loc=duration, scale=duration/2).rvs()

    def savePythonFile(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    def saveJsonFile(self, path):
        self.JSP = {
            "nbJobs": list(range(self.numJobs)),
            "nbMchs": list(range(self.numMchs)),
            "speed": self.speed,
            "timeEnergy": [],
            "minMakespan": int(self.min_makespan),
            "minEnergy": int(self.min_energy),
            "maxMinMakespan": int(self.max_min_makespan),
            "maxMinEnergy": int(self.max_min_energy)
        }
        
        for job in range(self.numJobs):
            new = {
                "jobId": job,
                "operations": {}
            }
            for machine in self.Orden[job]:
                machine = int(machine)
                new["operations"][machine] = {
                    "speed-scaling": [
                        {
                            "procTime": int(proc),
                            "energyCons": int(energy)
                        }
                        for proc, energy in zip(self.ProcessingTime[job, machine], self.EnergyConsumption[job, machine])
                    ]
                }
                if self.rddd == 2:
                    new["operations"][machine]["release-date"] = int(self.ReleaseDueDate[job][machine][0])
                    new["operations"][machine]["due-date"] = int(self.ReleaseDueDate[job][machine][1])
            if self.rddd == 1:
                new["release-date"] = int(self.ReleaseDueDate[job][0])
                new["due-date"] = int(self.ReleaseDueDate[job][1])
            if self.rddd == 2:
                new["release-date"] = int(min(self.ReleaseDueDate[job, :, 0]))
                new["due-date"] = int(max(self.ReleaseDueDate[job, :, 1]))
            self.JSP["timeEnergy"].append(new)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w+' ) as f:
            json.dump(self.JSP, f, indent=4)

    def saveDznFile(self, InputDir, OutputDir):
        indexProblema = OutputDir.split("/")[-2]
        OutputDir = "/".join(OutputDir.split("/")[:-2])
        # indexProblema = os.path.basename(os.path.normpath(OutputDir))
        with open(f"{InputDir}", 'rb') as f:
            data: JSP = pickle.load(f)
            # print(self.speed)
            # for t in [0, 1, 2]:
            t = data.rddd
            for s in range(1,self.speed+1):
                s0, sf, sp = [0,s,1]
                time = data.ProcessingTime[:, :, s0:sf:sp]
                energy = data.EnergyConsumption[:, :, s0:sf:sp]
                precedence = np.full((data.numJobs, data.numMchs), 0)

                replace_data = {
                    "machines": data.numMchs,
                    "jobs": data.numJobs,
                    "Speed": s,
                    "time": list(time.flatten()),
                    "energy": list(energy.flatten())
                }
                if t == 1:
                    replace_data["releaseDate"] = [data.ReleaseDueDate[job, 0] for job in range(data.numJobs)]
                    replace_data["dueDate"] = [data.ReleaseDueDate[job, 1] for job in range(data.numJobs)]
                elif t == 2:
                    replace_data["releaseDate"] = list(data.ReleaseDueDate[:, :, 0].flatten())
                    replace_data["dueDate"] = list(data.ReleaseDueDate[:, :, 1].flatten())

                for job in range(data.numJobs):
                    for i, prioridad in enumerate(range(data.numMchs)):
                        precedence[job, data.Orden[job, prioridad]] = i
                replace_data["precedence"] = list(precedence.flatten())

                new_object = data.change_rddd_type(t).select_speeds(list(range(s0, sf, sp)))
                with open(f"./Minizinc/Types/RD/type{t}.dzn", "r", encoding="utf-8") as file:
                    filedata = file.read()
                    for kk, v in replace_data.items():
                        filedata = filedata.replace("{" + kk + "}", str(v))

                    os.makedirs(f"{OutputDir}/", exist_ok=True)

                    with open(f"{OutputDir}/{indexProblema}-{t}-{s}.dzn", "w+", encoding="utf-8") as new:
                        new.write(filedata)
                # print(f"{OutputDir}/{indexProblema}")
                # with open(f"{OutputDir}/{indexProblema}", "wb") as new:
                #     pickle.dump(new_object, new)

    def saveTaillardStandardFile(self, path):
        os.makedirs("/".join(path.split("/")[:-1]),exist_ok=True)
        with open(path, 'w+') as f:
            # Escribir el encabezado con el número de trabajos y máquinas
            f.write(f"Number of jobs: {self.numJobs}\n")
            f.write(f"Number of machines: {self.numMchs}\n\n")
            
            # Escribir la matriz de tiempos de procesamiento
            f.write("Processing times:\n")
            for job in range(self.numJobs):
                for machine_index in range(self.numMchs):
                    machine = self.Orden[job, machine_index]
                    processing_time = self.ProcessingTime[job, machine, 0]
                    f.write(f"{processing_time} ")
                f.write("\n")
            
            f.write("\n")

            # Escribir la matriz de consumo de energía
            f.write("Energy consumption:\n")
            for job in range(self.numJobs):
                for machine_index in range(self.numMchs):
                    machine = self.Orden[job, machine_index]
                    energy_consumption = self.EnergyConsumption[job, machine, 0]
                    f.write(f"{energy_consumption} ")
                f.write("\n")
            
            f.write("\n")

            # Escribir el orden de las máquinas para cada trabajo
            f.write("Machine order:\n")
            for job in range(self.numJobs):
                for machine_index in range(self.numMchs):
                    machine = self.Orden[job, machine_index]
                    f.write(f"{machine} ")
                f.write("\n")


    def select_speeds(self, speeds):
        if self.speed == len(speeds):
            return self
        new_object = copy.deepcopy(self)
        new_object.speed = len(speeds)
        new_object.ProcessingTime = new_object.ProcessingTime[:, :, speeds]
        new_object.EnergyConsumption = new_object.EnergyConsumption[:, :, speeds]
        new_object.generate_maxmin_objective_values()
        return new_object

    def change_rddd_type(self, new_rddd):
        if new_rddd == self.rddd:
            return self
        new_object = copy.deepcopy(self)
        new_object.rddd = new_rddd 
        if new_rddd == 0:
            if self.rddd != 0:
                del new_object.ReleaseDueDate
        elif new_rddd == 1:
            if self.rddd == 2:
                new_object.ReleaseDueDate = np.zeros((self.numJobs, 2), dtype=int)
                for job in range(self.numJobs):
                    new_object.ReleaseDueDate[job] = min(self.ReleaseDueDate[job, :, 0]), max(self.ReleaseDueDate[job, :, 1])
        elif new_rddd == 2:
            pass
        new_object.generate_maxmin_objective_values()
        return new_object

    def generate_maxmin_objective_values(self):
        self.max_makespan = sum([max(self.ProcessingTime[job, machine, :]) for job in range(self.numJobs) for machine in range(self.numMchs)])
        self.min_makespan = max([sum([min(self.ProcessingTime[job, machine, :]) for machine in range(self.numMchs)]) for job in range(self.numJobs)])
        self.max_min_makespan = self.max_makespan - self.min_makespan
        self.max_energy = sum([max(self.EnergyConsumption[job, machine, :]) for job in range(self.numJobs) for machine in range(self.numMchs)])
        self.min_energy = sum([min(self.EnergyConsumption[job, machine, :]) for job in range(self.numJobs) for machine in range(self.numMchs)])
        self.max_min_energy = self.max_energy - self.min_energy
        if self.rddd == 1:
            self.max_tardiness = sum([max(0, self.max_makespan - self.ReleaseDueDate[job, 1]) for job in range(self.numJobs)])
        elif self.rddd == 2:
            self.max_tardiness = np.sum([max(0, np.int64(self.max_makespan - self.ReleaseDueDate[job, machine, 1])) for job in range(self.numJobs) for machine in range(self.numMchs)])

    def norm_makespan(self, makespan):
        return (makespan - self.min_makespan) / self.max_min_makespan
    
    def norm_energy(self, energy):
        return (energy - self.min_energy) / self.max_min_energy if self.max_min_energy > 0 else 0
    
    def norm_tardiness(self, tardiness):
        return tardiness / self.max_tardiness if self.rddd > 0 else 0
    
    def objective_function_solution(self, solution):
        makespan = 0
        energy = 0
        tardiness = 0
        
        orders_done = [0] * self.numJobs
        available_time_machines = [0] * self.numMchs
        end_time_last_operations = [0] * self.numJobs
        
        tproc = [0] * self.numJobs
        for job, speed in zip(solution[::2], solution[1::2]):
            operation = orders_done[job]
            machine = self.Orden[job, operation]            
            
            end_time_last_operation = end_time_last_operations[job]
            available_time = available_time_machines[machine]
            
            if operation == 0:
                if self.rddd == 0:
                    release_date = 0
                elif self.rddd == 1:
                    release_date = self.ReleaseDueDate[job, 0]
                elif self.rddd == 2:
                    release_date = self.ReleaseDueDate[job, machine, 0]
            else:                
                if self.rddd == 2:
                    release_date = self.ReleaseDueDate[job, machine, 0]
                else:
                    release_date = available_time

            start_time = max(end_time_last_operation, available_time, release_date)
            end_time = start_time + self.ProcessingTime[job, machine, speed]

            if self.rddd == 2:
                tardiness += min(max(0, end_time - self.ReleaseDueDate[job, machine, 1]), self.ProcessingTime[job, machine, speed])
            energy += self.EnergyConsumption[job, machine, speed]
            if self.rddd == 1:
                tproc[job] += self.ProcessingTime[job, machine, speed]
            available_time_machines[machine] = end_time
            end_time_last_operations[job] = end_time
            orders_done[job] += 1
        
        makespan = max(end_time_last_operations)

        if self.rddd == 1:
            tardiness = sum(min(max(0, end_time - self.ReleaseDueDate[job, 1]), tproc[job]) for job, end_time in enumerate(end_time_last_operations))

        return self.norm_makespan(makespan) + self.norm_energy(energy) + self.norm_tardiness(tardiness), (makespan, energy, tardiness)

    def evalua_añadir_operacion(self, candidate, speed, makespan, energy, tardiness, orders_done, available_time_machines, end_time_last_operations, tproc, actualizacion):
        operation = orders_done[candidate]
        machine = self.Orden[candidate, operation]            
        
        end_time_last_operation = end_time_last_operations[candidate]
        available_time = available_time_machines[machine]
        
        if operation == 0:
            if self.rddd == 0:
                release_date = 0
            elif self.rddd == 1:
                release_date = self.ReleaseDueDate[candidate, 0]
            elif self.rddd == 2:
                release_date = self.ReleaseDueDate[candidate, machine, 0]
        else:                
            if self.rddd == 2:
                release_date = self.ReleaseDueDate[candidate, machine, 0]
            else:
                release_date = available_time

        start_time = max(end_time_last_operation, available_time, release_date)
        end_time = start_time + self.ProcessingTime[candidate, machine, speed]

        if self.rddd == 2:
            tardiness += min(max(0, end_time - self.ReleaseDueDate[candidate, machine, 1]), self.ProcessingTime[candidate, machine, speed])
        energy += self.EnergyConsumption[candidate, machine, speed]

        if actualizacion:
            available_time_machines[machine] = end_time
            end_time_last_operations[candidate] = end_time
            orders_done[candidate] += 1
            tproc[candidate] += self.ProcessingTime[candidate, machine, speed]

        makespan = makespan if end_time < makespan else end_time
        
        if self.rddd == 1:
            tardiness = sum(min(max(0, end_time - self.ReleaseDueDate[job, 1]), tproc[job]) for job, end_time in enumerate(end_time_last_operations))

        return self.norm_makespan(makespan) + self.norm_energy(energy) + self.norm_tardiness(tardiness), makespan, energy, tardiness

    def generate_schedule_image(self, schedule):
        pass
    
    def vectorization(self):
        vectorization = {}
        # Caracteristicas básicas
        vectorization["jobs"]           = self.numJobs
        vectorization["machines"]       = self.numMchs
        vectorization["rddd"]           = self.rddd
        vectorization["speed"]          = self.speed
        vectorization["max_makespan"]    = self.max_makespan
        vectorization["min_makespan"]    = self.min_makespan
        vectorization["max_sum_energy"]   = self.max_energy
        vectorization["min_sum_energy"]   = self.min_energy
        vectorization["max_tardiness"]   = self.max_tardiness
        vectorization["min_window"]     = 0
        vectorization["max_window"]     = 0
        vectorization["mean_window"]    = 0
        vectorization["overlap"]        = 0

        # Caracteristicas complejas
        if self.rddd == 0:
            vectorization["min_window"]  = -1
            vectorization["max_window"]  = -1
            vectorization["mean_window"]  = -1
            vectorization["overlap"] = -1
        else:
            if self.rddd == 1:
                # Ventana de cada trabajo
                for job in range(self.numJobs):
                    tproc_min  = np.sum(np.min(self.ProcessingTime[job,machine,:]) for machine in range(self.numMchs))
                    tproc_max  = np.sum(np.max(self.ProcessingTime[job,machine,:]) for machine in range(self.numMchs))                    
                    tproc_mean = np.sum(np.mean(self.ProcessingTime[job,machine,:]) for machine in range(self.numMchs)) 
                    window     = self.ReleaseDueDate[job,1] - self.ReleaseDueDate[job,0]
                    vectorization["min_window"]  += window / tproc_max 
                    vectorization["max_window"]  += window / tproc_min 
                    vectorization["mean_window"] += window / tproc_mean 
                vectorization["min_window"]  = vectorization["min_window"]  / self.numJobs
                vectorization["max_window"]  = vectorization["max_window"]  / self.numJobs
                vectorization["mean_window"] = vectorization["mean_window"] / self.numJobs
                # Overlap entre trabajos
                for job in range(self.numJobs):
                    for job2 in range(job + 1, self.numJobs):
                        diff = min(self.ReleaseDueDate[job,1],self.ReleaseDueDate[job2,1])-max(self.ReleaseDueDate[job,0], self.ReleaseDueDate[job2,0])
                        if diff > 0:
                            vectorization["overlap"] += diff / (self.ReleaseDueDate[job,1] - self.ReleaseDueDate[job,0])
                            vectorization["overlap"] += diff / (self.ReleaseDueDate[job2,1] - self.ReleaseDueDate[job2,0])
                vectorization["overlap"] = vectorization["overlap"] / (self.numJobs * (self.numJobs - 1))
            else:
                # Ventana de cada operacion
                for job in range(self.numJobs):
                    for machine in range(self.numMchs):
                        tproc_min  = np.min(self.ProcessingTime[job,machine,:])
                        tproc_max  = np.max(self.ProcessingTime[job,machine,:])                   
                        tproc_mean = np.mean(self.ProcessingTime[job,machine,:])
                        window     = self.ReleaseDueDate[job,machine,1] - self.ReleaseDueDate[job,machine,0]
                        vectorization["min_window"]  += window / tproc_max 
                        vectorization["max_window"]  += window / tproc_min 
                        vectorization["mean_window"] += window / tproc_mean 
                vectorization["min_window"]  = vectorization["min_window"]  / (self.numJobs * self.numMchs)
                vectorization["max_window"]  = vectorization["max_window"]  / (self.numJobs * self.numMchs)
                vectorization["mean_window"] = vectorization["mean_window"] / (self.numJobs * self.numMchs)
                # Overlap entre operaciones
                for job1 in range(self.numJobs):
                    for machine1 in range(self.numMchs):
                        for job2 in range(job1 + 1, self.numJobs):
                            diff = min(self.ReleaseDueDate[job1,machine1,1],self.ReleaseDueDate[job2,machine1,1])-max(self.ReleaseDueDate[job1,machine1,0],  self.ReleaseDueDate[job2,machine1,0])
                            if diff > 0:
                                vectorization["overlap"] += diff / (self.ReleaseDueDate[job1,machine1,1] - self.ReleaseDueDate[job1,machine1,0])
                                vectorization["overlap"] += diff / (self.ReleaseDueDate[job2,machine1,1] -  self.ReleaseDueDate[job2,machine1,0])
                vectorization["overlap"] = vectorization["overlap"] / (self.numJobs * (self.numJobs - 1) * self.numMchs)   
        # Estadísticos de los datos
        vectorization["max_processing_time_value"]     = np.max(self.ProcessingTime)
        vectorization["min_processing_time_value"]     = np.min(self.ProcessingTime)
        vectorization["mean_processing_time_value"]    = np.mean(self.ProcessingTime)

        vectorization["max_energy_value"]     = np.max(self.ProcessingTime)
        vectorization["min_energy_value"]     = np.min(self.ProcessingTime)
        vectorization["mean_energy_value"]    = np.mean(self.ProcessingTime)

        return vectorization
    
    def disjuntive_graph(self):
        vertex = list(range(self.numJobs * self.numMchs + 2))
        A = {v: [] for v in vertex}
        E = {v: [] for v in vertex}

        index = np.arange(1, self.Orden.size).reshape(self.numJobs, self.numMchs)

        for v in index[:, 0]:
            A[0].append(v)
        
        for v in index[:, -1]:
            A[v].append(self.numJobs * self.numMchs + 1)

        for job in range(self.numJobs):
            for machine in range(1, self.numMchs):
                A[index[job, machine - 1]].append(index[job, machine])
        aux = {m: [] for m in range(self.numMchs)}
        
        for job in range(self.numJobs):
            for machine in range(self.numMchs):
                aux[self.Orden[job, machine]].append(index[job, machine])
        
        for machine, vertex in aux.items():            
            for v, w in combinations(vertex, 2):
                A[v].append(w)
                A[w].append(v)
        return index, A, E
    
    def disjuntive_graph_solution(self, solution):
        graph = nx.Graph()
        graph.add_nodes_from([(0, {"valor": 0}), (self.numJobs * self.numMchs + 1, {"valor": 0})])
        
        orders_done = [0] * self.numJobs
        available_time_machines = [0] * self.numMchs
        end_time_last_operations = [0] * self.numJobs

        for job, speed in zip(solution[::2], solution[1::2]):

            operation = orders_done[job]
            machine = self.Orden[job, operation]
            valor = self.EnergyConsumption[job, machine, speed]   

            graph.add_node((job * self.numMchs + operation, {"valor": valor}))   
            if operation == 0:
                graph.add_edge((0, job * self.numMchs + operation))
            if operation == self.numMchs - 1:
                graph.add_edge((0, self.numJobs * self.numMchs + 1))            
            if operation > 0 and operation < self.numMchs - 1:
                graph.add_edge((job * self.numMchs + operation - 1, job * self.numMchs + operation))

# if __name__ == "__main__":
#     jsp = JSP(jobs=5, machines=5)
#     jsp.fill_random_values(speed=3, rddd=2, distribution="uniform", seed=1234)
#     jsp.saveTaillardStandardFile("./output_taillard.txt")

class Generator:
    def __init__( self,json = False, dzn = False, taillard = False, savepath="./"):
        self.json = json
        self.dzn = dzn
        self.taillard = taillard
        self.savepath = savepath
        
    def generate_new_instance(self, jobs = 10, machines = 4,speed = 1, ReleaseDateDueDate = 0, distribution = "uniform" , seed = 0, tpm=[]):
        jsp = JSP(jobs=jobs, machines=machines)
        jsp.fill_random_values(speed = speed, rddd = ReleaseDateDueDate, distribution = distribution, seed = seed,tpm = tpm)
        if not (self.json or self.dzn or self.taillard): return jsp
        
        j = str(jobs)
        m = str(machines)
        jm_path = str(j)+"_"+str(m)+"/"
        
        i = seed

        if self.json:
            jsp.saveJsonFile(f"{self.savepath}/JSON/"+jm_path.split("/")[0]+f"_{j}x{m}_{i}.json")
        if self.dzn:
            pkl_path = f"{self.savepath}/"+jm_path.split("/")[0]+f"_{j}x{m}_{i}.pkl"
            jsp.savePythonFile(pkl_path)
            jsp.saveDznFile(pkl_path,f"{self.savepath}/DZN/"+jm_path)#f"{j}x{m}_{i}")
            os.remove(pkl_path)
        if self.taillard:
            jsp.saveTaillardStandardFile(f"{self.savepath}/TAILLARD/"+jm_path.split("/")[0]+f"_{j}x{m}_{i}.txt")
        return jsp