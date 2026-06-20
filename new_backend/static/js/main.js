async function predict() {
    const data = {
        location: document.getElementById('location').value,
        sqft: document.getElementById('sqft').value,
        bhk: document.getElementById('bhk').value,
        bath: document.getElementById('bath').value,
        balcony: document.getElementById('balcony').value
    };
    
    const resultDiv = document.getElementById('result');
    const button = document.getElementById('predict-btn');
    
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

        if(res.error) {
            resultDiv.style.color = '#ef4444';
            resultDiv.innerText = 'Error';
        } else {
            resultDiv.style.color = '#113023';
            resultDiv.innerText = '₹ ' + res.price_lakhs.toFixed(2) + ' L';
        }
    } catch(e) {
        button.innerText = 'Calculate Value';
        button.style.opacity = '1';
        resultDiv.style.color = '#ef4444';
        resultDiv.innerText = 'Server Error';
    }
}
