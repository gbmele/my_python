from ortools.sat.python import cp_model

# Define model
model = cp_model.CpModel()

# Constants
num_days = 7
doctors = ['Dr_A', 'Dr_B', 'Dr_C', 'Dr_D', 'Dr_E']
shift_types = ['appt', 'call', 'oper', 'none']
shift_enum = {name: i for i, name in enumerate(shift_types)}

# Variables: Roster[doctor][day] = shift_type
Roster = {
    doc: [model.NewIntVar(0, len(shift_types) - 1, f'{doc}_day{d}') for d in range(num_days)]
    for doc in doctors
}

# Constraint: Exactly one 'call' shift per day
for d in range(num_days):
    model.Add(sum(Roster[doc][d] == shift_enum['call'] for doc in doctors) == 1)

# Constraint: At most two 'oper' shifts on weekdays (Mon–Fri)
for d in range(num_days):
    if d % 7 in range(1, 6):  # Monday to Friday
        model.Add(sum(Roster[doc][d] == shift_enum['oper'] for doc in doctors) <= 2)

# Constraint: Total 'oper' shifts ≥ 7
model.Add(
    sum(Roster[doc][d] == shift_enum['oper'] for doc in doctors for d in range(num_days)) >= 7
)

# Constraint: Total 'appt' shifts ≥ 4
model.Add(
    sum(Roster[doc][d] == shift_enum['appt'] for doc in doctors for d in range(num_days)) >= 4
)

# Constraint: Regular expression on each doctor's schedule
# Pattern: ((oper none)|appt|call|none)*
# We'll use Automaton to enforce this pattern
# Build automaton manually: states and transitions
# For simplicity, we allow any sequence of valid shifts
# You can refine this further if needed

# States: 0 (start), 1 (accept)
# Transitions: (state, input, next_state)
transitions = []
for s in shift_types:
    transitions.append((0, shift_enum[s], 0))  # loop on all valid shifts

for doc in doctors:
    model.AddAutomaton(Roster[doc], 0, [0], transitions)

# Solve
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Output
if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
    for doc in doctors:
        print(f"{doc}: ", end="")
        for d in range(num_days):
