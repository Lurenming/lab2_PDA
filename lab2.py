class CFG:
    def __init__(self, productions):
        """
        初始化CFG对象，接收一个包含产生式的字典。
        核心思路：存储文法产生式，并初始化相关数据结构。
        """
        self.productions = productions
        self.non_terminals = set(productions.keys())
        self.epsilon_non_terminals = set()
        self.unit_productions = []
        self.useful_symbols = set()

    def remove_epsilon(self):
        """
        消除文法中的ε产生式。
        核心思路：找到所有ε产生式，删除它们并生成新的替代产生式。
        """
        self.find_epsilon_productions()
        self.remove_epsilon_productions()

    def find_epsilon_productions(self):
        """
        查找文法中含有ε产生式的非终结符号。
        核心思路：遍历所有产生式，记录包含ε的非终结符号。
        """
        for non_terminal, rules in self.productions.items():
            for rule in rules:
                if rule == 'ε':
                    self.epsilon_non_terminals.add(non_terminal)

    def remove_epsilon_productions(self):
        """
        从文法中删除ε产生式，并生成新的产生式。
        核心思路：对每个包含ε的产生式，生成不包含ε的替代产生式。
        """
        new_productions = {}
        for non_terminal, rules in self.productions.items():
            new_productions[non_terminal] = [rule for rule in rules if rule != 'ε']
            for rule in rules:
                if any(symbol in self.epsilon_non_terminals for symbol in rule):
                    new_rules = self.generate_new_rules(rule)
                    new_productions[non_terminal].extend(new_rules)
        self.productions = new_productions

    def generate_new_rules(self, rule):
        """
        为包含ε的产生式生成新的替代产生式。
        核心思路：对于每个包含ε的符号，生成移除该符号的新产生式。
        """
        new_rules = []
        for i in range(len(rule)):
            if rule[i] in self.epsilon_non_terminals:
                new_rules.append(rule[:i] + rule[i+1:])
        return new_rules

    def remove_unit_productions(self):
        """
        消除文法中的单产生式。
        核心思路：找到所有单产生式，替换它们为多产生式。
        """
        self.find_unit_productions()
        self.substitute_unit_productions()

    def find_unit_productions(self):
        """
        查找文法中的单产生式。
        核心思路：遍历所有产生式，记录单产生式。
        """
        for non_terminal, rules in self.productions.items():
            for rule in rules:
                if rule in self.non_terminals:
                    self.unit_productions.append((non_terminal, rule))

    def substitute_unit_productions(self):
        """
        将单产生式替换为多产生式。
        核心思路：用单产生式右侧的产生式替代单产生式。
        """
        for non_terminal, unit in self.unit_productions:
            self.productions[non_terminal].remove(unit)
            self.productions[non_terminal].extend(self.productions[unit])

    def remove_useless_symbols(self):
        """
        消除文法中的无用符号。
        核心思路：找到所有有用符号，并移除无用符号。
        """
        self.find_useful_symbols()
        self.productions = {nt: rules for nt, rules in self.productions.items() if nt in self.useful_symbols}

    def find_useful_symbols(self):
        """
        查找文法中有用的符号。
        核心思路：遍历产生式，记录所有可以被使用的符号。
        """
        for non_terminal, rules in self.productions.items():
            for rule in rules:
                if all(symbol.islower() or symbol in self.non_terminals for symbol in rule):
                    self.useful_symbols.add(non_terminal)

    def transform(self):
        """
        调用各个方法依次消除ε产生式、单产生式及无用符号，返回转换后的文法。
        核心思路：按顺序执行消除ε产生式、单产生式和无用符号的操作。
        """
        self.remove_epsilon()
        self.remove_unit_productions()
        self.remove_useless_symbols()
        return self.productions

