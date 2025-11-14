/**
 * script.js – CLEAN & CONSOLIDATED VERSION
 * Handles Toasts, Product Detail Page, Homepage Slideshow, and AI Predictions
 */

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message, type = 'info') {
    let box = document.getElementById('toast-container');
    if (!box) {
        box = document.createElement('div');
        box.id = 'toast-container';
        box.style.position = 'fixed';
        box.style.top = '20px';
        box.style.right = '20px';
        box.style.zIndex = '9999';
        document.body.appendChild(box);
    }

    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.textContent = message;
    box.appendChild(t);

    setTimeout(() => t.remove(), 3500);
}

// ==================== AI PREDICTION ====================
function fetchPrediction(card) {
    const name = card.dataset.name;
    const price = parseFloat(card.dataset.price);
    const category = card.dataset.category || "General";
    
    // 1. Get the individual value elements first
    const demandElem = card.querySelector('.prediction-output .ai-row:nth-child(1) .ai-value');
    const stockRiskElem = card.querySelector('.prediction-output .ai-row:nth-child(2) .ai-value');
    const recommendationElem = card.querySelector('.prediction-output .ai-row:nth-child(3) .ai-value');

    if (!name || !demandElem) return;

    // 2. Display loading state directly in the value spans
    demandElem.textContent = "Loading...";
    stockRiskElem.textContent = "Loading...";
    recommendationElem.textContent = "Loading...";


    fetch('/api/predict_sales', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            product_name: name,
            series: category, // Use 'category' to match AI model's structure
            price: price,
            rating: 4.0,          // placeholder
            reviews_count: 50,    // placeholder
            stock: 10             // placeholder
        })
    })
    .then(r => r.json())
    .then(data => {
        
        const prediction = data.predicted_sales !== undefined ? parseFloat(data.predicted_sales) : null;

        // Demand (Predicted Sales)
        if (demandElem) demandElem.textContent = prediction !== null ? prediction.toFixed(1) : 'Error';
        
        // Stock Risk Logic
        if (stockRiskElem) {
            const currentStock = 10; // Must match the value sent in the fetch body
            if (prediction !== null) {
                stockRiskElem.textContent = prediction > currentStock ? 'High' : 'Low';
            } else {
                stockRiskElem.textContent = 'N/A';
            }
        }
        
        // Recommendation Logic
        if (recommendationElem) {
            const restockThreshold = 15;
            const monitorThreshold = 10;
            if (prediction !== null) {
                if (prediction > restockThreshold) {
                    recommendationElem.textContent = 'RESTOCK NOW';
                } else if (prediction > monitorThreshold) {
                    recommendationElem.textContent = 'Monitor Stock';
                } else {
                    recommendationElem.textContent = 'Stock OK';
                }
            } else {
                recommendationElem.textContent = 'N/A';
            }
        }
    })
    .catch(err => {
        console.error('AI prediction failed for', name, err);
        if (demandElem) demandElem.textContent = "Error";
        if (stockRiskElem) stockRiskElem.textContent = "Error";
        if (recommendationElem) recommendationElem.textContent = "Error";
    });
}

// You must also include the logic to initialize the predictions for all cards:
document.addEventListener('DOMContentLoaded', () => {
    // Select all cards that need AI prediction
    const aiCards = document.querySelectorAll('.ai-card.product-card'); 
    aiCards.forEach(card => {
        fetchPrediction(card);
    });
});