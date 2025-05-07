import re
import math
from itertools import combinations
from scipy.optimize import minimize
import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

def geometric_Method_for_Solving_Linear_Programming(constraints,  objective_function: list[float], Maximization = True):
    """
        Գեոմետրիկ մեթոդը գծային ծրագրավորման խնդիրների լուծման համար (երկու փոփոխականով)։

        :param constraints: Սահմանափակումների ցուցակ, որտեղ յուրաքանչյուր սահմանափակում տրված է (a, b, նշան, c) ձևաչափով։
                            Օրինակ՝ (2, 3, '<=', 12) համապատասխանում է 2x + 3y <= 12։
        :param objective_function: Նպատակային ֆունկցիան ցուցակի տեսքով, օրինակ՝ [3, 5] համապատասխանաբար x և y գործակիցների համար։
        :param Maximization: Եթե True է, լուծումը կլինի առավելագույնը (maximization), եթե False՝ նվազագույնը (minimization)։
        :return: Տափակագծում հնարավոր լուծումների ուսումնասիրությունից ստացված նպատակային ֆունկցիայի օպտիմալ արժեքը և օպտիմալ կետի համարը։
    """

    def satisfies_constraints(x, y, constraints):
        """ Ստուգում է, արդյոք (x, y) կետը բավարարում է բոլոր սահմանափակումներին։ """
        for a, b, sign, c in constraints:
            value = a * x + b * y
            if sign == '<=' and value > c:
                return False
            if sign == '>=' and value < c:
                return False
        return True

    # Միջակայքի որոշում
    x_min, x_max = float('inf'), float('-inf')
    y_min, y_max = float('inf'), float('-inf')

    for a, b, sign, c in constraints:
        if a != 0:
            x_val = c / a
            x_min = min(x_min, x_val)
            x_max = max(x_max, x_val)
        if b != 0:
            y_val = c / b
            y_min = min(y_min, y_val)
            y_max = max(y_max, y_val)

    x_min, x_max = max(0, x_min - 1), x_max + 1
    y_min, y_max = max(0, y_min - 1), y_max + 1

    # X-ի արժեքների միջակայք
    x = np.linspace(x_min, x_max, 1000)
    y_funcs = []
    lines = []

    for a, b, sign, c in constraints:
        if b != 0:
            y_expr = (c - a * x) / b
            y_funcs.append((y_expr, sign))
            lines.append((a, b, c))

    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)

    # Լուծման տարածքի գունավորում
    y_upper = np.full_like(x, y_max)
    y_lower = np.full_like(x, y_min)

    for y_expr, sign in y_funcs:
        plt.plot(x, y_expr, linestyle='dashed' if sign == '>=' else 'solid')
        if sign == '<=':
            y_upper = np.minimum(y_upper, y_expr)
        else:
            y_lower = np.maximum(y_lower, y_expr)

    plt.fill_between(x, y_lower, y_upper, where=y_lower < y_upper, color='grey', alpha=0.5)

    plt.xlabel(r'$x$')
    plt.ylabel(r'$y$')
    plt.grid(True)

    # Հաշվում ենք բոլոր հնարավոր գագաթները (constraint-ների հատման կետերը)
    vertices = []
    for (a1, b1, c1), (a2, b2, c2) in combinations(lines, 2):
        A = np.array([[a1, b1], [a2, b2]])
        B = np.array([c1, c2])
        if np.linalg.det(A) != 0:  # Համակարգը լուծելի է
            vertex = np.linalg.solve(A, B)
            x_v, y_v = vertex
            if x_min <= x_v <= x_max and y_min <= y_v <= y_max and satisfies_constraints(x_v, y_v, constraints):
                vertices.append(vertex)

    # Հաշվում է նաև այն կետերը, որոնք հատվում են x=0 կամ y=0-ի հետ, բայց ստուգում է նրանց համապատասխանությունը
    for a, b, sign, c in constraints:
        if a != 0:  # x=0-ի համար
            y_val = c / b if b != 0 else None
            if y_val is not None and y_min <= y_val <= y_max and satisfies_constraints(0, y_val, constraints):
                vertices.append((0, y_val))
        if b != 0:  # y=0-ի համար
            x_val = c / a if a != 0 else None
            if x_val is not None and x_min <= x_val <= x_max and satisfies_constraints(x_val, 0, constraints):
                vertices.append((x_val, 0))

    # (0,0) կետը կավելացվի **միայն** եթե այն իրականում բավարարում է բոլոր պայմանները
    if satisfies_constraints(0, 0, constraints):
        vertices.append((0, 0))

    if vertices:
        vertices = np.array(vertices)
        plt.scatter(vertices[:, 0], vertices[:, 1], color='red', zorder=5)
        for x_v, y_v in vertices:
            plt.text(x_v, y_v, f'({x_v:.1f}, {y_v:.1f})', fontsize=10, verticalalignment='bottom')

    objectiv_function_values = []

    # Տպում ենք բոլոր ծայրակետերի կոորդինատները
    print("Ծայրակետեր (գագաթներ):")
    unique_vertices = set(tuple(v) for v in vertices)  # Հեռացնում ենք կրկնությունները
    for x_v, y_v in unique_vertices:
        objectiv_function_values.append(x_v * objective_function[0] + y_v * objective_function[1])
        print(f"({x_v:.2f}, {y_v:.2f})")

    plt.show()
    index = objectiv_function_values.index(
        max(objectiv_function_values)) if Maximization else objectiv_function_values.index(
        max(objectiv_function_values))
    solution = max(objectiv_function_values) if Maximization else min(objectiv_function_values)
    return solution, index + 1

