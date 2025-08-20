from ortools.sat.python import cp_model

# Define data
num_employees = 4
num_days = 7
num_shifts = 3  # Morning, Afternoon, Night

model = cp_model.CpModel()

# Create shift variables: shift[e][d][s] = 1 if employee e works shift s on day d
shift = {}
for e in range(num_employees):
    for d in range(num_days):
        for s in range(num_shifts):
            shift[(e, d, s)] = model.NewBoolVar(f'shift_e{e}_d{d}_s{s}')

# Constraint: Each shift must be assigned to exactly one employee per day
for d in range(num_days):
    for s in range(num_shifts):
        model.AddExactlyOne(shift[(e, d, s)] for e in range(num_employees))

# Constraint: Each employee works at most one shift per day
for e in range(num_employees):
    for d in range(num_days):
        model.AddAtMostOne(shift[(e, d, s)] for s in range(num_shifts))

# Optional: Fairness constraint (e.g. each employee works ~same number of shifts)
min_shifts = (num_days * num_shifts) // num_employees
max_shifts = min_shifts + 1
for e in range(num_employees):
    total_shifts = sum(shift[(e, d, s)] for d in range(num_days) for s in range(num_shifts))
    model.Add(total_shifts >= min_shifts)
    model.Add(total_shifts <= max_shifts)

# Solve
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Output
if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
    for d in range(num_days):
        print(f'Day {d + 1}')
        for s in range(num_shifts):
            for e in range(num_employees):
                if solver.Value(shift[(e, d, s)]):
                    print(f'  Shift {s}: Employee {e}')
else:
    print("No solution found.")