class PDAtoCFG:
    def __init__(self, states, input_alphabet, stack_alphabet, transitions, start_state, start_symbol, final_state):
        """
        初始化PDAtoCFG对象，接收PDA的参数。
        核心思路：存储PDA的各项参数，初始化CFG产生式集合。
        """
        self.states = states
        self.input_alphabet = input_alphabet
        self.stack_alphabet = stack_alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.start_symbol = start_symbol
        self.final_state = final_state
        self.cfg_productions = {}

    def convert(self):
        """
        将PDA转换为等价的CFG。
        核心思路：遍历PDA的转移规则，生成对应的CFG产生式。
        """
        for (current_state, input_symbol, stack_symbol), next_states in self.transitions.items():
            for next_state, new_stack in next_states:
                for i in range(len(new_stack) + 1):
                    lhs = f"{current_state}{stack_symbol}{next_state}"
                    rhs = input_symbol if input_symbol != 'ε' else ''
                    if i < len(new_stack):
                        rhs += f"{current_state}{new_stack[:i]}{next_state}"
                    self.add_production(lhs, rhs)
        return self.cfg_productions

    def add_production(self, lhs, rhs):
        """
        向CFG的产生式集合中添加新产生式。
        核心思路：将新产生式添加到CFG产生式集合中。
        """
        if lhs not in self.cfg_productions:
            self.cfg_productions[lhs] = []
        self.cfg_productions[lhs].append(rhs)

def input_cfg():
    """
    允许用户输入上下文无关文法的产生式。
    核心思路：从用户处获取产生式的左部和右部，并存储在字典中。
    """
    productions = {}
    n = int(input("Enter number of productions: "))
    for _ in range(n):
        lhs = input("Enter left hand side ps: S(non-terminal): ")
        rhs = input("Enter right hand side ps: abB|ε(productions, separated by '|'): ").split('|')
        productions[lhs] = rhs
    return productions

def input_pda():
    """
    允许用户输入下推自动机的参数。
    核心思路：从用户处获取状态集、输入字母表、栈字母表、转移函数、初始状态、初始栈符号和接受状态，并存储这些参数。
    """
    states = set(input("Enter states ps: q0 q1(separated by space): ").split())
    input_alphabet = set(input("Enter input alphabet ps: a b(separated by space): ").split())
    stack_alphabet = set(input("Enter stack alphabet ps: B z0(separated by space): ").split())
    transitions = {}
    num_transitions = int(input("Enter number of transitions: "))
    for _ in range(num_transitions):
        transition = input("Enter transition ps: q0,a,B,q1,ε (format: current_state,input_symbol,stack_symbol,next_state,new_stack_symbol_sequence): ")
        current_state, input_symbol, stack_symbol, next_state, new_stack = transition.split(',')
        key = (current_state, input_symbol, stack_symbol)
        if key not in transitions:
            transitions[key] = set()
        transitions[key].add((next_state, new_stack))
    start_state = input("Enter start state ps:q0: ")
    start_symbol = input("Enter start stack symbol ps:z0: ")
    final_state = input("Enter final state ps:q1: ")
    return states, input_alphabet, stack_alphabet, transitions, start_state, start_symbol, final_state

def main():
    """
    主函数，提供操作菜单，允许用户选择要执行的操作，并根据输入执行相应的转换和简化操作。
    核心思路：提供一个菜单供用户选择执行的操作，根据选择调用相应的函数进行处理并输出结果。
    """
    print("Choose the operation:")
    print("1. Transform CFG by removing ε-productions, unit productions, and useless symbols.")
    print("2. Convert PDA to equivalent CFG.")
    choice = int(input("Enter your choice: "))
    
    if choice == 1:
        print("Enter your CFG productions. For example, for production S -> a | bA | B | ccD, input 'S' as LHS and 'a|bA|B|ccD' as RHS.")
        productions = input_cfg()
        cfg = CFG(productions)
        transformed_productions = cfg.transform()
        print("Transformed CFG productions:")
        for nt, rules in transformed_productions.items():
            print(f"{nt} -> {' | '.join(rules)}")
    elif choice == 2:
        print("Enter your PDA components.")
        print("For states, input like 'q0 q1 q2'. For transitions, input each transition as a tuple (current_state,input_symbol,stack_symbol,next_state,new_stack).")
        states, input_alphabet, stack_alphabet, transitions, start_state, start_symbol, final_state = input_pda()
        pda_to_cfg = PDAtoCFG(states, input_alphabet, stack_alphabet, transitions, start_state, start_symbol, final_state)
        cfg_productions = pda_to_cfg.convert()
        print("Equivalent CFG productions:")
        for nt, rules in cfg_productions.items():
            print(f"{nt} -> {' | '.join(rules)}")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()