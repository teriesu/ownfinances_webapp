
function addObject() {
    const table = document.getElementById('dynamicTable');
    const tbody = table.getElementsByTagName('tbody')[0];
    let index = tbody.rows.length + 1;
    let newRow = tbody.insertRow();
    let cellName = newRow.insertCell(0);
    cellName.innerHTML = '<input type="text" name="object' + index + '" placeholder="Objeto ' + index + '">';

    let numProps = table.rows[0].cells.length;
    for (let i = 1; i < numProps; i++) {
        let newCell = newRow.insertCell(i);
        newCell.innerHTML = '<input type="text" name="prop' + i + '_obj' + index + '">';
    }
}


function addProperty() {
    const table = document.getElementById('dynamicTable');
    let index = table.rows[0].cells.length;
    let header = table.createTHead().rows[0];
    let newHeaderCell = header.insertCell(index);
    newHeaderCell.innerHTML = '<input type="text" name="property' + index + '" placeholder="Propiedad ' + index + '">';

    let bodyRows = table.getElementsByTagName('tbody')[0].rows;
    for (let i = 0; i < bodyRows.length; i++) {
        let newCell = bodyRows[i].insertCell(index);
        newCell.innerHTML = '<input type="text" name="prop' + index + '_obj' + (i + 1) + '">';
    }

    let footRows = table.getElementsByTagName('tfoot')[0].rows;
    let weightCell = footRows[0].insertCell(index);
    weightCell.innerHTML = '<input type="text" name="weight' + index + '" onchange="checkWeights()">';
    let minmaxCell = footRows[1].insertCell(index);
    minmaxCell.innerHTML = '<select name="minmax' + index + '"><option value="min">Min</option><option value="max">Max</option></select>';
}

function removeObject() {
    const table = document.getElementById('dynamicTable');
    let numRows = table.getElementsByTagName('tbody')[0].rows.length;
    if (numRows > 2) {
        table.getElementsByTagName('tbody')[0].deleteRow(-1);
    }
}

function removeProperty() {
    const table = document.getElementById('dynamicTable');
    let numCols = table.rows[0].cells.length;
    if (numCols > 3) {
        [...table.rows].forEach(row => row.deleteCell(-1));
    }
}

function checkWeights() {
    const weightInputs = document.querySelectorAll('tfoot tr:first-child input[type="text"]');
    let totalWeight = 0;
    weightInputs.forEach(input => {
        totalWeight += parseFloat(input.value) || 0;
    });

    const weightRow = document.querySelector('tfoot tr:first-child');
    if (totalWeight !== 100) {
        weightRow.style.backgroundColor = 'red';
    } else {
        weightRow.style.backgroundColor = '';
    }
}

