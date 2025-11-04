let myDoughnutChartInstance;

function updateChartData(data) {
const labels = data.map(item => item.Categoria);
const data_values = data.map(item => item.Monto);
const ctx = document.getElementById('myChart').getContext('2d');
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
            'rgba(89, 176, 247, .7)',  // Nuevo tono más claro
            'rgba(84, 235, 216, .7)',  // Nuevo tono más claro
            'rgba(89, 247, 156, .7)',  // Nuevo tono más claro
            'rgba(149, 247, 104, .7)', // Nuevo tono más claro
            'rgba(42, 33, 79, .7)',    // Nuevo tono más oscuro
        ],
        borderColor: [
            'rgba(69, 166, 247, 1)',
            'rgba(74, 225, 216, 1)',
            'rgba(69, 247, 136, 1)',
            'rgba(129, 247, 94, 1)',
            'rgba(22, 23, 59, 1)',
            'rgba(89, 176, 247, 1)',   // Nuevo tono más claro
            'rgba(84, 235, 216, 1)',   // Nuevo tono más claro
            'rgba(89, 247, 156, 1)',   // Nuevo tono más claro
            'rgba(149, 247, 104, 1)',  // Nuevo tono más claro
            'rgba(42, 33, 79, 1)',     // Nuevo tono más oscuro
        ],
        borderWidth: 1
    }]
};
const config = {
    type: 'doughnut',
    data: chartData,
    options: {
        responsive: true,
        plugins: {
            datalabels: {
                color: '#fff',
                anchor: 'center',
                align: 'center',
                formatter: (value, ctx) => {
                    let sum = 0;
                    let dataArr = ctx.chart.data.datasets[0].data;
                    dataArr.map(data => {
                        sum += data;
                    });
                    return 'Total: $' + sum;
                }
            }
        }
    }
};
if (window.myDoughnutChart instanceof Chart) {
    window.myDoughnutChart.destroy();
}
window.myDoughnutChart = new Chart(ctx, config);
// Calcular total
const totalMonto = data_values.reduce((sum, current) => sum + current, 0);
// Actualizar la tarjeta con el total
document.getElementById('totalMonto').textContent = formatCurrency(totalMonto);
}

function updateTableChart() {
const startDateElement = document.getElementById('start-date');
const endDateElement = document.getElementById('end-date');

const startDate = startDateElement ? startDateElement.value : null;
const endDate = endDateElement ? endDateElement.value : null;

let url2 = '/wastes/api/graph';

let params = new URLSearchParams();

if (startDate) {
    params.append('startDate', startDate);
}
if (endDate) {
    params.append('endDate', endDate);
}

fetch(`${url2}?${params.toString()}`)
    .then(response => response.json())
    .then(data => {
        // Actualiza tu gráfico con los nuevos datos
        updateChartData(data);
}).catch(error => console.error('Error:', error));

}

document.getElementById('start-date').addEventListener('change', updateTableChart);
document.getElementById('end-date').addEventListener('change', updateTableChart);

$(document).ready(function () {
updateTableChart();

var table = $('#maestroinsumos').DataTable({
    "scrollX": true,
    "ajax": {
        "url": "/wastes/api/table",
        "dataSrc": "",
        "data": function (d) {
            d.startDate = $('#start-date').val();
            d.endDate = $('#end-date').val();
        }
    },
    columnDefs:[{
        "targets": [0], // Este es el índice de la columna ID, asumiendo que es la primera columna
        "visible": false, // Esto ocultará la columna ID
        "searchable": false // Opcional, si también quieres hacerla no buscable
    },{
        render: $.fn.dataTable.render.number( ',', '.', 0, '$' ), targets: [3]
    }
    ],
    "columns": [
        { "data": "Id" },
        { "data": "Fecha" },
        { "data": "Categoria" },
        { "data": "Monto" },
        { "data": "Descripcion" }
    ],
    dom: 'Bfrtip', // Este parámetro es importante para activar los botones
    buttons: [
        {
            extend: 'excelHtml5',
            title: 'MovimientosInventario',
            text: 'Exportar a Excel',
            // Opciones adicionales pueden ir aquí
        }
    ]
});

// Escuchar cambios en el selector de fecha y recargar la tabla
$('#start-date, #ends-date').change(function () {
    table.ajax.reload();
});

document.getElementById("end-date").value = getCurrentDate();
// Establecer las fechas predeterminadas para los campos de fecha
document.getElementById("start-date").value = getFirstDayOfMonth();
});
