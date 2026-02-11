// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-app.js";

// Import other Firebase services as needed
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-auth.js";

// Your web app's Firebase configuration
import { firebaseConfig } from "./firebaseConfig.js";

// Import shared utilities (Note: utils.js is in main app, so we'll keep getCookie local for now)
// TODO: Create shared utils module accessible from users app

// Initialize Firebase
const app = initializeApp(firebaseConfig);
// Initialize the authorization from Firebase
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
            nameField.classList.remove("name-field-visible");
            nameField.classList.add("name-field-hidden");
        }
    });
    
    signupBtn.addEventListener("click", () => {
        if (nameField) {
            nameField.classList.remove("name-field-hidden");
            nameField.classList.add("name-field-visible");
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
    if (!csrfToken) {
        console.warn("No CSRF token found, session creation may fail");
    }
    
    const response = await fetch("/users/sessions/", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${idToken}`,
            "Content-Type": "application/json",
            ...(csrfToken ? { "X-CSRFToken": csrfToken } : {})
        },
        credentials: "same-origin",
        body: JSON.stringify(
            name ? { name: name } : {}
        )
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        console.error("Error creating session on server:", response.status, errorText);
        throw new Error(`Failed to create session on server: ${response.status}`);
    }
    
    const data = await response.json();
    console.log("Session created on server:", data);
    return data;
}

async function signupUser(name, email, password) {
    try {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        const userToken = await user.getIdToken(true);
        
        console.log('User created:', userCredential.user);
        
        // Create session and wait for it to complete
        try {
            await createSession(userToken, name);
            console.log('Session created successfully, redirecting...');
        } catch (sessionError) {
            console.error('Session creation error:', sessionError);
            // Still try to redirect - session might be created by base.js
        }
        
        messages.textContent = "User created successfully.";
        
        // Use window.location.replace for immediate redirect
        window.location.replace("/dashboard/");
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
        
        console.log('User logged in:', userCredential.user);
        
        // Create session and wait for it to complete
        let sessionCreated = false;
        try {
            const sessionData = await createSession(userToken, name || '');
            console.log('Session created successfully:', sessionData);
            sessionCreated = true;
        } catch (sessionError) {
            console.error('Session creation error:', sessionError);
            // Try redirect anyway - base.js might handle session creation
        }
        
        messages.textContent = "User logged in successfully.";
        
        // Wait a bit longer to ensure session is fully set on server
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Use window.location.replace for immediate redirect
        console.log('Redirecting to dashboard...');
        window.location.replace("/dashboard/");
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