// Test user 
// name = asdf
// email = asdf@example.com
// password = test-Auth-9f3K!2
// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-app.js";

// Import other Firebase services as needed
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-auth.js";

// Your web app's Firebase configuration
import { firebaseConfig } from "./firebaseConfig.js";

// Initialize Firebase
const app = initializeApp(firebaseConfig);
// Initalize the authorization from Firebase
const auth = getAuth(app);

const messages = document.getElementById("error_messages");

// Password visibility toggle
const passwordInput = document.getElementById("password");
const passwordToggle = document.getElementById("password-toggle");
const nameField = document.getElementById("name-field");
const signinBtn = document.getElementById("signin-btn");
const signupBtn = document.getElementById("signup-btn");

if (passwordToggle) {
    passwordToggle.addEventListener("click", () => {
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);
    });
}

// Show/hide name field based on button clicked
if (signinBtn && signupBtn && nameField) {
    signinBtn.addEventListener("click", () => {
        if (nameField) {
            nameField.style.display = "none";
        }
    });
    
    signupBtn.addEventListener("click", () => {
        if (nameField) {
            nameField.style.display = "flex";
        }
    });
}

document.getElementById("user_form").addEventListener("submit", async event => {    
    event.preventDefault();
    const submitterValue = event.submitter.value;
    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    if (submitterValue == "signup") {
        await signupUser(name, email, password);
    } else {
        await loginUser(name, email, password);
    }
})

function getCookie(name) {
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split("=");
        if (cookieName === name) {
            return cookieValue;
        }
    }
    return null;
}

async function createSession(idToken, name='') {
    const csrfToken = getCookie("csrftoken");
    const response = await fetch("/users/sessions/", {
    method: "POST",
    headers: {
        "Authorization": `Bearer ${idToken}`,
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
    },
    credentials: "same-origin",
    body: JSON.stringify(
        name ? { name: name } : {}
    )
    });
    if (!response.ok) {
        const errorText = await response.text();
        console.error("Error creating session on server:", errorText);
        throw new Error("Failed to create session on server");
    }
    console.log("Session created on server.");
    const data = await response.json();
    console.log("Server response:", data);

    return data;
}

async function signupUser(name, email, password) {
    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        const userToken = await user.getIdToken(true);
        await createSession(userToken, name);
        console.log('User created:', userCredential.user);
        messages.textContent = "User created successfully.";
        window.location.href = "/dashboard/"; 
    } catch (error) {
        console.error('Error creating user:', error);
        displayError(error.code);
    }
}

async function loginUser(name, email, password) {
    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        const userToken = await user.getIdToken(true);
        await createSession(userToken, name);
        console.log('User logged in:', userCredential.user);
        messages.textContent = "User logged in successfully.";
        window.location.href = "/dashboard/"; 
    } catch (error) {
        console.error('Error logging in user:', error);
        displayError(error.code);
    }
}

function displayError(message) {
    if (message == 'auth/email-already-in-use') {
        messages.textContent = "This email is already in use.";
    } else if (message == 'auth/invalid-email') {
        messages.textContent = "The email address is not valid."; 
    } else if (message == 'auth/invalid-credential') {
        messages.textContent = "The password is incorrect.";
    } else if (message == 'auth/user-not-found') {
        messages.textContent = "No user found with this email.";
    } else {
        messages.textContent = "An unknown error occurred.";
    }
}