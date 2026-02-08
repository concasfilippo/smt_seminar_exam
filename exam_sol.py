
## Exam

# Consider the following Counting game:
#
# A player draws 6 different numbers. The goal is to combine these numbers using the elementary arithmetic operations (+, -, *, /) to obtain a number as close as possible to a given goal. 
# Combining numbers means the following. First, the player chooses an initial number from the starting six numbers in their hand. Then, they choose a second number from their hand (different from the initial one), together with an operation, and compute the result of the operation. Now they choose a third number from their hand (different from the first and the second number), an operation, and compute the results. And so on.
#
# For example, if the user draws the numbers 1, 3, 5, 8, 10 e 50, and the goal number is 462, they can combine their numbers in the following way:
#
# 8 + 1 = 9
# 9 * 50 = 450
# 450 + 10 = 460
# 460 - 3 = 457
# 457 + 5 = 462
#
# Here, the player precisely reached the goal number. However, there are cases in which this is not possible. In such cases, the player has to aim to find the closest possible number to the goal.
# If it is possible to precisely reach the goal number, the players should try to minimize the numbers used. E.g., in the previous game, a better solution would have been:
#
# 50 - 3 = 47
# 47 * 10 = 470
# 470 - 8 = 462 
#
# which only uses 4 numbers instead of 6.
#
# Each number can only be used one time. 
#
# Your task is to implement a function CountingStrategy() that takes as input a list of 6 user numbers and 1 goal number, and returns the winning strategy. 
# The winning strategy should be printed in the following form:
#   Initial number: <n1>
#   Step 1: operation <operation> with number <n2> -> result <r2>
#   Step 2: operation <operation> with number <n3> -> result <r3>
#   ...
#   Final number: <final_result>
#   Distance from goal: <distance>
#
#
# E.g.:
# CountingStrategy([1, 3, 5, 8, 10, 50], 462) should output:
#   Initial number: 50
#   Step 1: operation - with number 3 -> result 47
#   Step 2: operation * with number 10 -> result 470
#   Step 3: operation - with number 8 -> result 462
#   Final number: 462
#   Distance from goal: 0
#


# [Optional]
# After you have implemented the function to find the optimal strategy for the Counting game, consider the following variation of the game.
# The rules are as before, but now an adversary can "attack" the player after their last operation. 
# The attack consists in choosing one number between 1 and 10, and replace it to the user choosen last number to make the final result as far as possible from the goal number.
# E.g., in the previous example, the attacker would have replaced the last number 8 with the number 0, making the player final result be 470 - 0 = 470.
# Hence, in this variant, the player must find a strategy that is resilient to the actions of the attacker. The best strategy will not be the one that gets closest to the goal, but rather the one that, after the worst possible attack, is as close as possible to the goal. 
#
#
# Your task is to implement a function CountingStrategyResilient that takes the same input as CountingStrategy, and returns the optimal strategy for this variation.
# In the output, include:
#    Distance from goal after attack: <distance_after_attack>

# Counting game with Optimize and resilient variant (min-max)

from z3 import *


