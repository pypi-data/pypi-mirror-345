from PyMELib.labels2 import *
from PyMELib.TreeDecompositions import RootedDisjointBranchNiceTreeDecomposition
from frozendict import frozendict

MAX_CHR = 1114111


def IsExtendable(td: RootedDisjointBranchNiceTreeDecomposition, theta, i):
    """
    This function uses the pre-processing phase of the TD to check if the labeling is extendable.
    :param td: A rooted disjoint branch nice tree decomposition.
    :param theta: A labeling or False.
    :param i: The index of the vertex in the graph (in Q).
    :return: True if the labeling is extendable, False otherwise.
    """
    if not theta:
        return False
    first_bag = td.first_appear[td.Q[i]]
    bag = td.nodes[first_bag]["bag"]
    frozen_theta = frozendict({key: theta[key] for key in bag})
    if frozen_theta in td.nodes[first_bag]["factor"].get_all_keys():
        return td.nodes[first_bag]["factor"].get_value(frozen_theta) == 1
    else:
        return False

def EnumMDS(td: RootedDisjointBranchNiceTreeDecomposition, theta: Dict[str, int] = dict(), i=0, debug_flag=False, options_for_labels=False):
    """
    This algorithm means to enumerate all the minimal dominating sets of the graph.
    :param td: A rooted disjoint branch nice tree decomposition.
    :param theta: An extendable labeling.
    :param i: The index of the vertex in the graph (in Q).
    :param debug_flag: A flag to print debug information.
    :param options_for_labels: A flag to use if the user added additional constraints to the labels of the vertices.
    :return:
    """
    if i == len(td.all_vertices):
        yield frozenset({td.original_graph.nodes[ord(x[0])]["original_name"] for x in V_label("S", theta)})
        return
    V_label_S, V_label_W = V_label_S_W(theta)
    if options_for_labels:
        options_for_label = td.original_graph.nodes[ord(td.Q[i][0])]["options"]
    else:
        options_for_label = F
    for c in options_for_label:
        if debug_flag:
            print("Current theta: " + str(theta))
            print("Current vertex: " + str(td.Q[i]))
            print("Current node: " + str(td.nodes[td.first_appear[td.Q[i]]]["bag"]))
            print("Current br: " + str(td.nodes[td.first_appear[td.Q[i]]]["br"]))
            print("Optional label: " + reverse_trans_dict[c])
        counter = 0
        for v in td.nodes[td.first_appear[td.Q[i]]]["bag"]:
            if v[0] == td.Q[i][0]:
                counter += 1
        if counter == 1:
            new_theta = IncrementLabeling(td, theta, i, c, V_label_S, V_label_W)
        elif counter == 2:
            new_theta = IncrementLabeling2(td, theta, i, c)
        elif counter == 3:
            original_copy = td.Q[i][0] + td.nodes[td.first_appear[td.Q[i]]]["br"]
            original_c = theta[original_copy]
            first_copy = td.Q[i][0] + td.nodes[td.first_appear[td.Q[i]]]["br"] + "0"
            first_c = theta[first_copy]
            if in_rho(original_c):
                if in_rho(c) and in_rho(first_c) and original_c - R0 == c - R0 + first_c - R0:
                    if first_c == R1 and c == R1:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif first_c == R0 and c == R0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif first_c == R0 and c == R1:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    else:
                        if debug_flag:
                            print("Not Valid Labeling")
                            print("-" * 20)
                        continue
                elif original_c == R1 and first_c == R1 and c == W0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == R2 and first_c == W0 and c == R2:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == R2 and first_c == R2 and c == W0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                else:
                    if debug_flag:
                        print("Not Valid Labeling")
                        print("-" * 20)
                    continue
            elif in_sigma(original_c) and in_sigma(first_c) and in_sigma(c):
                if original_c == SI and first_c == SI and c == SI:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == S0 and first_c == S0 and c == S0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == S1 and first_c == S1 and c == S0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == S1 and first_c ==S0 and c == S1:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == S1 and first_c == S1 and c == S1:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                else:
                    if debug_flag:
                        print("Not Valid Labeling")
                        print("-" * 20)
                    continue
            elif in_omega(original_c) and in_omega(first_c) and in_omega(c):
                if original_c == W0 and first_c == W0 and c == W0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == W1 and first_c == W0 and c == W1:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == W1 and first_c == W1 and c == W0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                else:
                    if debug_flag:
                        print("Not Valid Labeling")
                        print("-" * 20)
                    continue
            else:
                if debug_flag:
                    print("Not Valid Labeling")
                    print("-" * 20)
                continue
        else:
            print("Error - First Appear isn't good")
            return -1
        if debug_flag:
            print("IncrementLabeling: " + str(new_theta))
            print("-" * 20)
        if new_theta is None or not new_theta:
            continue
        for option in new_theta:
            if debug_flag:
                print("Option: " + str(option))
                print("IsExtendable: " + str(IsExtendable(td, option, i)))
                print("-" * 20)
            if IsExtendable(td, option, i):
                yield from EnumMDS(td, option, i + 1, debug_flag=debug_flag, options_for_labels=options_for_labels)