def create_simplex_tableau(A, b, signs, c, objective='max', M=10):
    """
    Ստեղծում է սիմպլեքս աղյուսակը՝ տրված մուտքային տվյալներով։

    :param A: (m x n) numpy մատրիցա, որտեղ m սահմանափակումներ, n որոշման փոփոխականներ։
    :param b: m-ի աջ կողմերի վեկտոր։
    :param signs: Սահմանաչափերի նշանների ցուցակ՝ "<=", ">=" կամ "="։
    :param c: Որոշման փոփոխականների նպատակային ֆունկցիայի գործակիցների ցուցակ։
    :param objective: "max" կամ "min"՝ հայտարարելով խնդրի ուղղությունը։ Եթե "min", ապա կատարվում է փոխակերպում։
    :param M: Մեծ դրական թիվ Big M մեթոդի համար (օրինակ՝ 10)։

    :return: Սիմպլեքս աղյուսակ՝ numpy.array տիպով։

    Հատկանիշներ:
        - Եթե որևէ (b[i] < 0) է, ապա նույն տողը բազմապատկվում է -1-ով և փոխվում է սահմանաչափի նշանը։
        - Եթե խնդիրը minimization է, ապա նախապես կատարվում է c-ի փոխակերպում՝ c := -c։
        - Ավելացվում են համապատասխան հավելյալ փոփոխականներ՝
            - "<=" համար՝ slack փոփոխական։
            - ">=" համար՝ surplus (հայտանիշ -1), ապա artificial (հայտանիշ 1)։
            - "=" համար՝ միայն artificial փոփոխական։
        - Big M մեթոդի կիրառմամբ՝
            * Որոշման փոփոխականների արժեքները կլինեն c։
            * Slack և surplus փոփոխականների արժեքները՝ 0։
            * Artificial փոփոխականների արժեքները՝ -M։
        - Սկզբնական objective տողի արժեքները կարգավորվում են Big M մեթոդի համաձայն՝
            - -c + M * (արտերիֆիցիալ փոփոխական ունեցող տողերի գումար)։
"""

    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)
    m, n = A.shape

    # Եթե որևէ b < 0, "համանակարծարկում ենք" տողը
    for i in range(m):
        if b[i] < 0:
            A[i] = -A[i]
            b[i] = -b[i]
            if signs[i] == '<=':
                signs[i] = '>='
            elif signs[i] == '>=':
                signs[i] = '<='
            # "=" մնանում է "="

    # Եթե խնդիրը minimization է, վերափոխում ենք max-ի ձև՝ փոխհարցնելով c-ի նշանը
    if objective.lower() == 'min':
        c = -c

    # Հաշվում ենք հավելյալ փոփոխականների քանակները
    num_slack = sum(1 for s in signs if s == '<=')
    num_surplus = sum(1 for s in signs if s == '>=')
    num_artificial = sum(1 for s in signs if s in ['>=', '='])

    total_cols = n + num_slack + num_surplus + num_artificial + 1  # վերջին սյունը՝ b-ի համար
    tableau = np.zeros((m + 1, total_cols))

    # Կոլոնների սահմանումը:
    col_orig_start = 0
    col_orig_end = n

    col_slack_start = n
    col_slack_end = col_slack_start + num_slack

    col_surplus_start = col_slack_end
    col_surplus_end = col_surplus_start + num_surplus

    col_artificial_start = col_surplus_end
    col_artificial_end = col_artificial_start + num_artificial

    rhs_col = total_cols - 1

    # Հաշվողիչներ
    slack_count = 0
    surplus_count = 0
    artificial_count = 0

    # Լրացնում ենք սահմանափակումների տողերը
    for i in range(m):
        # Դնում ենք decision փոփոխականների գործակիցները:
        tableau[i, col_orig_start:col_orig_end] = A[i]
        if signs[i] == '<=':
            # ≤ սահմանափակում - ավելացնում ենք slack փոփոխական:
            tableau[i, col_slack_start + slack_count] = 1.0
            slack_count += 1
        elif signs[i] == '>=':
            # ≥ սահմանափակում - ավելացնում ենք surplus (գործակից -1) ու հետո artificial:
            tableau[i, col_surplus_start + surplus_count] = -1.0
            surplus_count += 1
            tableau[i, col_artificial_start + artificial_count] = 1.0
            artificial_count += 1
        elif signs[i] == '=':
            # = սահմանափակում - ավելացնում ենք միայն artificial:
            tableau[i, col_artificial_start + artificial_count] = 1.0
            artificial_count += 1
        else:
            raise ValueError("Հայտառված սահմանաչափի նշանը չհայտնաբերում է: " + signs[i])
        # Դնում ենք b-ի արժեքը:
        tableau[i, rhs_col] = b[i]

    # Հիմնական արժեքավորում ենք cost- vector-ը (ոչ թե այն, որ է տողի մեջ)
    # Այս վեկտորը պարունակում է իրայնական արժեքները բոլոր փոփոխականների համար:
    # Decision փոփոխականներ՝ cost = c (եթե min, արդեն փոխվեց)
    # Slack և surplus՝ 0, իսկ artificial՝ -M:
    cost_vector = np.zeros(total_cols - 1)
    cost_vector[col_orig_start:col_orig_end] = c
    # slack և surplus էլ մինչեւ 0, եւ:
    cost_vector[col_artificial_start:col_artificial_end] = -M

    # Նախնական objective տողը, որպես -c (decision-ի համար) և -M (արտిఫիցիալների համար)
    tableau[-1, col_orig_start:col_orig_end] = -c
    tableau[-1, col_artificial_start:col_artificial_end] = -M
    tableau[-1, rhs_col] = 0.0

    # Կատարում ենք այն նախնական Big M կարգավորումը՝
    # յուրաքանչյուր տողի համար, որտեղ կա ատրիտֆիցիալ, ավելացնում ենք M-ով բազմապատկված այդ տողը:
    for i in range(m):
        if signs[i] in ['>=', '=']:
            tableau[-1, :] += M * tableau[i, :]

    return tableau, cost_vector

def compute_objective_row(tableau, cost_vector, tol=1e-9):
    """
    :param tableau: Սիմպլեքս աղյուսակ
    :param cost_vector: Նպատակային ֆունկցիայի գործակիցներ
    :param tol: Զրոյին մոտ թիվ

    Հաշվում է նոր objective տողը I_j - C_j-ի ձևով,
    որպեսզի թույլտրվեն ցիկլային պարամետրերի փոփոխությունները Big M մեթոդում:

    """
    m, total_cols = tableau.shape
    num_constraints = m - 1
    n = total_cols - 1  # excluding RHS
    new_obj = np.zeros(total_cols)

    # Determine basic variable indices in each constraint row:
    basic_indices = {}  # mapping row i -> basic column index
    for i in range(num_constraints):
        for j in range(n):
            if np.abs(tableau[i, j] - 1) < tol:
                # Check if the rest of the column is (almost) zero:
                col_entries = np.delete(tableau[:num_constraints, j], i)
                if np.all(np.abs(col_entries) < tol):
                    basic_indices[i] = j
                    break
    # Now compute for each column j (decision, slack, surplus, artificial):
    for j in range(n):
        sum_term = 0
        for i, basic_j in basic_indices.items():
            sum_term += cost_vector[basic_j] * tableau[i, j]
        new_obj[j] = sum_term - cost_vector[j]
    # RHS column:
    sum_rhs = 0
    for i, basic_j in basic_indices.items():
        sum_rhs += cost_vector[basic_j] * tableau[i, -1]
    new_obj[-1] = sum_rhs
    return new_obj