def _build_model(numbers, goal, k):

    states = [
        [
            [Int(f'n1_{i}'), Int(f'n2_{i}'), Int(f'n3_{i}'), Int(f'n4_{i}'), Int(f'n5_{i}'), Int(f'n6_{i}')],
            [Int(f'used_1_{i}'), Int(f'used_2_{i}'), Int(f'used_3_{i}'), Int(f'used_4_{i}'), Int(f'used_5_{i}'), Int(f'used_6_{i}')],
            Int(f'n_res_{i}'),
            Int(f'n_used_{i}'),
        ]
        for i in range(k)
    ]

    Function = Datatype('Functions')
    Function.declare('add')
    Function.declare('subtract')
    Function.declare('multiply')
    Function.declare('divide')
    Function = Function.create()

    function = [Const(f'f_{i}', Function) for i in range(k)]
    pick1 = [Int(f'pick1_{i}') for i in range(k)]
    pick2 = [Int(f'pick2_{i}') for i in range(k)]

    def _update(state_now, state_next, num1, num2, res):
        return And(
            state_next[0][0] == state_now[0][0],
            state_next[0][1] == state_now[0][1],
            state_next[0][2] == state_now[0][2],
            state_next[0][3] == state_now[0][3],
            state_next[0][4] == state_now[0][4],
            state_next[0][5] == state_now[0][5],

            state_next[1][0] == If(Or(num1 == 0, num2 == 0), state_now[1][0] + 1, state_now[1][0]),
            state_next[1][1] == If(Or(num1 == 1, num2 == 1), state_now[1][1] + 1, state_now[1][1]),
            state_next[1][2] == If(Or(num1 == 2, num2 == 2), state_now[1][2] + 1, state_now[1][2]),
            state_next[1][3] == If(Or(num1 == 3, num2 == 3), state_now[1][3] + 1, state_now[1][3]),
            state_next[1][4] == If(Or(num1 == 4, num2 == 4), state_now[1][4] + 1, state_now[1][4]),
            state_next[1][5] == If(Or(num1 == 5, num2 == 5), state_now[1][5] + 1, state_now[1][5]),

            state_next[2] == res,
            state_next[3] == state_now[3] + 1,
        )

    def add(state_now, state_next, num1, num2):
        if num1 == -1:
            res = state_now[2] + state_now[0][num2]
        elif num2 == -1:
            res = state_now[0][num1] + state_now[2]
        else:
            res = state_now[0][num1] + state_now[0][num2]
        return _update(state_now, state_next, num1, num2, res)

    def subtract(state_now, state_next, num1, num2):
        if num1 == -1:
            res = state_now[2] - state_now[0][num2]
        elif num2 == -1:
            res = state_now[0][num1] - state_now[2]
        else:
            res = state_now[0][num1] - state_now[0][num2]
        return _update(state_now, state_next, num1, num2, res)

    def multiply(state_now, state_next, num1, num2):
        if num1 == -1:
            res = state_now[2] * state_now[0][num2]
        elif num2 == -1:
            res = state_now[0][num1] * state_now[2]
        else:
            res = state_now[0][num1] * state_now[0][num2]
        return _update(state_now, state_next, num1, num2, res)

    def divide(state_now, state_next, num1, num2):
        if num1 == -1:
            res = state_now[2] / state_now[0][num2]
        elif num2 == -1:
            res = state_now[0][num1] / state_now[2]
        else:
            res = state_now[0][num1] / state_now[0][num2]

        if num2 == -1:
            guardia = state_now[2] != 0
        else:
            guardia = state_now[0][num2] != 0

        return And(guardia, _update(state_now, state_next, num1, num2, res))

    opt = Optimize()

    n1, n2, n3, n4, n5, n6 = numbers
    initial_state = And(
        states[0][0][0] == n1,
        states[0][0][1] == n2,
        states[0][0][2] == n3,
        states[0][0][3] == n4,
        states[0][0][4] == n5,
        states[0][0][5] == n6,

        #I can already assign to res variables one of the initial numbers (and possibly save 1 step of k)
        Or(
            And(states[0][2] == n1, states[0][1][0] == 1, states[0][1][1] == 0, states[0][1][2] == 0, states[0][1][3] == 0, states[0][1][4] == 0, states[0][1][5] == 0),
            And(states[0][2] == n2, states[0][1][0] == 0, states[0][1][1] == 1, states[0][1][2] == 0, states[0][1][3] == 0, states[0][1][4] == 0, states[0][1][5] == 0),
            And(states[0][2] == n3, states[0][1][0] == 0, states[0][1][1] == 0, states[0][1][2] == 1, states[0][1][3] == 0, states[0][1][4] == 0, states[0][1][5] == 0),
            And(states[0][2] == n4, states[0][1][0] == 0, states[0][1][1] == 0, states[0][1][2] == 0, states[0][1][3] == 1, states[0][1][4] == 0, states[0][1][5] == 0),
            And(states[0][2] == n5, states[0][1][0] == 0, states[0][1][1] == 0, states[0][1][2] == 0, states[0][1][3] == 0, states[0][1][4] == 1, states[0][1][5] == 0),
            And(states[0][2] == n6, states[0][1][0] == 0, states[0][1][1] == 0, states[0][1][2] == 0, states[0][1][3] == 0, states[0][1][4] == 0, states[0][1][5] == 1)
        ),

        states[0][3] == 1,
    )
    opt.add(initial_state)

    for i in range(k):
        #I've defined -1 as picking intermediate result variable
        opt.add(Or(pick1[i] == -1, And(pick1[i] >= 0, pick1[i] <= 5)))
        opt.add(Or(pick2[i] == -1, And(pick2[i] >= 0, pick2[i] <= 5)))
        # forbid negative intermediate results
        opt.add(states[i][2] >= 0)

    for i in range(k - 1):
        transition = []
        idxs = list(range(-1, 6))

        #Building giant transitions set using for loops (more readable!)
        for a in idxs:
            for b in idxs:
                if a == b: #can't use same variable
                    continue

                transition.append(And(
                    function[i] == Function.add,
                    add(states[i], states[i + 1], a, b),
                    pick1[i] == a,
                    pick2[i] == b,
                ))
                transition.append(And(
                    function[i] == Function.subtract,
                    subtract(states[i], states[i + 1], a, b),
                    pick1[i] == a,
                    pick2[i] == b,
                ))
                transition.append(And(
                    function[i] == Function.multiply,
                    multiply(states[i], states[i + 1], a, b),
                    pick1[i] == a,
                    pick2[i] == b,
                ))
                transition.append(And(
                    function[i] == Function.divide,
                    divide(states[i], states[i + 1], a, b),
                    pick1[i] == a,
                    pick2[i] == b,
                ))

        opt.add(Or(*transition))

        opt.add(And(
            states[i + 1][1][0] < 2,
            states[i + 1][1][1] < 2,
            states[i + 1][1][2] < 2,
            states[i + 1][1][3] < 2,
            states[i + 1][1][4] < 2,
            states[i + 1][1][5] < 2,
        ))

    return opt, states, function, pick1, pick2, Function