def EnumMDS_iterative(td: RootedDisjointBranchNiceTreeDecomposition, debug_flag=False, options_for_labels=False):
    """
    This is a for loop version of EnumMDS, using a stack.
    """
    stack = [(dict(), 0)]

    while stack:

        theta, i = stack.pop()

        if i == len(td.all_vertices):
            yield frozenset({td.original_graph.nodes[ord(x[0])]["original_name"] for x in V_label("S", theta)})
            continue

        V_label_S, V_label_W = V_label_S_W(theta)

        if options_for_labels:
            options_for_label = td.original_graph.nodes[ord(td.Q[i][0])]["options"]
        else:
            options_for_label = F

        for c in options_for_label:
            if debug_flag:
                print("Current theta: " + str(theta))
                print("Current vertex: " + str(td.Q[i]))
                print("Current node: " + str(td.nodes[td.first_appear[td.Q[i]]]["bag"]))
                print("Current br: " + str(td.nodes[td.first_appear[td.Q[i]]]["br"]))
                print("Optional label: " + reverse_trans_dict[c])
            counter = 0
            for v in td.nodes[td.first_appear[td.Q[i]]]["bag"]:
                if v[0] == td.Q[i][0]:
                    counter += 1
            if counter == 1:
                new_theta = IncrementLabeling(td, theta, i, c, V_label_S, V_label_W)
            elif counter == 2:
                new_theta = IncrementLabeling2(td, theta, i, c)
            elif counter == 3:
                if td.is_semi_nice:
                    original_copy = None
                    begins_with = td.Q[i][0]
                    for node in td.nodes[td.first_appear[td.Q[i]]]["bag"]:
                        if node.startswith(begins_with) and (not original_copy or len(node) < len(original_copy)):
                            original_copy = node
                else:
                    original_copy = td.Q[i][0] + td.nodes[td.first_appear[td.Q[i]]]["br"]
                original_c = theta[original_copy]
                first_copy = td.Q[i][0] + td.nodes[td.first_appear[td.Q[i]]]["br"] + "0"
                first_c = theta[first_copy]
                if in_rho(original_c):
                    if in_rho(c) and in_rho(first_c) and original_c - R0 == c - R0 + first_c - R0:
                        if first_c == R1 and c == R1:
                            new_theta = IncrementLabeling2(td, theta, i, c)
                        elif first_c == R0 and c == R0:
                            new_theta = IncrementLabeling2(td, theta, i, c)
                        elif first_c == R0 and c == R1:
                            new_theta = IncrementLabeling2(td, theta, i, c)
                        else:
                            if debug_flag:
                                print("Not Valid Labeling")
                                print("-" * 20)
                            continue
                    elif original_c == R1 and first_c == R1 and c == W0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == R2 and first_c == W0 and c == R2:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == R2 and first_c == R2 and c == W0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    else:
                        if debug_flag:
                            print("Not Valid Labeling")
                            print("-" * 20)
                        continue
                elif in_sigma(original_c) and in_sigma(first_c) and in_sigma(c):
                    if original_c == SI and first_c == SI and c == SI:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == S0 and first_c == S0 and c == S0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == S1 and first_c == S1 and c == S0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == S1 and first_c == S0 and c == S1:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == S1 and first_c == S1 and c == S1:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    else:
                        if debug_flag:
                            print("Not Valid Labeling")
                            print("-" * 20)
                        continue
                elif in_omega(original_c) and in_omega(first_c) and in_omega(c):
                    if original_c == W0 and first_c == W0 and c == W0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == W1 and first_c == W0 and c == W1:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == W1 and first_c == W1 and c == W0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    else:
                        if debug_flag:
                            print("Not Valid Labeling")
                            print("-" * 20)
                        continue
                else:
                    if debug_flag:
                        print("Not Valid Labeling")
                        print("-" * 20)
                    continue
            else:
                print("Error - First Appear isn't good")
                return -1
            if debug_flag:
                print("IncrementLabeling: " + str(new_theta))
                print("-" * 20)
            if new_theta is None or not new_theta:
                continue
            for option in new_theta:
                if debug_flag:
                    print("Option: " + str(option))
                    print("IsExtendable: " + str(IsExtendable(td, option, i)))
                    print("-" * 20)
                if IsExtendable(td, option, i):
                    stack.append((option, i + 1))


