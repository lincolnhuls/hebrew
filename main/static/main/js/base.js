// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-app.js";

// Import other Firebase services as needed
import { onAuthStateChanged, getAuth, signOut } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-auth.js";

// Import the firebaseConfig from the separate configuration file
import { firebaseConfig } from "./firebaseConfig.js";

console.log("Loaded File");

// Initialize Firebase
const app = initializeApp(firebaseConfig);
// Initialize the authorization from Firebase
const auth = getAuth(app);

// Nav + UI elements (may not exist on every page)
const signInLink = document.getElementById("signInLink");
const getStartedLink = document.getElementById("getStartedLink");
const signOutButton = document.getElementById("signOutButton");
const userGreeting = document.getElementById("userGreeting");

function getCookie(name) {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
        const [cookieName, cookieValue] = cookie.trim().split("=");
        if (cookieName === name) return cookieValue;
    }
    return null;
}

function setNavSignedIn(isSignedIn) {
    if (isSignedIn) {
        // signed in: ONLY sign out
        if (signInLink) {
            signInLink.classList.add("hidden");
        }
        if (getStartedLink) {
            getStartedLink.classList.add("hidden");
        }
        if (signOutButton) {
            signOutButton.classList.remove("hidden");
        }
    } else {
        // signed out: show sign in + get started, hide sign out
        if (signInLink) {
            signInLink.classList.remove("hidden");
        }
        if (getStartedLink) {
            getStartedLink.classList.remove("hidden");
        }
        if (signOutButton) {
            signOutButton.classList.add("hidden");
        }
    }
}

onAuthStateChanged(auth, async (user) => {
    if (user) {
        try {
            // Populate sessionStorage once per session
            if (!sessionStorage.getItem("username")) {
                const token = await user.getIdToken();
                const csrf = getCookie("csrftoken");

                const response = await fetch("/users/sessions/", {
                    method: "POST",
                    headers: {
                        Authorization: `Bearer ${token}`,
                        "Content-Type": "application/json",
                        ...(csrf ? { "X-CSRFToken": csrf } : {}),
                    },
                    credentials: "same-origin",
                });

                if (response.ok) {
                    const data = await response.json();
                    sessionStorage.setItem("username", data.user?.name ?? "");
                    sessionStorage.setItem("email", data.user?.email ?? "");
                    sessionStorage.setItem("firebase_uid", data.user?.firebase_uid ?? "");
                } else {
                    console.warn("Session endpoint returned:", response.status);
                }
            }
        } catch (err) {
            console.error("Error creating/updating session:", err);
        }

        const name = sessionStorage.getItem("username");
        console.log("User name from sessionStorage:", name);

        setNavSignedIn(true);

        // if (userGreeting) {
        //     userGreeting.textContent = name ? `Hello, ${name}!` : "Hello!";
        //     userGreeting.classList.remove("hidden");
        // }

        console.log("User is signed in:", user);
    } else {
        sessionStorage.removeItem("username");
        sessionStorage.removeItem("email");
        sessionStorage.removeItem("firebase_uid");

        if (userGreeting) {
            userGreeting.textContent = "";
            userGreeting.classList.add("hidden");
        }

        setNavSignedIn(false);

        console.log("No user is signed in.");
    }
});

if (signOutButton) {
    signOutButton.onclick = async (event) => {
        event.preventDefault();
        try {
            console.log("Signing out user...");
            await signOut(auth);

            await fetch("/users/logout/", {
                method: "POST",
                credentials: "include",
            });

            console.log("User signed out successfully.");
            window.location.href = "/";
        } catch (error) {
            console.error("Error signing out user:", error);
        }
    };
}
