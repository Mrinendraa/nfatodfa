from flask import Flask, request, render_template, jsonify
import graphviz

app = Flask(__name__)

def printtransitiontable(sets, alphabets):
    transition_table = ""
    sts = list(sets.keys())
    if not sts:
        return "No states found."

    max_len = max(len(i) for i in sts)
    max_len = max(max_len, 5)
    transition_table += f" {'_' * (max_len + 2)}{'_' * (max_len + 3) * len(alphabets)}\n"
    transition_table += f"| State{' ' * (max_len - 5)} | " + " | ".join(inp.ljust(max_len) for inp in alphabets) + " |\n"
    transition_table += f"|{'-' * (max_len + 2)}|" + "|".join(['-' * (max_len + 2)] * len(alphabets)) + "|\n"
    for i in sts:
        next_states = sets[i]
        transition_table += f"| {i.ljust(max_len)} | " + " | ".join(",".join(next_states.get(inp, ["trap"])).ljust(max_len) for inp in alphabets) + " |\n"
    transition_table += f" {'‾' * (max_len + 2)}{'‾' * (max_len + 3) * len(alphabets)}\n"
    return transition_table

def drawdfa(dfa, fstate):
    dot = graphviz.Digraph()
    final_states = set()
    for state, transitions in dfa.items():
        if fstate in state:
            final_states.add(state)
        for next_states in transitions.values():
            for next_state in next_states:
                if fstate in next_state:
                    final_states.add(next_state)

    for state in dfa:
        if state in final_states:
            dot.node(state, state, shape='doublecircle')
        else:
            dot.node(state, state)

    for state, transitions in dfa.items():
        for symbol, next_states in transitions.items():
            next_state_label = ",".join(next_states)
            dot.edge(state, next_state_label, label=symbol)

    dot.render('static/dfa_graph', format='png', cleanup=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        alphabets = data['alphabets']
        transitions = data['transitions']
        initial_state = data['initial_state']
        final_state = data['final_state']

        # Process input to form NFA
        nfa = {}
        states = set()
        for transition in transitions:
            if transition == 'end':
                break
            state, inp, next_state = transition.split()
            if state not in nfa:
                nfa[state] = {}
            if inp not in nfa[state]:
                nfa[state][inp] = []
            nfa[state][inp].append(next_state)
            states.update([state, next_state])

        # Adding missing transitions for states
        for state in states:
            if state not in nfa:
                nfa[state] = {}
            for inp in alphabets:
                if inp not in nfa[state]:
                    nfa[state][inp] = ["trap"]

        # NFA to DFA conversion (simplified)
        dfa = {}
        unprocessed_states = [initial_state]
        processed_states = set()

        while unprocessed_states:
            current_state = unprocessed_states.pop()
            if current_state in processed_states:
                continue

            processed_states.add(current_state)
            dfa[current_state] = {}

            for inp in alphabets:
                next_states = set()
                for state in current_state.split(','):
                    next_states.update(nfa.get(state, {}).get(inp, ["trap"]))
                
                next_states.discard("trap")
                next_state = ','.join(sorted(next_states)) if next_states else "trap"
                dfa[current_state][inp] = next_state.split(',')

                if next_state != "trap" and next_state not in processed_states:
                    unprocessed_states.append(next_state)

        transition_table = printtransitiontable(dfa, alphabets)
        drawdfa(dfa, final_state)

        return jsonify({'transition_table': transition_table})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