def EnumMHS(td: RootedDisjointBranchNiceTreeDecomposition, theta: Dict[str, int] = dict(), i=0, debug_flag=False):
    """
    This algorithm means to enumerate all the minimal hitting sets of a hypergraph (gets it reduction).
    :param td: A rooted disjoint branch nice tree decomposition.
    :param theta: An extendable labeling.
    :param i: The index of the vertex in the graph (in Q).
    :param debug_flag: A flag to print debug information.
    :return:
    """
    if i == len(td.all_vertices):
        yield frozenset({td.original_graph.nodes[ord(x[0])]["original_name"] for x in V_label("S", theta) if ord(x[0]) != MAX_CHR})
        return
    options_for_label = td.original_graph.nodes[ord(td.Q[i][0])]["options"]
    V_label_S, V_label_W = V_label_S_W(theta)
    for c in options_for_label:
        if debug_flag:
            print("Current theta: " + str(theta))
            print("Current vertex: " + str(td.Q[i]))
            print("Current node: " + str(td.nodes[td.first_appear[td.Q[i]]]["bag"]))
            print("Current br: " + str(td.nodes[td.first_appear[td.Q[i]]]["br"]))
            print("Optional label: " + reverse_trans_dict[c])
        counter = 0
        for v in td.nodes[td.first_appear[td.Q[i]]]["bag"]:
            if v[0] == td.Q[i][0]:
                counter += 1
        if counter == 1:
            new_theta = IncrementLabeling(td, theta, i, c, V_label_S, V_label_W)
        elif counter == 2:
            new_theta = IncrementLabeling2(td, theta, i, c)
        elif counter == 3:
            original_copy = td.Q[i][0] + td.nodes[td.first_appear[td.Q[i]]]["br"]
            original_c = theta[original_copy]
            first_copy = td.Q[i][0] + td.nodes[td.first_appear[td.Q[i]]]["br"] + "0"
            first_c = theta[first_copy]
            if in_rho(original_c):
                if in_rho(c) and in_rho(first_c) and original_c - R0 == c - R0 + first_c - R0:
                    if first_c == R1 and c == R1:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif first_c == R0 and c == R0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif first_c == R0 and c == R1:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    else:
                        if debug_flag:
                            print("Not Valid Labeling")
                            print("-" * 20)
                        continue
                elif original_c == R1 and first_c == R1 and c == W0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == R2 and first_c == W0 and c == R2:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == R2 and first_c == R2 and c == W0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                else:
                    if debug_flag:
                        print("Not Valid Labeling")
                        print("-" * 20)
                    continue
            elif in_sigma(original_c) and in_sigma(first_c) and in_sigma(c):
                if original_c == SI and first_c == SI and c == SI:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == S0 and first_c == S0 and c == S0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == S1 and first_c == S1 and c == S0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == S1 and first_c == S0 and c == S1:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == S1 and first_c == S1 and c == S1:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                else:
                    if debug_flag:
                        print("Not Valid Labeling")
                        print("-" * 20)
                    continue
            elif in_omega(original_c) and in_omega(first_c) and in_omega(c):
                if original_c == W0 and first_c == W0 and c == W0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == W1 and first_c == W0 and c == W1:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                elif original_c == W1 and first_c == W1 and c == W0:
                    new_theta = IncrementLabeling2(td, theta, i, c)
                else:
                    if debug_flag:
                        print("Not Valid Labeling")
                        print("-" * 20)
                    continue
            else:
                if debug_flag:
                    print("Not Valid Labeling")
                    print("-" * 20)
                continue
        else:
            print("Error - First Appear isn't good")
            return -1
        if debug_flag:
            print("IncrementLabeling: " + str(new_theta))
            print("-" * 20)
        if new_theta is None or not new_theta:
            continue
        for option in new_theta:
            if debug_flag:
                print("Option: " + str(option))
                print("IsExtendable: " + str(IsExtendable(td, option, i)))
                print("-" * 20)
            if IsExtendable(td, option, i):
                yield from EnumMHS(td, option, i + 1, debug_flag=debug_flag)


