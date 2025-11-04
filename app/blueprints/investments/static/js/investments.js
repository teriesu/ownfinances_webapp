function openEditModal(cells) {
    // Ejemplo: llenar el campo de monto
    document.getElementById('montoInput').value = cells[3].data; // Asumiendo que el monto está en la cuarta celda

    // Abrir el modal
    $('#editModal').modal('show');
}
document.getElementById('editForm').addEventListener('submit', function(event) {
    event.preventDefault();
    // Aquí puedes añadir la lógica para actualizar la información
    // Por ejemplo, enviar una solicitud AJAX con los datos actualizados
    $('#editModal').modal('hide');
});
        
function formatCurrency(value) {
    return "$" + value.toFixed(0).replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,').replace(/\./g, 'X').replace(/,/g, '.').replace(/X/g, ',');
}
let myDoughnutChartInstance; // Variable global para mantener la referencia al gráfico
function updateChartData(data) {
    const labels = data.map(item => item.Categoria);
    const data_values = data.map(item => item.Monto);
    const chartData = {
        labels: labels,
        datasets: [{
            data: data_values,
            backgroundColor: [
                'rgba(69, 166, 247, .7)',
                'rgba(74, 225, 216, .7)',
                'rgba(69, 247, 136, .7)',
                'rgba(129, 247, 94, .7)',
                'rgba(22, 23, 59, .7)',
            ],
            borderColor: [
                'rgba(69, 166, 247, 1)',
                'rgba(74, 225, 216, 1)',
                'rgba(69, 247, 136, 1)',
                'rgba(129, 247, 94, 1)',
                'rgba(22, 23, 59, 1)',
            ],
            borderWidth: 1
        }]
    };
    const config = {
        type: 'doughnut',
        data: chartData
    };
    if (!myDoughnutChartInstance) {
        // Si no existe una instancia del gráfico, crea una nueva
        myDoughnutChartInstance = new Chart(document.getElementById('myChart'), config);
    } else {
        myDoughnutChartInstance.data = chartData;
        myDoughnutChartInstance.options = config.options;
        myDoughnutChartInstance.update();
    }
    // Calcular total
    const totalMonto = data_values.reduce((sum, current) => sum + current, 0);
    // Actualizar la tarjeta con el total
    document.getElementById('totalMonto').textContent = formatCurrency(totalMonto);
}

let gridInstance = null;
let columns = [
    {id:'Id', name:'Id', sort: true, hidden: true},
    {id:'cerrada', name:'cerrada', sort: true, hidden: true},
    {id:'Fecha', name:'Fecha', sort: true},
    {id:'Categoria', name:'Categoría', sort: true},
    {id:'Monto', name:'Monto', sort: true},
    {id:'Descripcion', name:'Descripción', sort: false},
    {
        id: 'Retirar', 
        name: 'Retirar inversión', 
        sort: false, 
        formatter: (cell, row) => {
            // Verifica si la inversión está cerrada
            const isClosed = row.cells[1].data; // Asume que 'cerrada' es la segunda celda (índice 1)
            if (!isClosed) {
                return gridjs.h('button', {
                    className: 'btn btn-personal2 btn-sm',
                    onClick: () => openEditModal(row.cells)
                }, 'Retirar inversión');
            } else {
                return '';
            }
        }
    }
];
function updateTable(data) {
    const tableContainer = document.getElementById("my-table");
    // Vaciar el contenedor antes de renderizar la nueva tabla
    tableContainer.innerHTML = '';
    // Convertir los datos para la tabla
    const tableData = data.map(item => [
        item.Id,
        item.Cerrada,
        item.Fecha, 
        item.Categoria, 
        formatCurrency(item.Monto), 
        item.Descripcion
    ]); 
    // Configuración de la tabla
    const gridConfig = {
        data: tableData,
        search: false,
        sort: true,
        columns: columns,
        className: {
            table: 'table table-striped', // clases de Bootstrap para la tabla
            th: 'thead-dark', // clase de Bootstrap para los encabezados de la tabla
            td: 'align-middle', // clase de Bootstrap para las celdas de la tabla
            container: 'container mt-5', // clase de Bootstrap para el contenedor de la tabla
            },
    };
    if (window.gridInstance) {
        // Si la instancia ya existe, simplemente actualiza los datos
        window.gridInstance.updateConfig(gridConfig).forceRender();
    } else {
        // Si la instancia no existe, crear una nueva y asignarla a window.gridInstance
        window.gridInstance = new gridjs.Grid(gridConfig).render(tableContainer);
    }
}

function updateTableChart() {
    const startDateElement = document.getElementById('start-date');
    const endDateElement = document.getElementById('end-date');

    const startDate = startDateElement ? startDateElement.value : null;
    const endDate = endDateElement ? endDateElement.value : null;

    let url = '/investments/api/table';
    let params = new URLSearchParams();

    // if (selectedAreas && selectedAreas.length > 0) {
    //    params.append('areas', selectedAreas.join(',')); // Asumiendo que el backend acepta una lista de áreas separadas por comas
    // }
    if (startDate) {
        params.append('startDate', startDate);
    }
    if (endDate) {
        params.append('endDate', endDate);
    }    

    fetch(`${url}?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // Actualiza tu gráfico con los nuevos datos
            updateChartData(data);
            updateTable(data);
        })
        .catch(error => console.error('Error:', error));
}

updateTableChart();

document.getElementById('start-date').addEventListener('change', updateTableChart);
document.getElementById('end-date').addEventListener('change', updateTableChart);