def solve_simplex_tableau(tableau, cost_vector, num_decision_vars, tol=1e-9, max_iter=1000, objective='max'):
    """
    Կատարում է ստանդարտ սիմպլեքս ալգորիթմը։

        :param tableau: սիմպլեքս աղյուսակ 2D np.array տիպի։
        :param cost_vector: Նպաատակային ֆունկցիայի գործակիցներ։
        :param: Սկզբնական փոփխականների քանակ։
        :param tol: Զրոյին մոտ թիվ (ոչ պարտադիր պարամետր)
        :param max_iter: Իտերացիաների մքասիմալ քանակ
        :param objective: Նպատակային ֆունկցիայի ուղղություն


    :return: Տյուպլ՝ (solution, optimal_value, final_tableau):

    Գործընթաց:
        - Յուրաքանչյուր կրկնության (iter) ժամանակ հաշվարկվում է objective տողը I_j - C_j ձևով։
        - Ընտրվում է pivot սյունը՝ reduced cost-ի ամենամեծ բացասական արժեքով (մաքսիմիզացիայի դեպքում)։
        - Ratio Test-ի միջոցով որոշվում է pivot տողը։
        - Կատարվում է pivot գործողությունը։

    Արտածվող արդյունքներ:
        - solution: Որոշման փոփոխականների արժեքները։
        - optimal_value: Իրական նպատակային ֆունկցիայի արժեքը։
        - final_tableau: Վերջնական սիմպլեքս աղյուսակը։
"""

    m = tableau.shape[0] - 1  # սահմանափակումների քանակը
    total_cols = tableau.shape[1]
    rhs_col = total_cols - 1
    iteration = 0
    while iteration < max_iter:
        # Հաշվում ենք ընթացիկ objective տողը՝ "I_j - C_j" ձևով:
        tableau[-1, :] = compute_objective_row(tableau, cost_vector, tol)
        obj_row = tableau[-1, :-1]
        # Ստուգում ենք օպտիմալություն (մաքսիմալացման դեպքում բոլոր reduced cost-ներ պետք է ունենան առնվազն 0):
        if np.all(obj_row >= -tol):
            break  # optimal

        # Ընտրում ենք pivot column-ը՝ ամենաբացասական արժեք ունեցողը:
        pivot_col = np.argmin(obj_row)

        # Ratio Test՝ ընտրում ենք այն տողը, որտեղ բաժանումը նվազագույնն է:
        ratios = []
        for i in range(m):
            if tableau[i, pivot_col] > tol:
                ratios.append((tableau[i, rhs_col] / tableau[i, pivot_col], i))
        if not ratios:
            raise Exception("The problem is unbounded!")
        pivot_row = min(ratios, key=lambda x: x[0])[1]

        # Պիվոտ գործողություն:
        pivot_element = tableau[pivot_row, pivot_col]
        tableau[pivot_row, :] /= pivot_element
        for i in range(m + 1):
            if i != pivot_row:
                tableau[i, :] -= tableau[i, pivot_col] * tableau[pivot_row, :]

        iteration += 1

    # Եզրափակիչ լուծումը՝ decision փոփոխականների արժեքները ստանալով
    solution = np.zeros(num_decision_vars)
    for j in range(num_decision_vars):
        col = tableau[:m, j]
        if (np.count_nonzero(np.abs(col - 1) < tol) == 1 and
                np.count_nonzero(np.abs(col) < tol) == (m - 1)):
            row_index = np.where(np.abs(col - 1) < tol)[0][0]
            solution[j] = tableau[row_index, rhs_col]
        else:
            solution[j] = 0.0

    optimal_value = tableau[-1, rhs_col]
    if objective.lower() == 'min':
        optimal_value = -optimal_value

    return solution, optimal_value, tableau