def EnumMHS_iterative(td: RootedDisjointBranchNiceTreeDecomposition, bound_cardinality=False, debug_flag=False):
    """
    This is a for loop version of EnumMHS, using a stack.
    """
    stack = [(dict(), 0)]

    while stack:

        theta, i = stack.pop()

        if i == len(td.all_vertices):
            yield frozenset({td.original_graph.nodes[ord(x[0])]["original_name"] for x in V_label("S", theta) if ord(x[0]) != MAX_CHR})
            continue

        options_for_label = td.original_graph.nodes[ord(td.Q[i][0])]["options"]
        V_label_S, V_label_W = V_label_S_W(theta)
        if bound_cardinality:
            if len({xx[0] for xx in V_label_S}) > bound_cardinality + 1:
                continue
        for c in options_for_label:
            if debug_flag:
                print("Current theta: " + str(theta))
                print("Current vertex: " + str(td.Q[i]))
                print("Current node: " + str(td.nodes[td.first_appear[td.Q[i]]]["bag"]))
                print("Current br: " + str(td.nodes[td.first_appear[td.Q[i]]]["br"]))
                print("Optional label: " + reverse_trans_dict[c])
            counter = 0
            for v in td.nodes[td.first_appear[td.Q[i]]]["bag"]:
                if v[0] == td.Q[i][0]:
                    counter += 1
            if counter == 1:
                new_theta = IncrementLabeling(td, theta, i, c, V_label_S, V_label_W)
            elif counter == 2:
                new_theta = IncrementLabeling2(td, theta, i, c)
            elif counter == 3:
                if td.is_semi_nice:
                    original_copy = None
                    begins_with = td.Q[i][0]
                    for node in td.nodes[td.first_appear[td.Q[i]]]["bag"]:
                        if node.startswith(begins_with) and (not original_copy or len(node) < len(original_copy)):
                            original_copy = node
                else:
                    original_copy = td.Q[i][0] + td.nodes[td.first_appear[td.Q[i]]]["br"]
                original_c = theta[original_copy]
                first_copy = td.Q[i][0] + td.nodes[td.first_appear[td.Q[i]]]["br"] + "0"
                first_c = theta[first_copy]
                if in_rho(original_c):
                    if in_rho(c) and in_rho(first_c) and original_c - R0 == c - R0 + first_c - R0:
                        if first_c == R1 and c == R1:
                            new_theta = IncrementLabeling2(td, theta, i, c)
                        elif first_c == R0 and c == R0:
                            new_theta = IncrementLabeling2(td, theta, i, c)
                        elif first_c == R0 and c == R1:
                            new_theta = IncrementLabeling2(td, theta, i, c)
                        else:
                            if debug_flag:
                                print("Not Valid Labeling")
                                print("-" * 20)
                            continue
                    elif original_c == R1 and first_c == R1 and c == W0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == R2 and first_c == W0 and c == R2:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == R2 and first_c == R2 and c == W0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    else:
                        if debug_flag:
                            print("Not Valid Labeling")
                            print("-" * 20)
                        continue
                elif in_sigma(original_c) and in_sigma(first_c) and in_sigma(c):
                    if original_c == SI and first_c == SI and c == SI:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == S0 and first_c == S0 and c == S0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == S1 and first_c == S1 and c == S0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == S1 and first_c == S0 and c == S1:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == S1 and first_c == S1 and c == S1:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    else:
                        if debug_flag:
                            print("Not Valid Labeling")
                            print("-" * 20)
                        continue
                elif in_omega(original_c) and in_omega(first_c) and in_omega(c):
                    if original_c == W0 and first_c == W0 and c == W0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == W1 and first_c == W0 and c == W1:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    elif original_c == W1 and first_c == W1 and c == W0:
                        new_theta = IncrementLabeling2(td, theta, i, c)
                    else:
                        if debug_flag:
                            print("Not Valid Labeling")
                            print("-" * 20)
                        continue
                else:
                    if debug_flag:
                        print("Not Valid Labeling")
                        print("-" * 20)
                    continue
            else:
                print("Error - First Appear isn't good")
                return -1
            if debug_flag:
                print("IncrementLabeling: " + str(new_theta))
                print("-" * 20)
            if new_theta is None or not new_theta:
                continue
            for option in new_theta:
                if debug_flag:
                    print("Option: " + str(option))
                    print("IsExtendable: " + str(IsExtendable(td, option, i)))
                    print("-" * 20)
                if IsExtendable(td, option, i):
                    stack.append((option, i + 1))


