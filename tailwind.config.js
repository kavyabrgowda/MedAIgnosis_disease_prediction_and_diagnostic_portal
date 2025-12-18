/** @type {import('tailwindcss').Config} */

module.exports = {
    content: [
        './MDAI/src//*.{html,js,jsx,ts,tsx}', // Only scanning files in MDAI/src
        './doctor_form.html', // Add this if your HTML is directly in the root or public folder
        './doctor_login.html',
        './home.html',
        './index.html',
        './licence.html',
        './login.html',
        './main.html',
        './patient_form.html',
        './patient_login.html',
        './register.html',
        './result.html',
        './successful.html',
        './symptom_analysis.html',
        './symptopm.html',
        './welcome.html',
        './MDAI/templates//*.{html,js}' // Adjust this based on where your files are
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ["var(--Georgia)"],
            },
            colors: {
                //"hero-white": "#F6F9FF",

            },
            backgroundImage: {
                'header-pattern': "url('/img/regestration.jpg')",
            },
        },
    },
    plugins: [],
}


/* Command to pass in bash to import the requirements to the css file of public folder from src folder
-->(Akhila) npx tailwindcss -i ./MDAI/src/globals.css -o ./MDAI/templates/styles.css --watch
-->(Kavya)  npx tailwindcss -i ./static/css/globals.css -o ./MDAI/templates/styles.css --watch
*/