def simplex_solver(A, b, signs, c, objective='max', M=10, tol=1e-9, max_iter=1000):
    """
    Լուծում է լինեար ծրագրավորման խնդիր, օգտվելու սիմպլեքս ալգորիթմից, Big M մեթոդով։

    :param A: (m x n) numpy մատրիցա, որտեղ m սահմանափակումներ, n որոշման փոփոխականներ։
    :param b: m-ի աջ կողմերի վեկտոր։
    :param signs: Սահմանաչափերի նշանների ցուցակ՝ "<=", ">=" կամ "="։
    :param c: Որոշման փոփոխականների նպատակային ֆունկցիայի գործակիցների ցուցակ։
    :param objective: "max" կամ "min"՝ հայտարարելով խնդրի ուղղությունը։ Եթե "min", ապա կատարվում է փոխակերպում։
    :param M: Big M մեթոդի համար օգտագործվող մեծ դրական թիվ (օրինակ՝ 10)։
    :param tol: Զրոյին մոտ արժեքի սահման, հաշվումների համար։
    :param max_iter: Իտերացիաների առավելագույն քանակը։
    :return: Tuple՝ (solution, optimal_value, final_tableau)
    """

    def create_simplex_tableau(A, b, signs, c, objective='max', M=10):
        """
        Ստեղծում է սիմպլեքս աղյուսակը՝ տրված մուտքային տվյալներով։

        - Եթե որևէ (b[i] < 0) է, ապա նույն տողը բազմապատկվում է -1-ով և փոխվում է սահմանաչափի նշանը։
        - Եթե խնդիրը minimization է, ապա նախապես կատարվում է c-ի փոխակերպում՝ c := -c։
        - Ավելացվում են համապատասխան հավելյալ փոփոխականներ՝
            - "<=" համար՝ slack փոփոխական։
            - ">=" համար՝ surplus (հայտանիշ -1), ապա artificial (հայտանիշ 1)։
            - "=" համար՝ միայն artificial փոփոխական։
        - Big M մեթոդի կիրառմամբ՝
            * Decision փոփոխականների արժեքները՝ c։
            * Slack և surplus փոփոխականների արժեքները՝ 0։
            * Artificial փոփոխականների արժեքները՝ -M։
        - Նախնական objective տողի արժեքները կարգավորվում են Big M մեթոդի համաձայն՝
            - -c + M * (արտերիֆիցիալ փոփոխական ունեցող տողերի գումար)։
        """
        A = np.array(A, dtype=float)
        b = np.array(b, dtype=float)
        c = np.array(c, dtype=float)
        m, n = A.shape

        # Եթե որևէ b < 0, "համանակարծարկում ենք" տողը
        for i in range(m):
            if b[i] < 0:
                A[i] = -A[i]
                b[i] = -b[i]
                if signs[i] == '<=':
                    signs[i] = '>='
                elif signs[i] == '>=':
                    signs[i] = '<='
                # "=" դեռ մնանում է "="

        # Եթե խնդիրը minimization է, վերափոխում ենք max-ի ձև՝ փոխհարցնելով c-ի նշանը
        if objective.lower() == 'min':
            c = -c

        # Հաշվում ենք հավելյալ փոփոխականների քանակները
        num_slack = sum(1 for s in signs if s == '<=')
        num_surplus = sum(1 for s in signs if s == '>=')
        num_artificial = sum(1 for s in signs if s in ['>=', '='])

        total_cols = n + num_slack + num_surplus + num_artificial + 1  # վերջին սյունը՝ b-ի համար
        tableau = np.zeros((m + 1, total_cols))

        # Կոլոնների սահմանումը:
        col_orig_start = 0
        col_orig_end = n

        col_slack_start = n
        col_slack_end = col_slack_start + num_slack

        col_surplus_start = col_slack_end
        col_surplus_end = col_surplus_start + num_surplus

        col_artificial_start = col_surplus_end
        col_artificial_end = col_artificial_start + num_artificial

        rhs_col = total_cols - 1

        # Հաշվողիչներ
        slack_count = 0
        surplus_count = 0
        artificial_count = 0

        # Լրացնում ենք սահմանափակումների տողերը
        for i in range(m):
            # Դնում ենք decision փոփոխականների գործակիցները:
            tableau[i, col_orig_start:col_orig_end] = A[i]
            if signs[i] == '<=':
                # ≤ սահմանափակում - ավելացնում ենք slack փոփոխական:
                tableau[i, col_slack_start + slack_count] = 1.0
                slack_count += 1
            elif signs[i] == '>=':
                # ≥ սահմանափակում - ավելացնում ենք surplus (գործակից -1) ու հետո artificial:
                tableau[i, col_surplus_start + surplus_count] = -1.0
                surplus_count += 1
                tableau[i, col_artificial_start + artificial_count] = 1.0
                artificial_count += 1
            elif signs[i] == '=':
                # = սահմանափակում - ավելացնում ենք միայն artificial:
                tableau[i, col_artificial_start + artificial_count] = 1.0
                artificial_count += 1
            else:
                raise ValueError("Հայտառված սահմանաչափի նշանը չհայտնաբերում է: " + signs[i])
            # Դնում ենք b-ի արժեքը:
            tableau[i, rhs_col] = b[i]

        # Հիմնական արժեքավորում ենք cost- vector-ը (չկա table-ի objective տողում)
        cost_vector = np.zeros(total_cols - 1)
        cost_vector[col_orig_start:col_orig_end] = c
        # Slack և surplus փոփոխականները՝ 0, իսկ artificial՝ -M:
        cost_vector[col_artificial_start:col_artificial_end] = -M

        # Նախնական objective տողը, որպես -c (decision-ի համար) և -M (արտիֆիցիալների համար)
        tableau[-1, col_orig_start:col_orig_end] = -c
        tableau[-1, col_artificial_start:col_artificial_end] = -M
        tableau[-1, rhs_col] = 0.0

        # Կատարում ենք նախնական Big M կարգավորումը՝
        # յուրաքանչյուր տողի համար, որտեղ կա ատրիտֆիցիալ, ավելացնում ենք M-ով բազմապատկված այդ տողը:
        for i in range(m):
            if signs[i] in ['>=', '=']:
                tableau[-1, :] += M * tableau[i, :]

        return tableau, cost_vector

    def compute_objective_row(tableau, cost_vector, tol=1e-9):
        """
        Հաշվում է նոր objective տողը I_j - C_j-ի ձևով,
       ՝ թույլ տալով ցիկլային պարամետրերի փոփոխությունները Big M մեթոդում։

        :param tableau: Սիմպլեքս աղյուսակ
        :param cost_vector: Նպատակային ֆունկցիայի գործակիցների վեկտոր
        :param tol: Զրոյին մոտ թիվ
        :return: Նոր objective տողը, numpy վեկտոր
        """
        m, total_cols = tableau.shape
        num_constraints = m - 1
        n = total_cols - 1  # առանց b-ի սյունի
        new_obj = np.zeros(total_cols)

        # Հասկանում ենք յուրաքանչյուր սահմանափակող տողի basic փոփոխականների ինդեքսը:
        basic_indices = {}  # հախտվում է տողի i -> basic սյունի ինդեքսը
        for i in range(num_constraints):
            for j in range(n):
                if np.abs(tableau[i, j] - 1) < tol:
                    # Համոզվենք, որ մնացած սյունը (հետևած տողերը) 0-ի շուրջ է:
                    col_entries = np.delete(tableau[:num_constraints, j], i)
                    if np.all(np.abs(col_entries) < tol):
                        basic_indices[i] = j
                        break

        # Հաշվում ենք I_j - C_j յուրաքանչյուր սյունի համար:
        for j in range(n):
            sum_term = 0
            for i, basic_j in basic_indices.items():
                sum_term += cost_vector[basic_j] * tableau[i, j]
            new_obj[j] = sum_term - cost_vector[j]
        # Հաշվում ենք RHS-ի համար:
        sum_rhs = 0
        for i, basic_j in basic_indices.items():
            sum_rhs += cost_vector[basic_j] * tableau[i, -1]
        new_obj[-1] = sum_rhs
        return new_obj

    def solve_simplex_tableau(tableau, cost_vector, num_decision_vars, tol=1e-9, max_iter=1000, objective='max'):
        """
        Կատարում է ստանդարտ սիմպլեքս ալգորիթմը։

        :param tableau: Սիմպլեքս աղյուսակ (2D numpy.array)
        :param cost_vector: Նպատակային ֆունկցիայի գործակիցների վեկտոր
        :param num_decision_vars: Decision փոփոխականների քանակը
        :param tol: Զրոյին մոտ թիվ
        :param max_iter: Իտերացիաների առավելագույն քանակը
        :param objective: "max" կամ "min"՝ հայտարարելու համար խնդիրի ուղղությունը
        :return: Tuple՝ (solution, optimal_value, final_tableau)
        """
        m = tableau.shape[0] - 1  # սահմանափակումների քանակը
        total_cols = tableau.shape[1]
        rhs_col = total_cols - 1
        iteration = 0

        while iteration < max_iter:
            # Հաշվում ենք ընթացիկ objective տողը՝ "I_j - C_j" ձևով:
            tableau[-1, :] = compute_objective_row(tableau, cost_vector, tol)
            obj_row = tableau[-1, :-1]
            # Ստուգում ենք օպտիմալությունը (մաքսիմալացման դեպքում բոլոր reduced cost-ներ պետք է լինեն ≥ 0):
            if np.all(obj_row >= -tol):
                break  # optimal solutions achieved

            # Ընտրում ենք pivot սյունը՝ ամենամեծ բացասական reduced cost-ի հիման վրա:
            pivot_col = np.argmin(obj_row)

            # Ratio Test՝ ընտրում ենք այն տողը, որտեղ բաժանումը նվազագույնն է:
            ratios = []
            for i in range(m):
                if tableau[i, pivot_col] > tol:
                    ratios.append((tableau[i, rhs_col] / tableau[i, pivot_col], i))
            if not ratios:
                raise Exception("The problem is unbounded!")
            pivot_row = min(ratios, key=lambda x: x[0])[1]

            # Պիվոտ գործողություն:
            pivot_element = tableau[pivot_row, pivot_col]
            tableau[pivot_row, :] /= pivot_element
            for i in range(m + 1):
                if i != pivot_row:
                    tableau[i, :] -= tableau[i, pivot_col] * tableau[pivot_row, :]

            iteration += 1

        # Հաշվում ենք վերջնական լուծումը՝ decision փոփոխականների արժեքները վերցնելով:
        solution = np.zeros(num_decision_vars)
        for j in range(num_decision_vars):
            col = tableau[:m, j]
            if (np.count_nonzero(np.abs(col - 1) < tol) == 1 and
                    np.count_nonzero(np.abs(col) < tol) == (m - 1)):
                row_index = np.where(np.abs(col - 1) < tol)[0][0]
                solution[j] = tableau[row_index, rhs_col]
            else:
                solution[j] = 0.0

        optimal_value = tableau[-1, rhs_col]
        if objective.lower() == 'min':
            optimal_value = -optimal_value

        return solution, optimal_value, tableau

    # Ստեղծում ենք սկզբնական սիմպլեքս աղյուսակը և արժեքների վեկտորը:
    tableau, cost_vector = create_simplex_tableau(A, b, signs, c, objective, M)
    num_decision_vars = len(c)
    solution, optimal_value, final_tableau = solve_simplex_tableau(tableau, cost_vector, num_decision_vars, tol,
                                                                   max_iter, objective)
    solution_list = [float(i) for i in solution]
    return solution_list, float(optimal_value)