def _print_solution(model, states, function, pick1, pick2, k):
    def op_symbol(op):
        op_s = str(op)
        if op_s == "add":
            return "+"
        if op_s == "subtract":
            return "-"
        if op_s == "multiply":
            return "*"
        if op_s == "divide":
            return "/"
        return op_s

    initial_state_val = model.evaluate(states[0][2], model_completion=True)
    print(f"Initial number: {initial_state_val}")

    for t in range(k - 1):
        op = model.evaluate(function[t], model_completion=True)
        op_sym = op_symbol(op)

        p1 = model.evaluate(pick1[t], model_completion=True).as_long()
        p2 = model.evaluate(pick2[t], model_completion=True).as_long()

        res = model.evaluate(states[t + 1][2], model_completion=True)
        # show only the "other number" (not res), like the assignment example
        if p1 == -1 and p2 != -1:
            num_str = str(model.evaluate(states[t][0][p2], model_completion=True))
        elif p2 == -1 and p1 != -1:
            num_str = str(model.evaluate(states[t][0][p1], model_completion=True))
        elif p1 != -1:
            num_str = str(model.evaluate(states[t][0][p1], model_completion=True))
        else:
            num_str = "res"

        print(f"Step {t + 1}: operation {op_sym} with number {num_str} -> result {res}")


