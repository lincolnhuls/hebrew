// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-app.js";

// Import other Firebase services as needed
import { onAuthStateChanged, getAuth, signOut } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-auth.js";

// Import the firebaseConfig from the separate configuration file
import { firebaseConfig } from "./firebaseConfig.js";

console.log("Loaded File")

// Initialize Firebase
const app = initializeApp(firebaseConfig);
// Initalize the authorization from Firebase
const auth = getAuth(app);

// const signed_in = document.getElementById("signed_in");

const signInButton = document.getElementById("signInButton");
const signOutButton = document.getElementById("signOutButton");
const userGreeting = document.getElementById("userGreeting");

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

onAuthStateChanged(auth, async user => {
    if (user) {
        const token = await user.getIdToken();

        let name = '';

        const response = await fetch("/users/sessions/", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            },
            credentials: "same-origin",
        });

        if (response.ok) {
            const data = await response.json();
            name = data?.user?.name || '';
        }
        console.log("User name from sessionStorage:", name);
        if (signInButton) {
            signInButton.classList.add('hidden');
        }
        if (signOutButton) {
            signOutButton.classList.remove('hidden');
        }
        if (userGreeting) {
            if (name == null || name === '') {
                userGreeting.textContent = `Hello!`;
            } else {
                userGreeting.textContent = `Hello, ${name}!`;
            }
            userGreeting.classList.remove('hidden');
        }
        console.log('User is signed in:', user);
    } else {
        if (userGreeting) {
            userGreeting.textContent = '';
            userGreeting.classList.add('hidden');
        }
        if (signInButton) {
            signInButton.classList.remove('hidden');
        }
        if (signOutButton) {
            signOutButton.classList.add('hidden');
        }
        console.log('No user is signed in.');
    }
})

if (signOutButton) { signOutButton.onclick = async (event) => {
    event.preventDefault();
    const csrfToken = getCookie("csrftoken");
    try {
        console.log('Signing out user...');
        await signOut(auth);
        await fetch("/users/logout/", { 
            method: "POST",
            credentials: "include",
            headers: {
                "X-CSRFToken": csrfToken
            }
        })
        console.log('User signed out successfully.');
        window.location.href = "/"; 
    }
    catch (error) {
        console.error('Error signing out user:', error);
    }
};
}

if (signInButton) { signInButton.onclick = async (event) => {
    event.preventDefault();
    try {
        console.log('Navigating to sign-in page...');
        window.location.href = "/users/account/"; 
    }
    catch (error) {
        console.error('Error navigating to sign-in:', error);
    }
};
}