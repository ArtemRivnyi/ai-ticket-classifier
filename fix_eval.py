import re

# Read the file  
with open('templates/evaluation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problematic section and insert the forEach loop
# Pattern: tbody.innerHTML = ''; followed immediately by console.error
pattern = r"(tbody\.innerHTML = '';.*?\n\s+)(console\.error\('Evaluation error:', error\);)"

replacement = r"""\1data.results.forEach(row => {
                        const tr = document.createElement('tr');
                        const isCorrect = row.correct;

                        tr.innerHTML = `
                            <td class="px-6 py-4 text-sm text-slate-900 max-w-xs truncate" title="${row.ticket}">${row.ticket}</td>
                            <td class="px-6 py-4 text-sm text-slate-500">${row.expected_category}</td>
                            <td class="px-6 py-4 text-sm font-medium ${isCorrect ? 'text-green-600' : 'text-red-600'}">${row.predicted_category}</td>
                            <td class="px-6 py-4 text-sm text-slate-500">${(row.confidence * 100).toFixed(0)}%</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${isCorrect ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                                    ${isCorrect ? 'Pass' : 'Fail'}
                                </span>
                            </td>
                        `;
                        tbody.appendChild(tr);
                    });

                } catch (error) {
                    \2"""

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('templates/evaluation.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed evaluation.html")
