// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-app.js";

// Import other Firebase services as needed
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, sendPasswordResetEmail } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-auth.js";

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
const forgotPasswordLink = document.getElementById("forgot-password");
const forgotPasswordMessage = document.getElementById("forgot-password-message");

if (passwordToggle) {
    passwordToggle.addEventListener("click", () => {
        const type = passwordInput.getAttribute("type") === "password" ? "text" : "password";
        passwordInput.setAttribute("type", type);
    });
}

// Forgot password: send reset email via Firebase
if (forgotPasswordLink) {
    forgotPasswordLink.addEventListener("click", async (event) => {
        event.preventDefault();
        const emailInput = document.getElementById("email");
        const email = emailInput ? emailInput.value.trim() : "";
        const target = forgotPasswordMessage || messages;

        if (!target) {
            return;
        }

        if (!email) {
            target.textContent = "Enter your email to reset your password.";
            return;
        }

        try {
            await sendPasswordResetEmail(auth, email);
            target.textContent = "If an account exists for this email, a reset link has been sent. Check your inbox and spam folder.";
        } catch (error) {
            console.error("Error sending password reset email:", error);
            // For security, don't reveal whether the email exists
            target.textContent = "If an account exists for this email, a reset link has been sent. Check your inbox and spam folder.";
        }
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

    // Require a name only when signing up
    if (submitterValue === "signup" && !name) {
        if (messages) {
            messages.textContent = "Please enter your name to sign up.";
        }
        return;
    }

    if (submitterValue === "signup") {
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
        const raw = await response.text();
        console.error("Error creating session on server:", response.status, raw);
        let detail = raw.slice(0, 400);
        try {
            const errJson = JSON.parse(raw);
            if (errJson.error || errJson.details) {
                detail = [errJson.error, errJson.details].filter(Boolean).join(" — ");
            }
        } catch {
            /* use raw slice */
        }
        let hint = "";
        if (response.status === 403) {
            hint =
                " (CSRF: hard-refresh this page, then sign in again. Do not open the app in multiple tabs with an old page.)";
        } else if (response.status === 401) {
            hint =
                " (Server could not verify the Firebase token — usually missing or wrong Firebase Admin credentials on the server.)";
        }
        throw new Error(`Failed to create session: HTTP ${response.status} — ${detail}${hint}`);
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
        
        await createSession(userToken, name);
        console.log("Session created successfully, redirecting...");
        messages.textContent = "User created successfully.";
        window.location.replace("/dashboard/");
    } catch (error) {
        console.error("Error creating user:", error);
        if (error && error.message && error.message.includes("Failed to create session")) {
            messages.textContent = error.message;
        } else {
            displayError(error.code);
        }
    }
}

async function loginUser(name, email, password) {
    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        const userToken = await user.getIdToken(true);
        
        console.log('User logged in:', userCredential.user);
        
        await createSession(userToken, name || "");
        console.log("Session created successfully, redirecting...");
        messages.textContent = "User logged in successfully.";
        window.location.replace("/dashboard/");
    } catch (error) {
        console.error("Error logging in user:", error);
        if (error && error.message && error.message.includes("Failed to create session")) {
            messages.textContent = error.message;
        } else {
            displayError(error.code);
        }
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