def get_dual(c, A, b, signs, direction):
    """
    Գծային ծրագրավորման primal խնդրի հիման վրա կազմում է նրա երկկը (dual) տարբերակը։

    :param c: Primal օբյեկտիվ ֆունկցիայի գործակիցների ցուցակ (x փոփոխականների համար)։
    :param A: (m x n) numpy մատրիցա, որտեղ m սահմանափակումներ են, n որոշման փոփոխականներ։
    :param b: m սահմանափակումների աջ կողմի արժեքների վեկտոր։
    :param signs: Սահմանափակումների նշանների ցուցակ՝ "<=", ">=" կամ "="։
    :param direction: Primal խնդրի նպատակային ուղղությունը՝ "min" կամ "max"։
    :return: Tuple՝ (dual_c, dual_A, dual_b, dual_signs, dual_var_signs, dual_direction)
        - dual_c: Dual օբյեկտիվ ֆունկցիայի գործակիցների վեկտոր։
        - dual_A: Dual սահմանափակումների մատրիցա։
        - dual_b: Dual սահմանափակումների աջ կողմի արժեքների վեկտոր։
        - dual_signs: Dual սահմանափակումների նշանների ցուցակ (հիմնականում բոլորն '<=')։
        - dual_var_signs: Dual փոփոխականների սահմանվածության ցուցակ ('>=', 'free')։
        - dual_direction: Dual խնդրի ուղղությունը՝ "max" կամ "min"։
"""

    m, n = A.shape  # m սահմանափակում, n փոփոխական

    # Հիմնական dual փոփոխականի համար, հաշվենք բազմապատկիչ k,
    # որտեղ՝ k = -1, եթե primals-ի սահմանափակումը "<=" է,
    # իսկ k = 1, եթե սահմանափակումը ">=" կամ "=" է:
    k = np.ones(m)
    dual_var_signs = []  # dual փոփոխականների սահմանվածություն
    for i, s in enumerate(signs):
        if s == '<=':
            k[i] = -1
            dual_var_signs.append('>=')  # y_i >= 0
        elif s == '>=':
            k[i] = 1
            dual_var_signs.append('>=')  # y_i >= 0
        elif s == '=':
            k[i] = 1
            dual_var_signs.append('free')  # ազատ
        else:
            raise ValueError("Սահմանափակումների նշումները պետք է լինեն '<=', '>=', կամ '='")

    # Dual օբյեկտիվի կոեֆիցիանտները՝
    # dual-ի օբյեկտիվը՝ maximize(sum(k[i]*b[i]*y_i)), եթե primals-ը minimization:
    dual_c = k * b  # վեկտոր (հաստատում ենք, որ դա տեղադրվում է dual-ի օբյեկտիվի կոեֆիցիանտներում)

    # Dual սահմանափակումները՝ յուրաքանչյուր primals-ի փոփոխականի համար:
    # Համաձայն dual-ի կանոնների, Dual սահմանափակումը՝
    #   sum_{i=1}^{m} (-k[i]*A[i,j]) * y_i <= c[j], j = 0,..., n-1.
    dual_A = np.empty((n, m))
    for j in range(n):
        for i in range(m):
            dual_A[j, i] = -k[i] * A[i, j]

    # Dual-ի սահմանափակումների աջ կողմը՝ primalsի օբյեկտիվի կոեֆիցիանտները:
    dual_b = c.copy()

    # Dual սահմանափակումների նշումները՝ բոլոր dual սահմանափակումները տվյալ ձևով՝ "<=",
    # քանի որ primals-ի փոփոխականները ենթադրում ենք, որ շատացնում են x >= 0:
    dual_signs = ['<='] * n

    # primals-ի ուղղությունից կախված, dual-ի ուղղությունը հետևյալն է.
    # Եթե primals-ը minimization է, dual-ը կլինի maximization, և հակառակ:
    if direction == 'min':
        dual_direction = 'max'
    elif direction == 'max':
        dual_direction = 'min'
    else:
        raise ValueError("direction-ի արժեքը պետք է լինի 'min' կամ 'max'")

    return dual_c, dual_A, dual_b, dual_signs, dual_var_signs, dual_direction

def is_integer_solution(solution, tol=1e-6):
    """Վերադարձնում է True, եթե բոլոր արժեքները ամբողջ են"""
    return all(abs(x - round(x)) < tol for x in solution)

def add_gomory_cut(num_decision_vars, tableau, tol=1e-9):
    """
    Գոմորի կրճատման մեթոդ (Gomory cut)՝ բազային decision փոփոխականի համար։

    :param num_decision_vars: Decision փոփոխականների քանակը։
    :param tableau: Tableau-ը (մատրից), որը ներկայացնում է ընթացիկ Simplex ալգորիթմի վիճակը։
    :param tol: Թույլատրելի շեղում փոքր թվային սխալների համար (default արժեքը 1e-9)։
    :return: Վերադարձնում է նոր սահմանափակող տողի (constraint row) գործակիցների զանգվածը
             և աջ կողմի արժեքը (RHS), եթե ֆրակցիոնալ արժեք ունեցող բազային փոփոխական գտնվել է։
             Հակառակ դեպքում վերադարձնում է (None, None)։
"""

    m = tableau.shape[0] - 1
    chosen_row = None
    basic_var_index = None
    best_frac = 0
    for i in range(m):
        for j in range(num_decision_vars):
            col = tableau[:m, j]
            # Այստեղ էլ օգտագործում ենք զույգ փակիչներ
            if (np.abs(tableau[i, j] - 1) < tol) and (np.all(np.abs(np.delete(col, i)) < tol)):
                x_val = tableau[i, -1]
                frac = x_val - np.floor(x_val)
                if frac > tol and frac > best_frac:
                    best_frac = frac
                    chosen_row = i
                    basic_var_index = j
                break
    if chosen_row is None:
        return None, None
    new_row = np.zeros(num_decision_vars)
    new_row[basic_var_index] = 1
    new_rhs = np.floor(tableau[chosen_row, -1])
    return new_row, new_rhs

