
// Get HTML elements
const imageInput = document.getElementById("imageInput");
const fileName = document.getElementById("fileName");

const rankSlider = document.getElementById("rankSlider");
const rankValue = document.getElementById("rankValue");

const compressionForm = document.getElementById("compressionForm");
const compressButton = document.getElementById("compressButton");

const compareSlider = document.getElementById("compareSlider");
const compressedOverlay = document.getElementById("compressedOverlay");


// -----------------------------------
// 1. Update Rank Slider
// -----------------------------------

if (rankSlider && rankValue) {

    rankSlider.addEventListener("input", function () {

        rankValue.textContent = rankSlider.value;

    });

}


// -----------------------------------
// 2. Image Upload and Validation
// -----------------------------------

if (imageInput) {

    imageInput.addEventListener("change", function () {

        const file = imageInput.files[0];

        if (!file) {

            fileName.textContent = "No image selected";

            return;

        }


        // Check file extension
        const allowedExtensions = ["jpg", "jpeg", "png"];

        const extension = file.name.split(".").pop().toLowerCase();

        if (!allowedExtensions.includes(extension)) {

            alert("Please select a JPG, JPEG or PNG image.");

            imageInput.value = "";

            fileName.textContent = "No image selected";

            return;

        }


        // Check file size (10 MB)
        const maxSize = 10 * 1024 * 1024;

        if (file.size > maxSize) {

            alert("Image size must be less than 10 MB.");

            imageInput.value = "";

            fileName.textContent = "No image selected";

            return;

        }


        // Display selected file name
        fileName.textContent = file.name;


        // Read image dimensions
        const image = new Image();

        image.onload = function () {

            const width = image.width;
            const height = image.height;

            // Match the maximum 600-pixel processing size
            const scale = Math.min(
                1,
                600 / Math.max(width, height)
            );

            const resizedWidth = Math.round(width * scale);
            const resizedHeight = Math.round(height * scale);

            const maxRank = Math.max(
                1,
                Math.min(resizedWidth, resizedHeight)
            );


            // Update rank slider maximum
            rankSlider.max = maxRank;

            if (Number(rankSlider.value) > maxRank) {

                rankSlider.value = maxRank;

            }

            rankValue.textContent = rankSlider.value;

            URL.revokeObjectURL(image.src);

        };

        image.src = URL.createObjectURL(file);

    });

}


// -----------------------------------
// 3. Compression Button
// -----------------------------------

if (compressionForm) {

    compressionForm.addEventListener("submit", function (event) {

        const file = imageInput.files[0];

        if (!file) {

            event.preventDefault();

            alert("Please select an image first.");

            return;

        }


        compressButton.disabled = true;

        compressButton.textContent = "Compressing... Please wait";

    });

}


// =================================
// 4. DARK MODE / LIGHT MODE
// =================================

const themeToggle = document.getElementById("themeToggle");

// Check saved theme or system preference
const savedTheme = localStorage.getItem("pixelmate-theme");

const systemPrefersDark = window.matchMedia(
    "(prefers-color-scheme: dark)"
).matches;

// Apply the theme
function applyTheme(theme) {

    if (theme === "dark") {

        document.body.classList.add("dark-mode");

        themeToggle.textContent = "☀️ Light Mode";

    } else {

        document.body.classList.remove("dark-mode");

        themeToggle.textContent = "🌙 Dark Mode";

    }

}

// Set initial theme
const initialTheme = savedTheme ||
    (systemPrefersDark ? "dark" : "light");

applyTheme(initialTheme);

// Toggle theme when button is clicked
themeToggle.addEventListener("click", function () {

    const isDark = document.body.classList.contains("dark-mode");

    const newTheme = isDark ? "light" : "dark";

    applyTheme(newTheme);

    // Remember selected theme
    localStorage.setItem("pixelmate-theme", newTheme);

});
