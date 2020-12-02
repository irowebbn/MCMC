import itertools
import random
import copy
import time
import matplotlib.pyplot as plt

dependency_map = {
    "fc" : ["fever", "cough"], 
    "~fc" : ["fever", "cough"], 
    "fn" : ["fever", "nausea"],
    "~fn" : ["fever", "nausea"],
    "cn" : ["cough", "nausea"],
    "~cn" : ["cough", "nausea"],
    "fever" : ["c19"],
    "~fever" : ["c19"],
    "cough" : ["c19"],
    "~cough" : ["c19"],
    "nausea": ["c19"],
    "~nausea" : ["c19"],
    "c19" : [],
    "~c19" : []}
base_map = {"c19" : 0.01}
cond_map = {
    ("fever", "c19") : 0.78, 
    ("fever", "~c19"): 0.1, 
    ("cough", "c19"): 0.98,
    ("cough", "~c19"): 0.1,
    ("nausea", "c19"): 0.59,
    ("nausea", "~c19"): 0.2,
    ("fc", ("fever", "cough")): 0.8,
    ("fc", ("cough", "fever")): 0.8,
    ("fc", ("fever", "~cough")): 0.95,
    ("fc", ("~cough", "fever")): 0.95,
    ("fc", ("~fever", "cough")): 0.3,
    ("fc", ("cough", "~fever")): 0.3,
    ("fc", ("~fever", "~cough")): 0.2,
    ("fc", ("~cough", "~fever")): 0.2,
    ("fn", ("fever", "nausea")): 0.85,
    ("fn", ("nausea", "fever")): 0.85,
    ("fn", ("fever", "~nausea")): 0.63,
    ("fn", ("~nausea", "fever")): 0.63,
    ("fn", ("~fever", "nausea")): 0.58,
    ("fn", ("nausea", "~fever")): 0.58,
    ("fn", ("~fever", "~nausea")): 0.08,
    ("fn", ("~nausea", "~fever")): 0.08,
    ("cn", ("cough", "nausea")): 0.76,
    ("cn", ("nausea", "cough")): 0.76,
    ("cn", ("cough", "~nausea")): 0.42,
    ("cn", ("~nausea", "cough")): 0.42,
    ("cn", ("~cough", "nausea")): 0.29,
    ("cn", ("nausea", "~cough")): 0.29,
    ("cn", ("~cough", "~nausea")): 0.05,
    ("cn", ("~nausea", "~cough")): 0.05,
    }
c19 = ["c19", "~c19"]
fever = ["fever", "~fever"]
nausea = ["nausea", "~nausea"]
cough = ["cough", "~cough"]
fn = ["fn", "~fn"]
fc = ["fc", "~fc"]
cn = ["cn", "~cn"]

variables = [c19, fever, nausea, cough, fn, fc, cn]
DEBUG = 0

def debug_print(str):
    if DEBUG:
        print(str)

def is_dependent_on(a, b):
     notb = get_negative(b)
     if b in dependency_map[a] or notb in dependency_map[a]:
         return True
     else:
         return False

def get_negative(var):
    if var[0] == "~":
        return var[1:]
    else:
        return "~" + var

def included_variables(x):
    included_variables = []
    for var_inst in x:
        val = False
        for var in variables:
            if var_inst in var:
                val = True
                included_variables.append(var)
                break
    return included_variables
        
def prob(x):
    debug_print("Finding P( " +  str(x) + " )")
    if type(x) == tuple:
        vars_used = included_variables(x)
        if len(vars_used) == 7:
            # Chain 'em
            if "c19" in x:
                c19_val ='c19'
            else:
                c19_val = '~c19'
            if "fever" in x:
                f_val = 'fever'
            else:
                f_val = '~fever'
            if "nausea" in x:
                n_val = 'nausea'
            else:
                n_val = '~nausea'
            if "cough" in x:
                c_val = 'cough'
            else:
                c_val = '~cough'
            if "fc" in x:
                fc_val = 'fc'
            else:
                fc_val = '~fc'
            if "fn" in x:
                fn_val = 'fn'
            else:
                fn_val = '~fn'
            if "cn" in x:
                cn_val = 'cn'
            else:
                cn_val = '~cn'
            return prob(c19_val)*cond_prob(f_val, c19_val)*cond_prob(c_val, c19_val)*cond_prob(n_val, c19_val)*cond_prob(fc_val, (f_val, c_val))*cond_prob(fn_val, (f_val, n_val))*cond_prob(cn_val, (c_val, n_val))
        else:
            missing_vars = []
            for var in variables:
                if var not in included_variables(x):
                    missing_vars.append(var)
            missing_combos = list(itertools.product(*missing_vars))
            sum = 0
            for combo in missing_combos:
                add = prob(x+combo)
                debug_print(add)
                sum = sum + add
                #sum = sum + prob(x+combo)
            debug_print(sum)
            return sum
    notx = get_negative(x)
    if x in base_map:
        debug_print(base_map[x])
        return base_map[x]
    elif notx in base_map:
        base_map[x] = 1 - base_map[notx]
        debug_print(base_map[x])
        return base_map[x]
    else:
        for key in cond_map:
            a, b = key
            if type(b) == tuple:
                b1, b2 = b
                notb1 = get_negative(b1)
                notb2 = get_negative(b2)
                tt = cond_prob(a, (b1, b2)) 
                tf = cond_prob(a, (b1, notb2))  
                ft = cond_prob(a, (notb1, b2)) 
                ff = cond_prob(a, (notb1, notb2)) 
                if a == x:
                    base_map[x] = tt*prob(b1)*prob(b2) + tf*prob(b1)*prob(notb2) + ft*prob(notb1)*prob(b2) + ff*prob(notb1)*prob(notb2)
                    return base_map[x]
                elif a == notx:
                    base_map[notx] = (1-tt)*prob(b1)*prob(b2) + (1-tf)*prob(b1)*prob(notb2) + (1-ft)*prob(notb1)*prob(b2) + (1-ff)*prob(notb1)*prob(notb2)
                    return 1 - base_map[notx]
            else:
                notb = get_negative(b)
                if a == x:
                    base_map[x] = cond_prob(a, b) * prob(b) + cond_prob(a, notb) * prob(notb)
                    return base_map[x]
                elif a == notx:
                    base_map[notx] = cond_prob(a, b) * prob(b) + cond_prob(a, notb) * prob(notb) 
                    return 1 - base_map[notx]

