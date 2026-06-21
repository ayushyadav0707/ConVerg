async function predict() {
    const locValue = document.getElementById('location').value.trim();
    const resultDiv = document.getElementById('result');
    const calcContainer = document.getElementById('calculation-container');
    const button = document.getElementById('predict-btn');

    if (!locValue) {
        resultDiv.style.color = '#ef4444';
        resultDiv.innerText = 'Please enter a location';
        if (calcContainer) calcContainer.style.display = 'none';
        return;
    }

    const validLocations = Array.from(document.querySelectorAll('.dropdown-item')).map(item => item.innerText);
    if (!validLocations.includes(locValue)) {
        resultDiv.style.color = '#ef4444';
        resultDiv.innerText = 'Location not found. Please select from the list.';
        if (calcContainer) calcContainer.style.display = 'none';
        return;
    }

    const data = {
        location: locValue,
        area_type: document.getElementById('area_type').value,
        sqft: document.getElementById('sqft').value,
        bhk: document.getElementById('bhk').value,
        bath: document.getElementById('bath').value,
        balcony: document.getElementById('balcony').value
    };
    
    button.innerText = 'Calculating...';
    button.style.opacity = '0.8';
    resultDiv.innerText = '';
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const res = await response.json();
        
        button.innerText = 'Calculate Value';
        button.style.opacity = '1';
        
        renderPrediction(res);
        
    } catch(e) {
        button.innerText = 'Calculate Value';
        button.style.opacity = '1';
        resultDiv.style.color = '#ef4444';
        resultDiv.innerText = 'Server Error';
    }
}

function renderPrediction(res) {
    const resultDiv = document.getElementById('result');
    const calcContainer = document.getElementById('calculation-container');
    const calcBody = document.getElementById('calc-body');
    const calcTotalSum = document.getElementById('calc-total-sum');

    if(res.error) {
        resultDiv.style.color = '#ef4444';
        resultDiv.innerText = 'Error';
        if (calcContainer) calcContainer.style.display = 'none';
    } else {
        resultDiv.style.color = '#113023';
        resultDiv.innerText = '₹ ' + res.price_lakhs.toFixed(2) + ' L';
        
        // Show calculation breakdown if available
        if (res.breakdown && calcContainer && calcBody) {
            calcContainer.style.display = 'block';
            
            calcBody.innerHTML = '';
            res.breakdown.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${item.feature}</td>
                    <td>${item.value.toFixed(4)}</td>
                    <td>${item.weight.toFixed(4)}</td>
                    <td>${item.contribution.toFixed(4)}</td>
                `;
                calcBody.appendChild(tr);
            });
            
            if (calcTotalSum) {
                calcTotalSum.innerText = res.price_lakhs.toFixed(4);
            }
        } else {
            if (calcContainer) calcContainer.style.display = 'none';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // If we are on the home page, clear all saved data so starting fresh
    if (window.location.pathname === '/' || window.location.pathname === '/index') {
        const keysToClear = ['converg_location', 'converg_area_type', 'converg_sqft', 'converg_bhk', 'converg_bath', 'converg_balcony', 'converg_last_prediction'];
        keysToClear.forEach(k => localStorage.removeItem(k));
        return; // Don't run the rest of the script on the home page
    }

    const fields = ['location', 'area_type', 'sqft', 'bhk', 'bath', 'balcony'];
    
    // Restore saved state
    fields.forEach(field => {
        const savedVal = localStorage.getItem('converg_' + field);
        const el = document.getElementById(field);
        
        if (el) {
            if (savedVal !== null) {
                el.value = savedVal;
            }
            
            // Save state when user types or changes value
            el.addEventListener('input', (e) => {
                localStorage.setItem('converg_' + field, e.target.value);
            });
            el.addEventListener('change', (e) => {
                localStorage.setItem('converg_' + field, e.target.value);
            });
        }
    });
});
