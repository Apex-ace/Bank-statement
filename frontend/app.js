document.addEventListener('DOMContentLoaded', () => {
    

    const gridOptions = {

        columnDefs: [
            { field: "date", sortable: true, filter: true, flex: 1 },
            { field: "description", sortable: true, filter: true, flex: 3 },
            { 
                field: "amount", 
                sortable: true, 
                filter: true, 
                flex: 1,
                valueFormatter: params => 'Rs' + params.value.toFixed(2), 
                cellStyle: params => (params.data.transaction_type === 'Debit' ? { color: '#e74c3c' } : { color: '#2ecc71' })
            },
            { 
                field: "transaction_type", 
                sortable: true, 
                filter: true, 
                flex: 1,
                cellRenderer: params => {
                    const color = params.value === 'Debit' ? '#e74c3c' : '#2ecc71';
                    return `<span style="color: ${color}; font-weight: bold;">${params.value}</span>`;
                }
            },
            { 
                field: "balance", 
                sortable: true, 
                filter: true, 
                flex: 1,
                valueFormatter: params => params.value ? 'Rs' + params.value.toFixed(2) : 'N/A'
            }
        ],
        defaultColDef: {
            resizable: true,
            filter: true,
        },
        rowData: [] 
    };


    const gridDiv = document.querySelector('#transactionGrid');
    const gridApi = agGrid.createGrid(gridDiv, gridOptions);


    const uploadButton = document.getElementById('uploadButton');
    const pdfUpload = document.getElementById('pdfUpload');
    const statusMessage = document.getElementById('statusMessage');
    const loader = document.getElementById('loader');
    const resultsCard = document.querySelector('.results-card');
    const exportCsvButton = document.getElementById('exportCsvButton');
    const totalCreditEl = document.getElementById('totalCredit');
    const totalDebitEl = document.getElementById('totalDebit');


    uploadButton.addEventListener('click', handleUpload);
    exportCsvButton.addEventListener('click', () => {
        gridApi.exportDataAsCsv();
    });

    async function handleUpload() {
        const file = pdfUpload.files[0];
        if (!file) {
            setStatus('Please select a PDF file first.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        setStatus('Processing file...', 'info');
        loader.style.display = 'block';
        uploadButton.disabled = true;
        resultsCard.style.display = 'none';

        try {
            const response = await fetch('http://127.0.0.1:8000/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'An unknown error occurred.');
            }

            setStatus(`Successfully extracted ${data.transactions.length} transactions.`, 'success');
            resultsCard.style.display = 'block';
            
            gridApi.setGridOption('rowData', data.transactions);
            
            calculateSummary(data.transactions);

        } catch (error) {
            console.error('Upload failed:', error);
            setStatus(`Error: ${error.message}`, 'error');
        } finally {
            loader.style.display = 'none';
            uploadButton.disabled = false;
        }
    }

    function setStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = type; // 'error', 'success', 'info'
    }

    function calculateSummary(transactions) {
        let totalCredit = 0;
        let totalDebit = 0;

        transactions.forEach(tx => {
            if (tx.transaction_type === 'Credit') {
                totalCredit += tx.amount;
            } else if (tx.transaction_type === 'Debit') {
                totalDebit += tx.amount;
            }
        });

        totalCreditEl.textContent = `Rs${totalCredit.toFixed(2)}`;
        totalDebitEl.textContent = `Rs${totalDebit.toFixed(2)}`;
        totalDebitEl.style.color = '#e74c3c';
        totalCreditEl.style.color = '#2ecc71';
    }
});