#!/usr/bin/env python3
#
# ---AST Definition---
#
# Exactly what a variable is is left abstract.
# In tests, variables are strings holding the name of the variable..
#
# There are three kinds of expressions:
#
# 1.) Literals, which represent the concept of a possibly
#     negated variable.  This is represented with the `Literal`
#     class.  The `variable` field holds the variable, and the
#     `is_positive` field holds `True` if it's a positive literal,
#     or `False` if its a negative literal.
#
# 2.) Logical and, which represents an AND operation between
#     two subexpressions.  This is represented with the `And`
#     class, which has `left` and `right` fields for subexpressions.
#
# 3.) Logical or, which represents an OR operation between
#     two subexpressions.  This is represented with the `Or`
#     class, which has `left` and `right` fields for subexpressions.
#
# A more compact representation of all the above information is shown
# below in a variant of a BNF grammar:
#
# x ∈ Variable
# b ∈ Boolean ::= True | False
# e ∈ Expression ::= Literal(x, b) | And(e1, e2) | Or(e1, e2)

class Literal:
    def __init__(self, variable, is_positive):
        self.variable = variable
        self.is_positive = is_positive

    def __str__(self):
        if self.is_positive:
            return self.variable
        else:
            return "!{}".format(self.variable)

class Binop:
    def __init__(self, left, right, op_string):
        self.left = left
        self.right = right
        self.op_string = op_string

    def __str__(self):
        return "({} {} {})".format(
            str(self.left),
            self.op_string,
            str(self.right))

class And(Binop):
    def __init__(self, left, right):
        super().__init__(left, right, "&&")

class Or(Binop):
    def __init__(self, left, right):
        super().__init__(left, right, "||")

# naive immutable map implementation
# just does a copy over an underlying dict
class ImmutableMap:
    def __init__(self, mapping = None):
        self.mapping = mapping if mapping is not None else dict()

    def add(self, key, value):
        new_mapping = self.mapping.copy()
        new_mapping[key] = value
        return ImmutableMap(new_mapping)

    def contains(self, key):
        return key in self.mapping

    def get(self, key):
        return self.mapping[key]

class List:
    def __init__(self):
        pass

class Nil(List):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "nil"

class Cons(List):
    def __init__(self, head, tail):
        super().__init__()
        self.head = head
        self.tail = tail
        
    def __str__(self):
        return "cons({}, {})".format(self.head, self.tail)


# add_literal
#
# Takes the following:
# 1.) An instance of `ImmutableMap` where the keys are variables and the
#     values are Python booleans (either `True` or `False`)
# 2.) A variable
# 3.) A Python boolean (either `True` or `False`)
#
# Returns:
# Either a new `ImmutableMap` containing the given variable/boolean binding,
# or None
#
# Purpose:
# Adds the given variable to the given `ImmutableMap` instance, mapping the
# variable to the given boolean. There are three cases of interest upon
# adding a variable to the `ImmutableMap` instance:
# 1.) The `ImmutableMap` instance does not contain the variable.  In this
#     case, the variable/boolean mapping is added, and the new `ImmutableMap`
#     instance is returned
# 2.) The `ImmutableMap` instance contains the variable, and it is mapped to
#     the same boolean as the one passed.  In this case, there is nothing that
#     needs to be added to the `ImmutableMap` instance, and so the
#     `ImmutableMap` instance is returned as-is.
# 3.) The `ImmutableMap` instance contains the variable, but it is mapped to
#     the opposite boolean as the one passed.  For example, the map contains
#     `False`, but the boolean passed was `True`. This means we hit a conflict:
#     a variable must be both true and false at the same time, which is
#     impossible.  As such, in this case None is returned.

def add_literal(immutable_map, variable, boolean):
    if immutable_map.contains(variable):
        if immutable_map.get(variable) == boolean:
            return immutable_map
        else:
            return None
    else:
        return immutable_map.add(variable, boolean)

# solve
#
# Takes the following:
# 1.) A `List` of expressions, using the linked list definition above.
#     `Nil` represents an empty list, and `Cons` represents a non-empty
#     list containing a `head` element followed by the rest of the list,
#     `tail`
# 2.) An `ImmutableMap` instance, where the keys are variables and the
#     values are Python booleans (either `True` or `False`)
#
# Returns:
# An `ImmutableMap` instance mapping variables to Python booleans
# corresponding to a satisfying solution, or None if there is no solution.
#
# Purpose:
# Uses semantic tableau (https://en.wikipedia.org/wiki/Method_of_analytic_tableaux)
# to try to find a satisfying solution.  The list of expressions represents expressions
# which must all be true for a satisfying solution.  The `ImmutableMap` instance
# represents truth values assigned so far for any literals.

def solve(goals, literals):
    # base case
    if isinstance(goals, Nil):
        return literals
    else:
        # list of expressions is non-empty
        if isinstance(goals.head, Literal):
            result = add_literal(literals, goals.head.variable, goals.head.is_positive)
            if result is None:
               return None
            else:
               return solve(goals.tail, result)
        # check if expression is And
        elif isinstance(goals.head, And):
            return solve(Cons(goals.head.left, Cons(goals.head.right, goals.tail)), literals)
        # check if expression is Or
        elif isinstance(goals.head, Or):
            left_side = solve(Cons(goals.head.left, goals.tail), literals)
            # evaluate right side only if left side is unsatisfiable
            if left_side is None:
                return solve(Cons(goals.head.right, goals.tail), literals)
            else:
                return left_side

def solve_one(formula):
    return solve(Cons(formula, Nil()), ImmutableMap())

# tests that should be satisfiable
sat_tests = [And(Or(Literal("a", True),
                    Literal("b", False)),
                 Literal("b", True)), # (a || !b) && b
             And(Or(Literal("x", True),
                    Literal("y", False)),
                 Or(Literal("y", False),
                    Literal("z", True)))] # (x || !y) && (!y || z)

# tests that should be unsatisfiable
unsat_tests = [And(Literal("x", True),
                   Literal("x", False))] # x && !x

def run_tests():
    tests_failed = False
    for test in sat_tests:
        results = solve_one(test)
        if results is None:
            print("Failed: {}".format(test))
            print("\tWas UNSAT, should have been SAT")
            tests_failed = True
        else:
            # print solution
            print("\nSolution for: ", test, "\n")
            print(results.mapping)

    for test in unsat_tests:
        if solve_one(test) is not None:
            print("Failed: {}".format(test))
            print("\tWas SAT, should have been UNSAT")
            tests_failed = True

    if not tests_failed:
        print("\nAll tests passed")

if __name__ == "__main__":
    run_tests()