def solve_integer_lp_gomory(A, b, signs, c, objective='max', M=10, tol=1e-6, max_iter=20):
    """
        Գոմորի կրճատումների մեթոդով ամբողջ թիվ լուծում գտնել գծային ծրագրավորման խնդրի համար։

        :param A: Սահմանափակումների գործակիցների մատրից։
        :param b: Սահմանափակումների աջ կողմի արժեքների վեկտոր։
        :param signs: Սահմանափակումների նշանների ցուցակ (օրինակ՝ ['<=', '>=', '='])։
        :param c: Նպատակային ֆունկցիայի գործակիցների վեկտոր։
        :param objective: Նպատակային ֆունկցիայի ուղղությունը՝ 'max' կամ 'min' (default՝ 'max')։
        :param M: Մեծ թվի մեթոդի մեջ օգտագործվող մեծ թիվը (default՝ 10)։
        :param tol: Թույլատրելի շեղում փոքր թվային սխալների համար (default՝ 1e-6)։
        :param max_iter: Գոմորի կրճատումների առավելագույն քանակը (default՝ 20)։
        :return: Վերադարձնում է ամբողջ թվերի լուծման ցուցակը և նպատակային ֆունկցիայի արժեքը։
    """

    iteration = 0
    while iteration < max_iter:
        tableau, cost_vector = create_simplex_tableau(A, b, signs, c, objective, M)
        solution, opt_val, final_tableau = solve_simplex_tableau(tableau, cost_vector, num_decision_vars=len(c),
                                                                 objective=objective)
        if is_integer_solution(solution, tol):
            solution_list = [int(i) for i in solution]
            return solution_list, opt_val
        new_row, new_rhs = add_gomory_cut(len(c), final_tableau, tol)
        if new_row is None:
            print("Հնարավոր չէ գեներացնել rounding cut-ը:")
            break
        A = np.vstack([A, new_row])
        b = np.append(b, new_rhs)
        signs = signs + ["<="]
        iteration += 1
    solution_list = [int(i) for i in solution]
    return solution_list, opt_val

def qp_solver_for_min(objective: str, constraints: list):
    """
        Լուծում է ոչ գծային (կամ գծային) օպտիմալացման խնդիր՝ min նպատակային ֆունկցիայով,
        օգտագործելով SciPy-ի `minimize` ֆունկցիան և սահմանափակումներ որպես տողային արտահայտություններ։

        :param objective: Նպատակային ֆունկցիա՝ որպես տող (օրինակ՝ 'x1**2 + 3*x2 + x1*x2')։
        :param constraints: Սահմանափակումների ցուցակ՝ տողային տեսքով (օրինակ՝ ['x1 + x2 <= 10', 'x2 >= 2'])։
        :return: Բառարան (dict) հետևյալ կառուցվածքով՝
            {
                'optimal_value': նպատակի ֆունկցիայի նվազագույն արժեքը՝ կլորացված մինչև 5 նիշ,
                'variables': փոփոխականների օպտիմալ արժեքները՝ { 'x1': արժեք, 'x2': արժեք, ... }
            }
    """

    # Բաղադրիչ փոփոխականների անունները հայտնաբերել
    var_names = sorted(set(re.findall(r'\bx\d+\b', objective)))
    var_indices = {var: i for i, var in enumerate(var_names)}

    # Նպատակային ֆունկցիան որպես ֆունկցիա
    def obj_func(x):
        local_vars = {var: x[i] for var, i in var_indices.items()}
        return eval(objective, {}, local_vars)

    # Սահմանափակումների մշակումը
    scipy_constraints = []
    for constraint in constraints:
        if '<=' in constraint:
            lhs, rhs = constraint.split('<=')
            op = '<='
        elif '>=' in constraint:
            lhs, rhs = constraint.split('>=')
            op = '>='
        elif '==' in constraint:
            lhs, rhs = constraint.split('==')
            op = '=='
        else:
            raise ValueError(f"Invalid constraint: {constraint}")

        lhs = lhs.strip()
        rhs = rhs.strip()

        def constraint_func_factory(lhs, rhs, op):
            def constraint_func(x):
                local_vars = {var: x[i] for var, i in var_indices.items()}
                left_val = eval(lhs, {}, local_vars)
                right_val = eval(rhs, {}, local_vars)
                if op == '<=':
                    return right_val - left_val
                elif op == '>=':
                    return left_val - right_val
                elif op == '==':
                    return left_val - right_val
            return constraint_func

        scipy_constraints.append({
            'type': 'ineq' if op in ('<=', '>=') else 'eq',
            'fun': constraint_func_factory(lhs, rhs, op)
        })

    # Սկզբնական ենթադրություն (բոլոր x-ը = 1)
    x0 = np.ones(len(var_names))

    result = minimize(obj_func, x0, constraints=scipy_constraints)

    solution = {var: round(result.x[i], 5) for var, i in var_indices.items()}
    return {
        'optimal_value': round(result.fun, 5),
        'variables': solution
    }

def qp_solver_for_max(objective: str, constraints: list):
    """
        Լուծում է ոչ գծային (կամ գծային) օպտիմալացման խնդիր՝ min նպատակային ֆունկցիայով,
        օգտագործելով SciPy-ի `minimize` ֆունկցիան և սահմանափակումներ որպես տողային արտահայտություններ։

        :param objective: Նպատակային ֆունկցիա՝ որպես տող (օրինակ՝ 'x1**2 + 3*x2 + x1*x2')։
        :param constraints: Սահմանափակումների ցուցակ՝ տողային տեսքով (օրինակ՝ ['x1 + x2 <= 10', 'x2 >= 2'])։
        :return: Բառարան (dict) հետևյալ կառուցվածքով՝
            {
                'optimal_value': նպատակի ֆունկցիայի նվազագույն արժեքը՝ կլորացված մինչև 5 նիշ,
                'variables': փոփոխականների օպտիմալ արժեքները՝ { 'x1': արժեք, 'x2': արժեք, ... }
            }
    """

    import numpy as np
    from scipy.optimize import minimize
    import re

    # Ներբեռնենք փոփոխականները
    var_names = sorted(set(re.findall(r'\bx\d+\b', objective + ' ' + ' '.join(constraints))))
    var_indices = {var: i for i, var in enumerate(var_names)}

    # Փոխում ենք նշանը առավելեցման համար
    def obj_func(x):
        local_env = {var: x[i] for var, i in var_indices.items()}
        return -eval(objective, {}, local_env)  # maximize -> minimize -f

    # Սահմանափակումներ
    scipy_constraints = []
    for constraint in constraints:
        if '<=' in constraint:
            lhs, rhs = constraint.split('<=')
            op = '<='
        elif '>=' in constraint:
            lhs, rhs = constraint.split('>=')
            op = '>='
        elif '==' in constraint:
            lhs, rhs = constraint.split('==')
            op = '=='
        else:
            raise ValueError(f"Invalid constraint: {constraint}")

        lhs, rhs = lhs.strip(), rhs.strip()

        def make_func(lhs, rhs, op):
            def func(x):
                local_env = {var: x[i] for var, i in var_indices.items()}
                left = eval(lhs, {}, local_env)
                right = eval(rhs, {}, local_env)
                if op == '<=':
                    return right - left
                elif op == '>=':
                    return left - right
                elif op == '==':
                    return left - right
            return func

        scipy_constraints.append({
            'type': 'eq' if op == '==' else 'ineq',
            'fun': make_func(lhs, rhs, op)
        })

    # ➕ Չբաց թողնենք x1 >= 0, x2 >= 0 սահմանափակումները
    for var in var_names:
        idx = var_indices[var]
        scipy_constraints.append({
            'type': 'ineq',
            'fun': lambda x, i=idx: x[i]
        })

    # Սկզբնական կետ
    x0 = np.ones(len(var_names))

    result = minimize(obj_func, x0, constraints=scipy_constraints)

    solution = {var: round(result.x[i], 5) for var, i in var_indices.items()}
    return {
        'optimal_value': -result.fun,  # դարձնել обратно max
        'variables': solution
    }