def CountingStrategy(numbers, goal, k=6):
    opt, states, function, pick1, pick2, _ = _build_model(numbers, goal, k)

    final_res = states[k - 1][2] #printing purposes
    dist = Abs(final_res - goal)
    used_sum = Sum(states[k - 1][1])

    opt.minimize(dist) #more efficient according to z3 docs
    opt.minimize(used_sum)

    if opt.check() != sat:
        print("No solution found")
        return

    m = opt.model()

    _print_solution(m, states, function, pick1, pick2, k)
    final_val = m.evaluate(final_res, model_completion=True).as_long()
    print(f"Final number: {final_val}")
    print(f"Distance from goal: {abs(final_val - goal)}")


def CountingStrategyResilient(numbers, goal, k=6):
    opt, states, function, pick1, pick2, Function = _build_model(numbers, goal, k)

    last = k - 2
    # force last step to use a real number as the "last chosen number" (not an intermediate result)
    opt.add(pick2[last] >= 0)

    res_before = states[last][2]
    op = function[last]

    # understand value of last used element in the chain of computation (intermediate result or one of the initial)
    def _num_at(state, idx):
        return If(idx == 0, state[0][0],
               If(idx == 1, state[0][1],
               If(idx == 2, state[0][2],
               If(idx == 3, state[0][3],
               If(idx == 4, state[0][4],
               If(idx == 5, state[0][5], -1))))))
    left_val = If(pick1[last] == -1, res_before, _num_at(states[last], pick1[last]))

    # worst-case distance across attack values 1..10 (explicit enumeration)
    worst_dist = Int('worst_dist')
    for attack in range(1, 11):
        attacked_res = If(op == Function.add, left_val + attack,
                          If(op == Function.subtract, left_val - attack,
                             If(op == Function.multiply, left_val * attack,
                                If(op == Function.divide, left_val / attack, left_val))))
        opt.add(worst_dist >= Abs(attacked_res - goal))

    final_res = states[k - 1][2]
    used_sum = Sum(states[k - 1][1])

    opt.minimize(worst_dist)
    opt.minimize(used_sum)

    if opt.check() != sat:
        print("No solution found")
        return

    m = opt.model()

    _print_solution(m, states, function, pick1, pick2, k)
    final_val = m.evaluate(final_res, model_completion=True).as_long()
    print(f"Final number: {final_val}")
    print(f"Distance from goal after attack: {m.evaluate(worst_dist, model_completion=True)}")


import time

if __name__ == '__main__':
    """
    CountingStrategy([3, 5, 6, 8, 9, 10], 317)
    print("---")
    CountingStrategyResilient([3, 5, 6, 8, 9, 10], 317)
    """
    
    def run_examples():
        prompt = (
            "Counting game: given 6 numbers, combine them with +, -, *, / to get as close as possible to a goal. "
            "Each number can be used at most once. If the goal is reachable, prefer fewer numbers used.\n"
            "Resilient variant: after the last operation, an adversary replaces the last chosen number with a value "
            "between 1 and 10 to maximize the distance from the goal. Choose a strategy that minimizes that worst-case distance."
        )
        prompt = (
            "Counting game and Resilient variant"
        )
        print(prompt)
        print("---")

        cases = [
            ([1, 3, 5, 8, 10, 50], 462),
            ([3, 5, 6, 8, 9, 10], 317),
            ([2, 4, 7, 9, 25, 50], 463),
            ([1, 6, 8, 12, 25, 75], 952),
            ([1, 2, 3, 4, 6, 8], 999),
            ([2, 3, 5, 7, 11, 13], 997),
            ([1, 4, 6, 7, 8, 9], 503),
            ([2, 4, 6, 8, 10, 12], 457),
        ]

        for nums, goal in cases:
            print(f"Case: numbers={nums}, goal={goal}")
            t0 = time.time()
            CountingStrategy(nums, goal, k=6)
            t1 = time.time()
            print(f"Time: {t1 - t0:.3f}s")
            print("---")

        for nums, goal in cases:
            print(f"Resilient case: numbers={nums}, goal={goal}")
            t0 = time.time()
            CountingStrategyResilient(nums, goal, k=6)
            t1 = time.time()
            print(f"Time: {t1 - t0:.3f}s")
            print("---")

    run_examples()
