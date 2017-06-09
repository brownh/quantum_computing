#!/usr/bin/env python
# Author: Howard Brown
# March 2017

from isakov_wrapper import solve_on_isakov

"""
Problem:
Consider some elements in the form of a graph, where each element
is a vertex connected to some other elements (by edges).

Cut the graph into two graphs of equal number of vertices, such that the
number of connections (edges) between the two groups is minimised.

i.e. for N elements, find two groups of N/2 vertices, with minimum number of edges
connecting group 1 and group 2

Utilize quantum simulator (Isakov simulator) to solve Hamiltonian of lowest energy
to find groups.

Input:
Pairs of numbers (undirected edges) representing connected vertices, where vertices
are indexed from zero.

No edges will be repeated, however edges may be unordered.
Total number of vertices is even.

ex: [(0, 1), (1, 3), (2, 0)]

Output:
Two sets of numbers, representing the two groups each vertex is assigned to.

If the two groups are not of equal size, the solution is considered invalid
and given a score of 0.

ex: [0, 2], [1, 3]
"""

# Test cases

## Initial given example
prob = [(0, 1), (1, 3), (2, 0)]

## Initial given example out of order
# prob = [(0, 1), (2, 0), (1, 3)]

## Initial given example with more edges between vertices
# prob = [(0, 1), (1, 3), (2, 0), (2, 3), (2, 1)]

## Initial given example with additional two vertices and edges
# prob = [(0, 1), (1, 3), (2, 0), (2, 4), (3, 5)]

# prob = [(0, 2), (2, 3), (1, 3)]

# prob = [(0, 1), (1, 3), (2, 3)]

# prob = [(0, 1), (1, 2), (1, 3), (2, 3)]

# prob = [(0, 1), (0, 2), (2, 3)]



def merge_two_dicts(x, y):
	"""
	Merge bias and couplings together
	"""
	z = x.copy()
	z.update(y)
	return z


def best_group(opt_result, verts):
	"""
	Attach vertices to Ising spins
	"""
	a, b = [], []
	for i in xrange(len(opt_result)):
		if opt_result[i] == -1:
			a.append(verts[i])
		else:
			b.append(verts[i])
	return a, b


def vert_degree(input_vertices):
	"""
	Determine the degree of each vertex. Used
	as value in one computation method
	"""
	vertex_map = {}
	for element in input_vertices:
		vertex_map[element] = 0
		for x in prob:
			for vertex in x:
				if element == vertex:
					vertex_map[element] += 1
	return vertex_map


def vert_ind_as_val(input_vertices):
	"""
	Uses vertex index as value for other
	computation method
	"""
	vertex_map = {}
	for element in input_vertices:
		vertex_map[element] = element
	return vertex_map


def drop_groups(input_first, input_second):
	"""
	If there are some groups that do not
	have the same number of vertices in each group
	they should be dropped
	"""
	ret_first, ret_second = [], []
	for idx in xrange(len(input_first)):
		if len(input_first[idx]) == len(input_second[idx]):
			ret_first.append(input_first[idx])
			ret_second.append(input_second[idx])
	return ret_first, ret_second


def get_verts(problem):
	"""
	Determine vertices from input edges
	"""
	verts = []
	for x in problem:
		for element in x:
			if element not in verts:
				verts.append(element)
	return verts


def count_edges(input_first, input_second, problem):
	"""
	Count number of edges between groups that emerged
	from simulator
	"""
	count = 0
	for idx in xrange(len(input_first)):
		for index in xrange(len(input_second)):
			if (input_first[idx], input_second[index]) in problem:
				count += 1
			elif (input_second[index], input_first[idx]) in problem:
				count += 1
	return count


def choose_values(input_verts, run=0):
	"""
	Determine which method of values will
	be used
	"""
	if run == 0:
		return vert_ind_as_val(input_verts)
	else:
		return vert_degree(input_verts)


def coupler(input_vertex_map, num):
	"""
	Create Q and assign appropriate values
	"""
	in_h = {}
	in_J = {}
	for i in xrange(num):
		for j in  xrange(i, num):
			if i == j:
				in_h[(i, i)] = 0
			else:
				in_J[(i, j)] = input_vertex_map[i] * input_vertex_map[j] / num
	couple = merge_two_dicts(in_h, in_J)
	return couple


def obtain_groups(input_results, input_vertices):
	"""
	Call different functions to create groups, drop groups, etc
	Returns the group from the optimal solution from this simulation run
	"""
	best_first, best_second = [], []
	for i in xrange(len(input_results)):
		first_group, second_group = best_group(input_results[i].solution, input_vertices)
		best_first.append(first_group)
		best_second.append(second_group)

	complete_first, complete_second = drop_groups(best_first, best_second)

	return complete_first[0], complete_second[0]


def method_winner(method_one_edges, method_two_edges, method_one_first_group, method_one_second_group, method_two_first_group, method_two_second_group):
	"""
	Looks at results from both simulation runs to determine which
	had the better results
	"""
	if method_one_edges < method_two_edges:
		input_best_first_group = method_one_first_group
		input_best_second_group = method_one_second_group
		input_num_edges = method_one_edges
	else:
		input_best_first_group = method_two_first_group
		input_best_second_group = method_two_second_group
		input_num_edges = method_two_edges
	return input_best_first_group, input_best_second_group, input_num_edges

def main_script(input_vertices, input_num, input_prob, input_run=0):
	"""
	Main code, inputs vertices, number of vertices and problem and
	outputs the number of edges between the two groups
	"""

	input_vert_map = choose_values(input_vertices, input_run)
	input_Q = coupler(input_vert_map, input_num)
	input_results = solve_on_isakov(input_Q)
	input_run_first_group, input_run_second_group = obtain_groups(input_results, input_vertices)
	input_num_edges = count_edges(input_run_first_group, input_run_second_group, input_prob)
	return input_num_edges, input_run_first_group, input_run_second_group


def main():

	vertices = get_verts(prob)

	vertices.sort()

	N = len(vertices)

	num_edges_first_method, run_1_first_group, run_1_second_group = main_script(vertices, N, prob)

	num_edges_second_method, run_2_first_group, run_2_second_group = main_script(vertices, N, prob, input_run=1)

	overall_best_first_group, overall_best_second_group, num_edges = method_winner(num_edges_first_method, num_edges_second_method, run_1_first_group, run_1_second_group, run_2_first_group, run_2_second_group)

	print 'The first group is: ', overall_best_first_group
	print 'The second group is: ', overall_best_second_group
	print 'This solution has ', num_edges, ' edge(s) between the two groups'


if __name__ == '__main__':
    main()