def check_extremum_direction(expr_str):
    """
        Վերլուծում է ֆունկցիայի երկրորդ կարգի ածանցյալները՝ Հեսսիանի մատրիցի հիման վրա,
        որոշելու համար նպատակի ֆունկցիայի ծայրակետերի բնույթը (min, max կամ անհայտ)։

        :param expr_str: Տողային արտահայտություն (օրինակ՝ 'x1**2 + x2**2 - x1*x2')։
        :return: 'min' եթե Հեսսիանի բոլոր գլխամասերը դրական են, 'max' եթե փոփոխակ փոխելով նվազում է արժեքը,
                 կամ 'undefined' եթե որոշել հնարավոր չէ (օրինակ՝ սիմետրիկ մատրիցը ունի զրոյական գլխամասեր)։
    """

    vars = sp.symbols('x1:10')  # ստեղծում է x1, x2, ..., x9

    # Փորձում ենք պարզել՝ որ փոփոխականներն են օգտագործվել
    expr = sp.sympify(expr_str)
    used_vars = sorted(expr.free_symbols, key=lambda v: str(v))
    n = len(used_vars)

    # Հեսսիանի մատրից
    H = sp.hessian(expr, used_vars)

    # Սիլվեստրի չափանիշի կիրառություն
    def sylvester_criterion(H):
        for k in range(1, H.shape[0] + 1):
            minor = H[:k, :k]
            if minor.det() <= 0:
                return None if minor.det() == 0 else "max"
        return "min"

    result = sylvester_criterion(H)
    return result or "undefined"

def qp_solver(ogj_func, constrains):
    """
        Լուծում է քվադրատային ծրագրավորման խնդիր՝ հաշվի առնելով նպատակի ֆունկցիայի ծայրակետերի բնույթը (min կամ max)։

        Արտաքին արտահայտությունը որոշում է, թե արդյոք նպատակի ֆունկցիան պետք է լինի նվազագույն կամ առավելագույն։
        Դրանից հետո համապատասխան լուծման մեթոդը կիրառում է՝ նվազագույնի կամ առավելագույնի համար։

        :param ogj_func: Տողային արտահայտություն (ֆունկցիա), որը ներկայացնում է նպատակի ֆունկցիան (օրինակ՝ 'x1**2 + x2**2').
        :param constrains: Սահմանափակումներ, որոնք պետք է պահպանվեն։ Դրանք կարող են լինել ինչպես սահմանափակված, այնպես էլ հավասարության ձևով։

        :return: Լուծում (նպատակային արժեքը և փոփոխականները), հաշված ըստ նախորդ մեթոդներից մեկի՝ նվազագույն կամ առավելագույն։
    """

    if check_extremum_direction(ogj_func,) == "min":
        return qp_solver_for_min(ogj_func, constrains)
    elif check_extremum_direction(ogj_func,) == "max":
        return qp_solver_for_max(ogj_func, constrains)

def check_unimodal(func_str, graph=False, domain=(-10, 10), num_points=1000):
    """
    Ստուգում է, արդյոք տրված ֆունկցիան (ստորազգուշացում որպես string)
    ունի մեկ ինքնաշխատ մոդա՝ որը գտնվում է միջակայքի ներսում:

    Այս տարբերակում միայն այն ֆունկցիաները կվերադարձնեն True, որոնք ունեն
    տրամաբանական «բարձրյալ» կետ ներքին մեջ (և ոչ մոնոտոնները):

    :param func_str: Ֆունկցիան որպես string, օրինակ "x**2 - 4*x + 3"
    :param graph: Եթե True, ցուցադրում է ֆունկցիայի գրաֆիկը (հիմնականը False)
    :param domain: Նմուշավորման միջակայք, հիմնականը (-10, 10)
    :param num_points: Նմուշավորման կետերի քանակը (հիմնականում 1000)
    :return: True, եթե ֆունկցիան ունի տրված միջակայքում ներքին mode, False հակառակ դեպքում
    """
    # Ստեղծում ենք symbol-ները և վերափոխում expression-ը
    x = sp.symbols('x')
    expr = sp.sympify(func_str)

    # Ստանում ենք աշխատող ֆունկցիա numpy-ի համար
    f = sp.lambdify(x, expr, "numpy")

    # Նմուշավորում ենք տվյալ միջակայքում
    xs = np.linspace(domain[0], domain[1], num_points)
    fs = f(xs)

    # Հաշվում ենք առաջին անկյունի առաջին վերլուծական փոփոխությունը՝ ըստ նիշի
    diffs = np.diff(fs)

    eps = 1e-8
    transitions = 0
    last_sign = None
    for d in diffs:
        # հաշվում ենք d-ի նշանը, եթե d-ի modulus-ը փոքր է eps-ի, ապա 0
        sign = np.sign(d) if abs(d) > eps else 0
        if sign == 0:
            continue
        if last_sign is None:
            last_sign = sign
        elif sign != last_sign:
            transitions += 1
            last_sign = sign

    # Այժմ, ըստ այս սահմանման, 0 փոփոխություն նշանակում է մոնոտոն,
    # իսկ unimodal համար պետք է լինի 1 փոխում, ինչը ցույց է տալիս
    # աճման և իջման հոսք, որտեղ ինտերյոր մոդա է:
    strictly_unimodal = (transitions == 1)

    if graph:
        plt.figure(figsize=(8, 4))
        plt.plot(xs, fs, label=f"f(x) = {func_str}")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.title("Ֆունկցիայի գրաֆիկ")
        plt.legend()
        plt.grid(True)
        plt.show()

    return strictly_unimodal

def check_unimodal(func_str, graph=False, domain=(-10, 10), num_points=1000):
    """
    Ստուգում է, արդյոք տրված ֆունկցիան (ստորազգուշացում որպես string)
    ունի մեկ ինքնաշխատ մոդա՝ որը գտնվում է միջակայքի ներսում:

    Այս տարբերակում միայն այն ֆունկցիաները կվերադարձնեն True, որոնք ունեն
    տրամաբանական «բարձրյալ» կետ ներքին մեջ (և ոչ մոնոտոնները):

    :param func_str: Ֆունկցիան որպես string, օրինակ "x**2 - 4*x + 3"
    :param graph: Եթե True, ցուցադրում է ֆունկցիայի գրաֆիկը (հիմնականը False)
    :param domain: Նմուշավորման միջակայք, հիմնականը (-10, 10)
    :param num_points: Նմուշավորման կետերի քանակը (հիմնականում 1000)
    :return: True, եթե ֆունկցիան ունի տրված միջակայքում ներքին mode, False հակառակ դեպքում
    """
    # Ստեղծում ենք symbol-ները և վերափոխում expression-ը
    x = sp.symbols('x')
    expr = sp.sympify(func_str)

    # Ստանում ենք աշխատող ֆունկցիա numpy-ի համար
    f = sp.lambdify(x, expr, "numpy")

    # Նմուշավորում ենք տվյալ միջակայքում
    xs = np.linspace(domain[0], domain[1], num_points)
    fs = f(xs)

    # Հաշվում ենք առաջին անկյունի առաջին վերլուծական փոփոխությունը՝ ըստ նիշի
    diffs = np.diff(fs)

    eps = 1e-8
    transitions = 0
    last_sign = None
    for d in diffs:
        # հաշվում ենք d-ի նշանը, եթե d-ի modulus-ը փոքր է eps-ի, ապա 0
        sign = np.sign(d) if abs(d) > eps else 0
        if sign == 0:
            continue
        if last_sign is None:
            last_sign = sign
        elif sign != last_sign:
            transitions += 1
            last_sign = sign

    # Այժմ, ըստ այս սահմանման, 0 փոփոխություն նշանակում է մոնոտոն,
    # իսկ unimodal համար պետք է լինի 1 փոխում, ինչը ցույց է տալիս
    # աճման և իջման հոսք, որտեղ ինտերյոր մոդա է:
    strictly_unimodal = (transitions == 1)

    if graph:
        plt.figure(figsize=(8, 4))
        plt.plot(xs, fs, label=f"f(x) = {func_str}")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.title("Ֆունկցիայի գրաֆիկ")
        plt.legend()
        plt.grid(True)
        plt.show()

    return strictly_unimodal

