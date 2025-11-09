const inputs = document.querySelectorAll(".otp-input");
const form = document.getElementById("otp-form");
const fullOtpInput = document.getElementById("full-otp");

inputs.forEach((input, index) => {
    input.addEventListener("input", (e) => {
        // Move focus to the next input if not the last one
        if (e.target.value.length > 0 && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }

        // Combine all OTP values into the hidden input
        fullOtpInput.value = Array.from(inputs).map(input => input.value).join("");

        // Check if all inputs are filled
        const isComplete = Array.from(inputs).every(input => input.value.trim() !== "");
        if (isComplete) {
            form.submit(); // Automatically submit the form
        }
    });

    input.addEventListener("keydown", (e) => {
        // Handle backspace to move to the previous input
        if (e.key === "Backspace" && e.target.value === "" && index > 0) {
            inputs[index - 1].focus();
        }
    });
});
