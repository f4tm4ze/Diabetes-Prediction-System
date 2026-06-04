<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Diabetes Risk Assessment | Clinical Prediction Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: system-ui, 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
        }

        /* BABY BLUE BACKGROUND - Hex: #89CFF0, RGB: 137,207,240 */
        body {
            background-color: #89CFF0;
            background: #89CFF0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 2rem 1.5rem;
        }

        /* Main white card container */
        .assessment-card {
            max-width: 1300px;
            width: 100%;
            margin: 0 auto;
            background: white;
            border-radius: 2rem;
            box-shadow: 0 25px 45px -12px rgba(0, 0, 0, 0.25), 0 8px 18px rgba(0, 0, 0, 0.05);
            overflow: hidden;
            transition: all 0.2s ease;
        }

        .card-inner {
            padding: 2rem 2rem 1.8rem 2rem;
        }

        /* Centered header */
        .hero-center {
            text-align: center;
            margin-bottom: 2rem;
        }

        .hero-center h1 {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #0F4C5F 0%, #1C6E7E 100%);
            background-clip: text;
            -webkit-background-clip: text;
            color: transparent;
            letter-spacing: -0.3px;
            margin-bottom: 0.65rem;
        }

        .hero-center p {
            font-size: 1.1rem;
            color: #2c3e4e;
            max-width: 700px;
            margin: 0 auto;
            line-height: 1.4;
            font-weight: 450;
        }

        hr.divider-light {
            margin: 1rem 0 1.8rem 0;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #cbdde9, transparent);
        }

        /* Two column form grid */
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.8rem 2rem;
            margin-bottom: 2.2rem;
        }

        .input-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .input-group label {
            font-weight: 600;
            color: #1a4c64;
            font-size: 0.9rem;
            letter-spacing: 0.3px;
        }

        .input-group input {
            padding: 0.85rem 1rem;
            border: 1.5px solid #e2edf2;
            border-radius: 18px;
            font-size: 1rem;
            background: #ffffff;
            transition: 0.2s;
            outline: none;
            font-weight: 500;
            color: #0b2b38;
        }

        .input-group input:focus {
            border-color: #5aa9c9;
            box-shadow: 0 0 0 3px rgba(90, 169, 201, 0.2);
        }

        .input-group input:hover {
            border-color: #89CFF0;
        }

        /* BUTTON SECTION - CENTERED BUTTONS */
        .button-row {
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin: 0.5rem 0 1rem 0;
            flex-wrap: wrap;
        }

        .btn {
            border: none;
            padding: 0.85rem 2.2rem;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 40px;
            cursor: pointer;
            transition: all 0.25s ease;
            background: #f0f4f8;
            color: #1a5d77;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }

        .btn-primary {
            background: #1f6e8c;
            color: white;
            box-shadow: 0 6px 14px rgba(31, 110, 140, 0.25);
        }

        .btn-primary:hover {
            background: #0e5a75;
            transform: translateY(-2px);
            box-shadow: 0 12px 20px -8px rgba(31, 110, 140, 0.4);
        }

        .btn-secondary {
            background: #eef2f6;
            border: 1px solid #cbdde6;
        }

        .btn-secondary:hover {
            background: #e2e9f0;
            transform: translateY(-1px);
        }

        /* Result area styling */
        .result-area {
            margin: 1.5rem 0 1.2rem 0;
            transition: 0.2s;
        }

        .risk-card {
            background: #fefefe;
            border-radius: 28px;
            padding: 1.5rem 2rem;
            border-left: 8px solid;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.03);
            margin-top: 0.5rem;
        }

        .high-risk {
            border-left-color: #c7362b;
            background: #fff6f5;
        }

        .low-risk {
            border-left-color: #2c8c5a;
            background: #f0faf5;
        }

        .risk-title {
            font-size: 1.7rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }

        .risk-score {
            font-size: 2rem;
            font-weight: 700;
            margin: 0.5rem 0;
        }

        .metrics-row {
            display: flex;
            gap: 2rem;
            margin: 1rem 0;
            flex-wrap: wrap;
        }

        .metric-box {
            background: white;
            padding: 0.6rem 1.2rem;
            border-radius: 50px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            border: 1px solid #e2edf2;
            font-weight: 500;
        }

        .advice-text {
            margin-top: 1.2rem;
            padding: 1rem;
            background: #f9fcfe;
            border-radius: 20px;
            line-height: 1.5;
            color: #2c3e50;
        }

        .advice-text strong {
            font-weight: 700;
        }

        /* Data summary expander */
        .data-summary {
            margin-top: 1rem;
        }

        .summary-toggle {
            background: #f8fafc;
            border-radius: 60px;
            padding: 0.6rem 1.2rem;
            display: inline-block;
            cursor: pointer;
            font-weight: 500;
            border: 1px solid #cde3ec;
            transition: 0.2s;
            user-select: none;
        }

        .summary-toggle:hover {
            background: #eef3f8;
        }

        .summary-table {
            margin-top: 1rem;
            overflow-x: auto;
            background: white;
            border-radius: 20px;
            padding: 0.5rem;
            border: 1px solid #e9edf2;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        th, td {
            text-align: left;
            padding: 10px 12px;
            border-bottom: 1px solid #e9edf2;
        }

        th {
            background: #eef3fc;
            font-weight: 600;
            color: #195a6e;
        }

        /* Disclaimer footer - WHITE TEXT, centered, baby blue background as requested */
        .disclaimer-footer {
            background-color: #89CFF0;
            margin-top: 2rem;
            padding: 1.5rem 1rem;
            border-radius: 28px;
            text-align: center;
            color: white;
            font-size: 0.85rem;
            line-height: 1.5;
        }

        .disclaimer-footer p {
            color: white;
            margin-bottom: 0.6rem;
        }

        .disclaimer-footer .copyright {
            font-size: 0.75rem;
            opacity: 0.92;
            margin-top: 8px;
        }

        /* Warning message */
        .warning-message {
            background: #fff3e0;
            border-radius: 28px;
            padding: 1rem;
            text-align: center;
            color: #b75f1a;
            font-weight: 500;
            margin-bottom: 1rem;
        }

        /* Responsive */
        @media (max-width: 780px) {
            .form-grid {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            .card-inner {
                padding: 1.5rem;
            }
            .button-row {
                gap: 1rem;
            }
            .btn {
                padding: 0.7rem 1.5rem;
            }
            .hero-center h1 {
                font-size: 1.8rem;
            }
            .risk-title {
                font-size: 1.4rem;
            }
            .risk-score {
                font-size: 1.6rem;
            }
        }
    </style>
</head>
<body>
<div class="assessment-card">
    <div class="card-inner">
        <!-- Centered header: Enter patient clinical measurements to generate a diabetes risk prediction -->
        <div class="hero-center">
            <h1>Diabetes Risk Assessment</h1>
            <p>Enter patient clinical measurements to generate a diabetes risk prediction.</p>
        </div>
        <hr class="divider-light">

        <!-- Input form with two columns -->
        <form id="diabetesForm">
            <div class="form-grid">
                <!-- Column 1 -->
                <div class="input-group">
                    <label>Number of Pregnancies</label>
                    <input type="number" id="pregnancies" value="0" step="1" min="0" max="20">
                </div>
                <div class="input-group">
                    <label>Glucose Level (mg/dL)</label>
                    <input type="number" id="glucose" value="0" step="1" min="0" max="300">
                </div>
                <div class="input-group">
                    <label>Blood Pressure (mm Hg)</label>
                    <input type="number" id="bp" value="0" step="1" min="0" max="200">
                </div>
                <div class="input-group">
                    <label>Skin Thickness (mm)</label>
                    <input type="number" id="skin" value="0" step="1" min="0" max="100">
                </div>
                <!-- Column 2 -->
                <div class="input-group">
                    <label>Insulin Level (μU/ml)</label>
                    <input type="number" id="insulin" value="0" step="1" min="0" max="900">
                </div>
                <div class="input-group">
                    <label>Body Mass Index (BMI)</label>
                    <input type="number" id="bmi" value="0" step="0.1" min="0" max="70">
                </div>
                <div class="input-group">
                    <label>Diabetes Pedigree Function</label>
                    <input type="number" id="dpf" value="0" step="0.01" min="0" max="3.0">
                </div>
                <div class="input-group">
                    <label>Age (years)</label>
                    <input type="number" id="age" value="0" step="1" min="0" max="120">
                </div>
            </div>

            <!-- Centered Buttons (Predict & Reset) -->
            <div class="button-row">
                <button type="button" id="predictBtn" class="btn btn-primary">Predict Risk</button>
                <button type="button" id="resetBtn" class="btn btn-secondary">Reset Form</button>
            </div>
        </form>

        <!-- Dynamic result container -->
        <div id="resultContainer" class="result-area"></div>

        <!-- Data summary wrapper (appears after prediction) -->
        <div id="summaryWrapper" style="margin-top: 0.8rem;"></div>

        <!-- Disclaimer Footer: White text, centered, on baby blue background -->
        <div class="disclaimer-footer">
            <p><strong>Disclaimer:</strong> This tool provides preliminary assessment only based on the data entered. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a healthcare professional for accurate diagnosis and treatment recommendations.</p>
            <p class="copyright">© 2024 Diabetes Prediction System | For educational purposes</p>
        </div>
    </div>
</div>

<script>
    // Diabetes risk prediction engine (clinically informed model)
    // Returns risk percentage (0-100) and binary class (0 = low risk, 1 = high risk)
    function computeDiabetesRisk(inputs) {
        const { pregnancies, glucose, bp, skin, insulin, bmi, dpf, age } = inputs;

        let riskScore = 0;

        // Glucose: primary predictor
        if (glucose >= 200) riskScore += 28;
        else if (glucose >= 140) riskScore += 22;
        else if (glucose >= 126) riskScore += 18;
        else if (glucose >= 100) riskScore += 10;
        else if (glucose > 0 && glucose < 70) riskScore += 5;
        
        // BMI (obesity key driver)
        if (bmi >= 40) riskScore += 25;
        else if (bmi >= 35) riskScore += 20;
        else if (bmi >= 30) riskScore += 15;
        else if (bmi >= 25) riskScore += 8;
        else if (bmi > 0 && bmi < 18.5) riskScore += 4;

        // Age progression
        if (age >= 60) riskScore += 18;
        else if (age >= 50) riskScore += 13;
        else if (age >= 40) riskScore += 8;
        else if (age >= 30) riskScore += 4;
        else if (age >= 21) riskScore += 1;

        // Diabetes Pedigree Function (genetic influence)
        if (dpf >= 1.2) riskScore += 15;
        else if (dpf >= 0.8) riskScore += 10;
        else if (dpf >= 0.5) riskScore += 6;
        else if (dpf >= 0.2) riskScore += 2;

        // Pregnancies (reproductive factor)
        if (pregnancies >= 8) riskScore += 9;
        else if (pregnancies >= 5) riskScore += 6;
        else if (pregnancies >= 2) riskScore += 3;
        else if (pregnancies === 1) riskScore += 1;

        // Blood pressure contribution
        if (bp >= 140) riskScore += 12;
        else if (bp >= 130) riskScore += 8;
        else if (bp >= 120) riskScore += 4;
        else if (bp >= 90 && bp < 120) riskScore += 1;

        // Insulin resistance marker
        if (insulin >= 300) riskScore += 12;
        else if (insulin >= 200) riskScore += 8;
        else if (insulin >= 140) riskScore += 5;
        else if (insulin > 0 && insulin < 30) riskScore += 1;

        // Skin thickness (triceps fold, correlates with insulin resistance)
        if (skin >= 40) riskScore += 6;
        else if (skin >= 30) riskScore += 4;
        else if (skin >= 20) riskScore += 2;

        // Synergistic interactions
        if (glucose >= 140 && bmi >= 30) riskScore += 8;
        if (age >= 45 && dpf >= 0.8) riskScore += 5;
        
        // Cap risk score at 100
        let finalRisk = Math.min(100, Math.max(0, riskScore));
        // Binary classification threshold at 42% (balanced for realistic output)
        const prediction = finalRisk >= 42 ? 1 : 0;
        return { riskPercent: finalRisk, prediction };
    }

    // Reset all form fields and clear results
    function resetFormFields() {
        document.getElementById('pregnancies').value = 0;
        document.getElementById('glucose').value = 0;
        document.getElementById('bp').value = 0;
        document.getElementById('skin').value = 0;
        document.getElementById('insulin').value = 0;
        document.getElementById('bmi').value = 0;
        document.getElementById('dpf').value = 0;
        document.getElementById('age').value = 0;
        
        const resultDiv = document.getElementById('resultContainer');
        const summaryWrap = document.getElementById('summaryWrapper');
        if (resultDiv) resultDiv.innerHTML = '';
        if (summaryWrap) summaryWrap.innerHTML = '';
    }

    // Get current input values from DOM
    function getInputValues() {
        return {
            pregnancies: parseFloat(document.getElementById('pregnancies').value) || 0,
            glucose: parseFloat(document.getElementById('glucose').value) || 0,
            bp: parseFloat(document.getElementById('bp').value) || 0,
            skin: parseFloat(document.getElementById('skin').value) || 0,
            insulin: parseFloat(document.getElementById('insulin').value) || 0,
            bmi: parseFloat(document.getElementById('bmi').value) || 0,
            dpf: parseFloat(document.getElementById('dpf').value) || 0,
            age: parseFloat(document.getElementById('age').value) || 0
        };
    }

    // Render prediction results and interactive summary table (no emojis)
    function renderPrediction(inputs) {
        const { pregnancies, glucose, bp, skin, insulin, bmi, dpf, age } = inputs;
        
        // Check if all fields are zero (no data entered)
        const allZero = (pregnancies === 0 && glucose === 0 && bp === 0 && skin === 0 && insulin === 0 && bmi === 0 && dpf === 0 && age === 0);
        
        const resultDiv = document.getElementById('resultContainer');
        const summaryWrap = document.getElementById('summaryWrapper');
        
        if (allZero) {
            resultDiv.innerHTML = `
                <div class="warning-message">
                    Please enter patient clinical measurements before generating an assessment.
                </div>
            `;
            summaryWrap.innerHTML = '';
            return;
        }
        
        // Compute risk metrics
        const { riskPercent, prediction } = computeDiabetesRisk(inputs);
        const isHighRisk = prediction === 1;
        // Confidence is either risk% (if high risk) or (100 - risk%) if low risk
        const confidence = isHighRisk ? riskPercent : (100 - riskPercent);
        const confidenceDisplay = confidence.toFixed(1);
        
        // Build risk result card
        let resultHtml = '';
        if (isHighRisk) {
            resultHtml = `
                <div class="risk-card high-risk">
                    <div class="risk-title" style="color:#c7362b;">HIGH DIABETES RISK DETECTED</div>
                    <div class="risk-score">Risk Score: ${riskPercent.toFixed(1)}%</div>
                    <div class="metrics-row">
                        <div class="metric-box">Confidence Level: ${confidenceDisplay}%</div>
                        <div class="metric-box">Risk Category: HIGH</div>
                    </div>
                    <div class="advice-text">
                        <strong>Immediate Actions Recommended:</strong><br>
                        - Consult with an endocrinologist immediately<br>
                        - Schedule HbA1c and fasting glucose tests<br>
                        - Begin lifestyle modifications (diet and exercise)<br>
                        - Regular monitoring of blood glucose levels<br>
                        - Discuss medication options with healthcare provider
                    </div>
                </div>
            `;
        } else {
            resultHtml = `
                <div class="risk-card low-risk">
                    <div class="risk-title" style="color:#2c8c5a;">LOW DIABETES RISK</div>
                    <div class="risk-score">Risk Score: ${riskPercent.toFixed(1)}%</div>
                    <div class="metrics-row">
                        <div class="metric-box">Confidence Level: ${confidenceDisplay}%</div>
                        <div class="metric-box">Risk Category: LOW</div>
                    </div>
                    <div class="advice-text">
                        <strong>Preventive Measures:</strong><br>
                        - Maintain healthy BMI (18.5-24.9)<br>
                        - Regular physical activity (150 mins/week)<br>
                        - Balanced diet with low sugar intake<br>
                        - Annual health checkups recommended<br>
                        - Periodic blood glucose monitoring
                    </div>
                </div>
            `;
        }
        resultDiv.innerHTML = resultHtml;
        
        // Build expandable patient data summary table (clean, no emojis)
        const summaryTableHtml = `
            <div class="data-summary">
                <div id="toggleSummaryBtn" class="summary-toggle">View Patient Data Summary ▼</div>
                <div id="summaryTableContent" style="display: none; margin-top: 12px;">
                    <div class="summary-table">
                        <table>
                            <thead>
                                <tr><th>Metric</th><th>Value</th></tr>
                            </thead>
                            <tbody>
                                <tr><td>Number of Pregnancies</td><td>${pregnancies}</td></tr>
                                <tr><td>Glucose Level (mg/dL)</td><td>${glucose}</td></tr>
                                <tr><td>Blood Pressure (mm Hg)</td><td>${bp}</td></tr>
                                <tr><td>Skin Thickness (mm)</td><td>${skin}</td></tr>
                                <tr><td>Insulin Level (μU/ml)</td><td>${insulin}</td></tr>
                                <tr><td>Body Mass Index (BMI)</td><td>${bmi}</td></tr>
                                <tr><td>Diabetes Pedigree Function</td><td>${dpf}</td></tr>
                                <tr><td>Age (years)</td><td>${age}</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        summaryWrap.innerHTML = summaryTableHtml;
        
        // Attach toggle event for expand/collapse
        const toggleBtn = document.getElementById('toggleSummaryBtn');
        const tableContent = document.getElementById('summaryTableContent');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', function() {
                const isVisible = tableContent.style.display === 'block';
                tableContent.style.display = isVisible ? 'none' : 'block';
                toggleBtn.innerHTML = isVisible ? 'View Patient Data Summary ▼' : 'Hide Patient Data Summary ▲';
            });
        }
    }
    
    // Predict action handler
    function onPredict() {
        const inputs = getInputValues();
        renderPrediction(inputs);
    }
    
    // Reset action handler
    function onReset() {
        resetFormFields();
    }
    
    // Wire up event listeners
    document.getElementById('predictBtn').addEventListener('click', onPredict);
    document.getElementById('resetBtn').addEventListener('click', onReset);
    
    // Enable "Enter" key submission on any input field
    const formInputs = document.querySelectorAll('#diabetesForm input');
    formInputs.forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                onPredict();
            }
        });
    });
    
    // Initial page state: no prediction, just empty result area
    // (no placeholder warning to keep clean)
</script>
</body>
</html>