def find_extremum(func_str, a, b, eps=1e-5, delta=1e-6, find_min=True):
    """
        Պետք է գտնել ֆունկցիայի էքստրեմումը տրված միջակայքում՝ օգտագործելով բիսեկցիայի մեթոդը:
        Արդյունքը կարող է լինել ինչպես մինիմում, այնպես էլ մաքսիմում՝ կախված `find_min` պարամետրի արժեքից:

        :param func_str: Ֆունկցիան որպես string, օրինակ "x**2 - 4*x + 3".
        :param a: Տրված միջակայքի սկիզբ։
        :param b: Տրված միջակայքի վերջ։
        :param eps: Ճշգրտության շեմ, որի տակ կարող ենք ընդունել արդյունքը որպես ընդունելի։
        :param delta: Տարբերություն, որն օգտագործվում է երկու կետերի միջև տարածության համար։
        :param find_min: Եթե True, գտնում է մինիմումը, եթե False՝ մաքսիմումը։
        :return: Տրված միջակայքում էքստրեմումի դիրքը և արժեքը։
    """

    if check_unimodal(func_str, domain=(a, b)):
        return "Ֆունկցիան ունիմոդալ չէ"
    # Ստեղծում ենք ֆունկցիա `f` տրված սթրինգից
    def f(x):
        return eval(func_str, {"x": x, "math": math, "__builtins__": {}})

    while (b - a) > eps:
        x1 = (a + b) / 2 - delta
        x2 = (a + b) / 2 + delta
        f1 = f(x1)
        f2 = f(x2)

        if find_min:
            if f1 < f2:
                b = x2
            else:
                a = x1
        else:  # փնտրում ենք մաքսիմում
            if f1 > f2:
                b = x2
            else:
                a = x1

    x_opt = (a + b) / 2
    return x_opt, f(x_opt)

def golden_ratio_search_from_string(func_str, a, b, eps=1e-5, delta=1e-6, find_min=True):
    """
        Պետք է գտնել ֆունկցիայի էքստրեմումը տրված միջակայքում՝ օգտագործելով բիսեկցիայի մեթոդը:
        Արդյունքը կարող է լինել ինչպես մինիմում, այնպես էլ մաքսիմում՝ կախված `find_min` պարամետրի արժեքից:

        :param func_str: Ֆունկցիան որպես string, օրինակ "x**2 - 4*x + 3".
        :param a: Տրված միջակայքի սկիզբ։
        :param b: Տրված միջակայքի վերջ։
        :param eps: Ճշգրտության շեմ, որի տակ կարող ենք ընդունել արդյունքը որպես ընդունելի։
        :param delta: Տարբերություն, որն օգտագործվում է երկու կետերի միջև տարածության համար։
        :param find_min: Եթե True, գտնում է մինիմումը, եթե False՝ մաքսիմումը։
        :return: Տրված միջակայքում էքստրեմումի դիրքը և արժեքը։
    """

    if check_unimodal(func_str, domain=(a, b)):
        return "Ֆունկցիան ունիմոդալ չէ"
    # Ստեղծում ենք ֆունկցիա `f` տրված սթրինգից
    def f(x):
        return eval(func_str, {"x": x, "math": math, "__builtins__": {}})

    while (b - a) > eps:
        x1 = (a + b) / 2 - delta
        x2 = (a + b) / 2 + delta
        f1 = f(x1)
        f2 = f(x2)

        if find_min:
            if f1 < f2:
                b = x2
            else:
                a = x1
        else:  # փնտրում ենք մաքսիմում
            if f1 > f2:
                b = x2
            else:
                a = x1

    x_opt = (a + b) / 2
    return x_opt, f(x_opt)


def solve_mvn_game(A):
    """
    Լուծում է զրոյական գումարային խաղը՝ վերադառնալով խաղի արժեքը,
    խաղացող Ա-ի (հանրային) և խաղացող Բ-ի (ստոկային) խառնուրդային ռազմավարությունները։

    :param A: (m x n) numpy մատրիցա՝ խաղի վճարային մատրիցը, որտեղ m է խաղացող Ա-ի ռազմավարությունների քանակը,
              իսկ n-ը խաղացող Բ-ի ռազմավարությունների քանակը:
    :return: Tuple (game_value, row_strategy, col_strategy)
             - game_value: խաղի արժեքը
             - row_strategy: խաղացող Ա-ի խառնուրդային ռազմավարության vector-ը
             - col_strategy: խաղացող Բ-ի խառնուրդային ռազմավարության vector-ը
    """
    m, n = A.shape

    min_val = np.min(A)
    if min_val < 0:
        k = -min_val + 1
    else:
        k = 0

    A_shift = A + k

    A_lp_row = A_shift.T  # չափ: (n x m)
    b_lp_row = np.ones(n)  # չափ: (n,)
    signs_row = [">="] * n  # բոլոր սահմանափակումները ">="
    c_row = np.ones(m)  # օբյեկտիվ ֆունկցիա՝ sum(y_i)
    y, S, tableau_row = simplex_solver(A_lp_row, b_lp_row, signs_row, c_row, objective='min')

    row_strategy = y / S
    game_value_shifted = 1 / S
    game_value = game_value_shifted - k

    A_lp_col = A_shift  # չափ: (m x n)
    b_lp_col = np.ones(m)  # չափ: (m,)
    signs_col = ["<="] * m  # բոլոր սահմանափակումները "<="
    c_col = np.ones(n)  # օբյեկտիվ՝ sum(w_j)
    w, T, tableau_col = simplex_solver(A_lp_col, b_lp_col, signs_col, c_col, objective='max')

    col_strategy = w / T
    game_value_shifted_2 = 1 / T
    game_value_2 = game_value_shifted_2 - k

    return game_value, row_strategy, col_strategy