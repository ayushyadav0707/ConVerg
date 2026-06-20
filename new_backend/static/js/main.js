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

        const calcContainer = document.getElementById('calculation-container');
        const calcFormula = document.getElementById('calc-formula');
        const calcBody = document.getElementById('calc-body');
        const calcTotalSum = document.getElementById('calc-total-sum');

        if(res.error) {
            resultDiv.style.color = '#ef4444';
            resultDiv.innerText = 'Error';
            calcContainer.style.display = 'none';
        } else {
            resultDiv.style.color = '#113023';
            resultDiv.innerText = '₹ ' + res.price_lakhs.toFixed(2) + ' L';
            
            // Show calculation breakdown if available
            if (res.breakdown) {
                calcContainer.style.display = 'block';
                calcFormula.innerText = res.formula || 'y = X * θ';
                
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
                
                calcTotalSum.innerText = res.price_lakhs.toFixed(4);
            } else {
                calcContainer.style.display = 'none';
            }
        }
    } catch(e) {
        button.innerText = 'Calculate Value';
        button.style.opacity = '1';
        resultDiv.style.color = '#ef4444';
        resultDiv.innerText = 'Server Error';
        document.getElementById('calculation-container').style.display = 'none';
    }
}
