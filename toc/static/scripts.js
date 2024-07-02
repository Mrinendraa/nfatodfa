function addTransition() {
    const div = document.createElement('div');
    div.className = 'transition';
    div.innerHTML = `
        <input type="text" name="state" placeholder="State">
        <input type="text" name="input" placeholder="Input">
        <input type="text" name="next_state" placeholder="Next State">
    `;
    document.getElementById('transitions').appendChild(div);
}

async function submitForm() {
    const form = document.getElementById('dfaForm');
    const formData = new FormData(form);
    const data = {
        alphabets: formData.get('alphabets').split(' '),
        initial_state: formData.get('initial_state'),
        final_state: formData.get('final_state'),
        transitions: []
    };

    document.querySelectorAll('.transition').forEach(transition => {
        const state = transition.querySelector('input[name="state"]').value;
        const input = transition.querySelector('input[name="input"]').value;
        const next_state = transition.querySelector('input[name="next_state"]').value;
        data.transitions.push(`${state} ${input} ${next_state}`);
    });

    data.transitions.push('end'); // Indicate the end of transitions

    const response = await fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    
    const result = await response.json();
    if (result.error) {
        alert(result.error);
    } else {
        document.getElementById('transition_table').textContent = result.transition_table;
        document.getElementById('dfa_graph').src = `/static/dfa_graph.png?${new Date().getTime()}`; // Force reload the image
    }
}
