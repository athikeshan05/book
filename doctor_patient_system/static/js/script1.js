document.addEventListener("DOMContentLoaded", function() {
    const bpRadioButtons = document.querySelectorAll('input[name="blood-pressure"]');
    const bpRateField = document.getElementById("pressure-rate");
    
    const diabetesRadioButtons = document.querySelectorAll('input[name="diabetes"]');
    const diabetesDetailsField = document.getElementById("diabetes-details");

    const allergyRadioButtons = document.querySelectorAll('input[name="allergies"]');
    const allergyDetailsField = document.getElementById("allergies-details");

    // Show/Hide Blood Pressure Rate field
    bpRadioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'yes') {
                bpRateField.classList.remove("hidden");
            } else {
                bpRateField.classList.add("hidden");
            }
        });
    });

    // Show/Hide Diabetes Glucose Level field
    diabetesRadioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'yes') {
                diabetesDetailsField.classList.remove("hidden");
            } else {
                diabetesDetailsField.classList.add("hidden");
            }
        });
    });

    // Show/Hide Allergies Details field
    allergyRadioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'yes') {
                allergyDetailsField.classList.remove("hidden");
            } else {
                allergyDetailsField.classList.add("hidden");
            }
        });
    });
});