def IncrementLabeling2(td: RootedDisjointBranchNiceTreeDecomposition, theta: Dict[str, int], i, c: int):
    """
    Procedure IncrementLabeling receives as input a labeling which we assume to be extendable (see EnumMDS),
    and a label. It generates a new assignment and updates the labels of vertices based on the given label, so that
    the new assignment is legal. [Taken from paper]
    :param td: A rooted disjoint branch nice tree decomposition.
    :param theta: Previous labeling.
    :param i: The index of the vertex in the graph (in Q).
    :param c: The label to be added to the vertex.
    :return:
    """
    new_theta = dict(theta)
    new_theta[td.Q[i]] = c
    return [new_theta]


def IncrementLabeling(td: RootedDisjointBranchNiceTreeDecomposition, theta: Dict[str, int], i, c: int, V_label_S, V_label_W):
    """
    Procedure IncrementLabeling receives as input a labeling which we assume to be extendable (see EnumMDS),
    and a label. It generates a new assignment and updates the labels of vertices based on the given label, so that
    the new assignment is legal. [Taken from paper]
    :param td: A rooted disjoint branch nice tree decomposition.
    :param theta: Previous labeling.
    :param i: The index of the vertex in the graph (in Q).
    :param c: The label to be added to the vertex.
    :param V_label_S: Set of vertices with label S (pre-calculated).
    :param V_label_W: Set of vertices with label W (pre-calculated).
    :return:
    """
    new_theta = dict(theta)
    new_theta[td.Q[i]] = c
    if i == 0:
        return [new_theta]
    current_vertex = td.Q[i]

    K_i = td.nodes[td.first_appear[current_vertex]]["local_neighbors"][current_vertex].intersection(
        {w[0] for w in td.Q[:i]})
    if td.is_semi_nice:
        K_i_new = set()
        len_of_br = len(td.nodes[td.first_appear[current_vertex]]["br"])
        for x in K_i:
            for y in td.nodes[td.first_appear[current_vertex]]["bag"]:
                if y.startswith(x) and len(y) <= len_of_br + 1:
                    K_i_new.add(y)
                    break
        K_i = K_i_new
    else:
        K_i = {x + td.nodes[td.first_appear[current_vertex]]["br"] for x in K_i}
    N_i = K_i.intersection(V_label_S)
    W_i = K_i.intersection(V_label_W)

    flag_of_two = False

    if in_sigma(c):
        for v in K_i:
            if in_rho(theta[v]):
                for l in F_rho:
                    if l == max(R0, theta[v] - 1):
                        new_theta[v] = l
                        break

    if c == SI and (len(N_i) != 0 or len(W_i) != 0):
        return False
    if S0 <= c <= S1:
        if len([w for w in K_i if theta[w] in {SI,W0}]) != 0 or \
                (c == S0 and len(W_i) == 0):
            return False
        else:
            for w in W_i:
                if theta[w] == W1:
                    new_theta[w] = W0
    if in_omega(c):
        if len([w for w in N_i if theta[w] == SI]) != 0 or \
                len(N_i) >= 2 or \
                (len(N_i) == 0 and c == W0) or \
                (len(N_i) != 0 and c == W1):
            return False
        elif c == W0:
            v = N_i.pop()
            if theta[v] == S0:
                return False
            flag_of_two = v
    if in_rho(c) and max(0, 2 - len(N_i)) != c - R0:
        return False
    if flag_of_two:
        new_theta[flag_of_two] = S0
        new_theta2 = dict(new_theta)
        new_theta2[flag_of_two] = S1
        return [new_theta, new_theta2]
    return [new_theta]