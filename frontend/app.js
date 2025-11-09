document.addEventListener('DOMContentLoaded', () => {

    const gridOptions = {
        columnDefs: [
            { field: "date", sortable: true, filter: true, flex: 1.5, resizable: true },
            { field: "description", sortable: true, filter: true, flex: 3, resizable: true },
            {
                field: "amount",
                sortable: true,
                filter: true,
                flex: 1,
                resizable: true,
                valueFormatter: params => params.value ? 'Rs' + params.value.toFixed(2) : '',
                cellStyle: params => (params.data.transaction_type === 'Debit' ? { color: '#e74c3c' } : { color: '#2ecc71' })
            },
            {
                field: "transaction_type",
                sortable: true,
                filter: true,
                flex: 1,
                resizable: true,
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
                resizable: true,
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
    const clearGridButton = document.getElementById('clearGridButton');

    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    const startCameraButton = document.getElementById('startCameraButton');
    const captureButton = document.getElementById('captureButton');
    const processCaptureButton = document.getElementById('processCaptureButton');
    const videoFeed = document.getElementById('videoFeed');
    const captureCanvas = document.getElementById('captureCanvas');
    const capturePreview = document.getElementById('capturePreview');
    const capturePreviewContainer = document.getElementById('capturePreviewContainer');
    
    let currentVideoStream = null;
    let capturedBlob = null;

    uploadButton.addEventListener('click', () => {
        const file = pdfUpload.files[0];
        if (!file) {
            setStatus('Please select a PDF file first.', 'error');
            return;
        }
        processFile(file);
    });

    exportCsvButton.addEventListener('click', () => {
        gridApi.exportDataAsCsv({
            fileName: `transactions-${new Date().toISOString().split('T')[0]}.csv`
        });
    });

    clearGridButton.addEventListener('click', () => {
        gridApi.setGridOption('rowData', []);
        calculateSummary([]);
        resultsCard.style.display = 'none';
        setStatus('Grid cleared.', 'info');
    });

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            button.classList.add('active');
            document.getElementById(button.dataset.tab).classList.add('active');
            
            if (button.dataset.tab !== 'scan' && currentVideoStream) {
                stopCamera();
            }
        });
    });

    startCameraButton.addEventListener('click', startCamera);
    captureButton.addEventListener('click', captureImage);
    processCaptureButton.addEventListener('click', () => {
        if (capturedBlob) {
            const file = new File([capturedBlob], "capture.jpg", { type: "image/jpeg" });
            processFile(file);
            capturePreviewContainer.style.display = 'none';
            captureButton.disabled = false;
        }
    });

   async function processFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        setStatus(`Processing ${file.name}...`, 'info');
        loader.style.display = 'block';
        uploadButton.disabled = true;
        processCaptureButton.disabled = true;

        try {
            // --- THIS IS THE CORRECTED LINE ---
            const response = await fetch("https://virtuous-celebration-production.up.railway.app/upload", {
                method: "POST",
                body: formData
            });
            // --- END OF CORRECTION ---

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'An unknown error occurred.');
            }

            setStatus(`Successfully extracted ${data.transactions.length} transactions from ${file.name}.`, 'success');
            resultsCard.style.display = 'block';

            const newTransactions = data.transactions;
            const existingTransactions = gridApi.getGridOption('rowData') || [];
            const allTransactions = existingTransactions.concat(newTransactions);
            
            gridApi.setGridOption('rowData', allTransactions);
            calculateSummary(allTransactions);

        } catch (error) {
            console.error('Upload failed:', error);
            setStatus(`Error: ${error.message}`, 'error');
        } finally {
            loader.style.display = 'none';
            uploadButton.disabled = false;
            processCaptureButton.disabled = false;
            pdfUpload.value = null;
            capturedBlob = null;
        }
    }
    
    function setStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = type;
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
    }

    async function startCamera() {
        if (currentVideoStream) {
            stopCamera();
            return;
        }
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'environment' }
            });
            currentVideoStream = stream;
            videoFeed.srcObject = stream;
            videoFeed.style.display = 'block';
            startCameraButton.textContent = 'Stop Camera';
            captureButton.disabled = false;
            capturePreviewContainer.style.display = 'none';
        } catch (err) {
            console.error("Error accessing camera:", err);
            setStatus('Error: Could not access camera. Check permissions.', 'error');
            if (err.name === "NotAllowedError") {
                 setStatus('Error: Camera permission denied. Please allow camera access in your browser settings.', 'error');
            }
        }
    }

    function stopCamera() {
        if (currentVideoStream) {
            currentVideoStream.getTracks().forEach(track => track.stop());
            currentVideoStream = null;
            videoFeed.srcObject = null;
            videoFeed.style.display = 'none';
            startCameraButton.textContent = 'Start Camera';
            captureButton.disabled = true;
            capturePreviewContainer.style.display = 'none';
        }
    }

    function captureImage() {
        if (!currentVideoStream) return;

        captureCanvas.width = videoFeed.videoWidth;
        captureCanvas.height = videoFeed.videoHeight;
        
        const context = captureCanvas.getContext('2d');
        context.drawImage(videoFeed, 0, 0, captureCanvas.width, captureCanvas.height);

        captureCanvas.toBlob((blob) => {
            capturedBlob = blob;
            capturePreview.src = URL.createObjectURL(blob);
            capturePreviewContainer.style.display = 'flex';
            processCaptureButton.disabled = false;
            captureButton.disabled = true;
        }, 'image/jpeg', 0.9);
    }
});