def cond_prob(a, b):
    debug_print("Finding P( "+str(a)+" | "+str(b)+" )")
    if (a, b) in cond_map:
        debug_print(cond_map[(a, b)])
        return cond_map[(a, b)]
    if type(a) == tuple:
        ans = 1
        for entry in a:
            notb = get_negative(b)
            if is_dependent_on(entry, b):
                ans = ans * cond_prob(entry,b)
            elif is_dependent_on(b, entry):
                ans = ans * cond_prob(b, entry) * prob(entry)
            elif entry == notb:
                ans = 0
        cond_map[(a, b)] = ans
        return cond_map[(a, b)]
    nota = get_negative(a)
    if (nota, b) in cond_map:
        return 1 - cond_map[(nota, b)]
    if type(b) == tuple:
        cond_map[(a, b)] = prob((a,)+b)/prob(b)
        return cond_map[(a,b)]
    if type(b) != tuple and is_dependent_on(a,b) and len(dependency_map[a]) == 2:
        dep1, dep2 = dependency_map[a]
        tt = cond_prob(a, (dep1, dep2)) * prob(dep1) * prob(dep2)
        if dep1 == b:
            notdep2 = get_negative(dep2)
            tf = cond_prob(a, (dep1, notdep2)) * prob(dep1) * prob(notdep2)
        else:
            notdep1 = get_negative(dep1)
            tf = cond_prob(a, (notdep1, dep2)) * prob(notdep1) * prob(dep2)
        cond_map[(a, b)] = tt + tf
        return cond_map[(a, b)]
    else:
        # Apply Bayes:
        if type(b) != tuple:
            cond_map[(a,b)] = cond_prob(b, a)*prob(a)/ prob(b)
        else:
            cond_map[(a,b)] = (cond_prob(b, a) * prob(a))/(cond_prob(b,a)*prob(a)+cond_prob(b, nota)*prob(nota)) 
        return cond_map[(a,b)]

nausea_res = ["nausea"]
fn_res = ["fn"]
available_vars = [c19, fever, nausea_res, cough, fn_res, fc, cn]
start_time = time.time()
# Generate Conditional Probability Tables for each variable
for n in range(len(variables)) :
    if n >= 0:
        desired = variables.pop(n)
        blanket_vars = []
        for var in available_vars:
            if is_dependent_on(desired[0], var[0]) or is_dependent_on(var[0], desired[0]) :
                blanket_vars.append(var)
            if is_dependent_on(var[0], desired[0]):
                for neighbor_var in dependency_map[var[0]]: 
                    if neighbor_var != desired[0]:
                        for var_state in available_vars:
                            if var_state[0] == neighbor_var:
                                blanket_vars.append(var_state)
        all_combos = tuple(itertools.product(*blanket_vars)) 

        print("Conditional probability table for", desired[0])
        variables.insert(n,desired)
        for combo in all_combos:
            prob_str = "P( "+desired[0]+" | " + str(combo) + ") ="
            result = cond_prob(desired[0],combo)
            print(prob_str,str(result))
        
print("P(C19 | N, FN) =",cond_prob("c19", ("nausea", "fn")))
records = []
for run_num in range(5):
    debug_print("Run " + str(run_num) + " : ")
    start = [random.choice(i) for i in available_vars]
    samples = [start]
    parent = start
    num_c19 = 0
    while len(samples) < 10000:
        child = copy.deepcopy(parent)
        for i, variable in enumerate(available_vars):
            if(variable == nausea_res or variable == fn_res):
                continue
            removed = child.pop(i)
            rf = random.random()
            if rf < cond_prob(variables[i][0],(child[0], child[1], child[2], child[3], child[4], child[5])):
                child.insert(i, removed)
                child[i] = variables[i][0]
            else:
                child.insert(i, removed)
                child[i] = variables[i][1]
        if child[0] == "c19":
            num_c19 = num_c19 + 1
        samples.append(child)
        parent = child
        if (len(samples) % 1000) == 0:
            debug_print(num_c19/len(samples))
            records.append((len(samples), num_c19/len(samples)))
print("Calculating CPTs and Gibbs sampling took: ", time.time() - start_time, "seconds")
plot_list = zip(*records)
plt.scatter(*plot_list, alpha=0.5, linewidths=0)
plt.xlabel("Number of iterations")
plt.ylabel("P(C19 | N, FN)")

plt.show()
