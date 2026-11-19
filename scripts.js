// =========================
// CALCULATOR DISPLAY
// =========================

let display;


// Page load hone ke baad code chalega
document.addEventListener("DOMContentLoaded", function () {

    display = document.getElementById("display");

    // Theme setup
    setupTheme();

});


// =========================
// PRESS BUTTON
// =========================

function press(value) {

    if (!display) return;

    if (
        display.value === "0" ||
        display.value === "Error"
    ) {
        display.value = value;
    }

    else {
        display.value += value;
    }
}


// =========================
// CLEAR
// =========================

function clearDisplay() {

    if (!display) return;

    display.value = "0";
}


// =========================
// BACKSPACE
// =========================

function backspace() {

    if (!display) return;

    if (
        display.value.length > 1 &&
        display.value !== "Error"
    ) {

        display.value =
            display.value.slice(0, -1);

    }

    else {

        display.value = "0";

    }
}


// =========================
// CALCULATE
// =========================

function calculate() {

    if (!display) return;

    try {

        let expression = display.value;

        let calculationExpression = expression
            .replace(/÷/g, "/")
            .replace(/×/g, "*")
            .replace(/%/g, "/100");


        let result = eval(calculationExpression);


        if (
            result === undefined ||
            !isFinite(result)
        ) {

            display.value = "Error";
            return;

        }


        result =
            Number.isInteger(result)
                ? result
                : Number(result.toFixed(10));


        display.value = result;


        saveCalculation(
            expression,
            result
        );

    }

    catch (error) {

        console.log(error);

        display.value = "Error";

    }
}


// =========================
// SCIENTIFIC CALCULATOR
// =========================

function scientific(type) {

    if (!display) return;

    try {

        let value =
            parseFloat(display.value);


        if (isNaN(value)) {

            display.value = "Error";
            return;

        }


        let result;


        // Square root
        if (type === "sqrt") {

            result = Math.sqrt(value);

        }


        // Square
        else if (type === "square") {

            result = Math.pow(value, 2);

        }


        // Cube
        else if (type === "cube") {

            result = Math.pow(value, 3);

        }


        // Sin
        else if (type === "sin") {

            result = Math.sin(
                value * Math.PI / 180
            );

        }


        // Cos
        else if (type === "cos") {

            result = Math.cos(
                value * Math.PI / 180
            );

        }


        // Tan
        else if (type === "tan") {

            result = Math.tan(
                value * Math.PI / 180
            );

        }


        // Log
        else if (type === "log") {

            result = Math.log10(value);

        }


        if (
            result === undefined ||
            !isFinite(result)
        ) {

            display.value = "Error";
            return;

        }


        result =
            Number(result.toFixed(10));


        let expression =
            type + "(" + value + ")";


        display.value = result;


        saveCalculation(
            expression,
            result
        );

    }

    catch (error) {

        console.log(error);

        display.value = "Error";

    }
}


// =========================
// SAVE CALCULATION
// =========================

function saveCalculation(
    expression,
    result
) {

    fetch("/save-calculation", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({

            expression: expression,

            result: result

        })

    })

    .then(response => response.json())

    .then(data => {

        console.log(
            "Calculation saved:",
            data
        );

    })

    .catch(error => {

        console.log(
            "Could not save calculation:",
            error
        );

    });
}


// =========================
// KEYBOARD SUPPORT
// =========================

document.addEventListener(
    "keydown",
    function (event) {

        let key = event.key;


        if (
            (key >= "0" && key <= "9") ||
            key === "+" ||
            key === "-" ||
            key === "*" ||
            key === "/" ||
            key === "%" ||
            key === "." ||
            key === "(" ||
            key === ")"
        ) {

            press(key);

        }


        else if (key === "Enter") {

            event.preventDefault();

            calculate();

        }


        else if (key === "Escape") {

            clearDisplay();

        }


        else if (key === "Backspace") {

            backspace();

        }

    }
);


// =========================
// THEME SYSTEM
// =========================

function setupTheme() {

    const themeSelector =
        document.getElementById("themeSelector");


    if (!themeSelector) {

        console.log("Theme selector not found.");

        return;

    }


    let savedTheme =
        localStorage.getItem("calculatorTheme");


    if (!savedTheme) {

        savedTheme = "girlie";

    }


    themeSelector.value = savedTheme;

    applyTheme(savedTheme);


    themeSelector.addEventListener(
        "change",
        function () {

            let selectedTheme =
                themeSelector.value;


            localStorage.setItem(
                "calculatorTheme",
                selectedTheme
            );


            applyTheme(selectedTheme);

        }
    );

}


// =========================
// APPLY THEME
// =========================

function applyTheme(theme) {

    document.body.classList.remove(
        "theme-girlie",
        "theme-lavender",
        "theme-blue",
        "theme-green",
        "theme-dark"
    );


    document.body.classList.add(
        "theme-" + theme
    );

}