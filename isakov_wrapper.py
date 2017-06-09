##########################################################
# Very simple wrapper around Isakov's solver
# September 2015
# Based on John Furness' library, modified for QxHack by 
# Jarred Gallina and Dan Padilha.
##########################################################
import subprocess
import os
import sys

class Result:
    def __init__(self, solution, occurrences, energy_unscaled):
        self.N           = len(solution)
        self.solution    = solution[:]
        self.occurrences = int(occurrences)
        self.energy      = energy_unscaled

def solve_on_isakov(Q):

    """
    results = solve_on_isakov(Q)

    Uses Isakov's solver to solve the given Ising problem (as a single matrix containing both h biases 
    and J couplings). Returns a list of (up to 1000) unique results output by the solver.

    Args:
        Q:  Matrix containing values for couplings (J) and biases (h) for Ising problem to be solved.
            Must be stored as a dictionary, indexed by (i, j):
                If i == j, then the value stored is a bias for qubit i.
                If i != j, then the value stored is a coupling between qubit i and qubit j.
            MUST be upper triangular (j >= i for all). Will raise an exception if not.
            Maximum of 2048 qubits can be used (i.e. 0 <= i,j <= 2048)

    Returns:
        A list of Result objects; one for each solution returned by Isakov solver.

        Result attributes
        solution: list of qubit spins, for example [1, -1, -1, 1, -1]
        occurences: no. of occurences of that solution
        energy: the solution's energy value

    """

    # "Lattice" file which will be read by Isakov's solver, defining the desired problem.
    lattice_file = r'IsakovSolver.lattice'

    # Setting defaults - Automatically detects OS if default is set to None. Uncomment a line to set manually.
    solver_default = None
    #solver_default = r'isakov_linux'
    #solver_default = r'isakov_mac'
    #solver_default = r'isakov_win.exe'
    if solver_default is None:
        solvers = {'win32':r'isakov_win.exe', 'linux2':r'isakov_linux', 'darwin':r'isakov_mac'}
        try:
            solver_default = solvers[sys.platform]
        except KeyError:
            print 'No solver file detected for your system! Try setting manually.'
            raise

    # Setting up Lattice File
    if os.path.isfile(lattice_file) == 1:
        os.remove(lattice_file)

    file = open(lattice_file, "w")
    file.write("Isakov Solver Function File")

    # Work out the max index in Q
    maxs = 0
    for idx,jdx in Q:
        maxs = idx if idx > maxs else maxs
        maxs = jdx if jdx > maxs else maxs
    maxs += 1

    assert maxs <= 2048, "More than 2048 qubits being used!"

    # Print Q values to Lattice File
    for i in range(maxs):
        for j in range(i, maxs):
            if (i,j) in Q:
                file.write("\n%s %s %s" % (i, j, Q[(i, j)]))
            elif (j,i) in Q:
                assert False, "Q must be upper triangular!"
            else:
                file.write("\n%s %s 0" % (i, j))

    file.close()

    # These affect how the solver runs. These are hard-coded in this wrapper
    # simply because there's no need to change them for the Hackathon.
    num_sweeps = str(100)
    num_reads = str(1000)
    

    # Running Isakov Solver by calling as a subprocesses
    args = [solver_default, "-l", lattice_file, "-s", num_sweeps, "-r", num_reads]
    popen = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True)
    
    isakov_output = popen.stdout.read()
    result_lines = isakov_output.splitlines()

    # Parse the output line by line and generate a list of Result instances to return.
    results = []
    for result_line in result_lines:
        result_words = result_line.split()
        assert len(result_words) == 3, "Expected output format of 3 words per line not found."

        occurrences = int(result_words[1])
        spin_string = result_words[2]
        energy_unscaled = float(result_words[0])

        solution = []
        for spin_character in spin_string:
            if spin_character == '-':
                solution.append(-1)
            elif spin_character == '+':
                solution.append(+1)
            else:
                assert False, "Unrecognised output character in spin result encoding string."

        results.append(Result(solution, occurrences, energy_unscaled))

    return results
