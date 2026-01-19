// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-app.js";

// Import other Firebase services as needed
import { onAuthStateChanged, getAuth, signOut } from "https://www.gstatic.com/firebasejs/12.7.0/firebase-auth.js";


// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries
// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBuJ-q4SaECbrc6VAW7z94ubGHelkdPPWo",
    authDomain: "auth-b32fb.firebaseapp.com",
    projectId: "auth-b32fb",
    storageBucket: "auth-b32fb.firebasestorage.app",
    messagingSenderId: "512245365222",
    appId: "1:512245365222:web:5a03f94e2438d36fcbbe27"
};
console.log("Loaded File")

// Initialize Firebase
const app = initializeApp(firebaseConfig);
// Initalize the authorization from Firebase
const auth = getAuth(app);

// const signed_in = document.getElementById("signed_in");

const signInButton = document.getElementById("signInButton");
const signOutButton = document.getElementById("signOutButton");
const userGreeting = document.getElementById("userGreeting");

onAuthStateChanged(auth, user => {
    if (user) {
        let name = sessionStorage.getItem('username');
        console.log("User name from sessionStorage:", name);
        signInButton.classList.add('hidden');
        signOutButton.classList.remove('hidden');
        userGreeting.textContent = `Hello, ${name}!`;
        userGreeting.classList.remove('hidden');
        console.log('User is signed in:', user);
    } else {
        sessionStorage.removeItem('username');
        sessionStorage.removeItem('email');
        sessionStorage.removeItem('firebase_uid');
        userGreeting.textContent = '';
        userGreeting.classList.add('hidden');
        signInButton.classList.remove('hidden');
        signOutButton.classList.add('hidden');
        console.log('No user is signed in.');
    }
})

document.getElementById("signOutButton").addEventListener("click", async (event) => {
    event.preventDefault();
    try {
        console.log('Signing out user...');
        await signOut(auth);
        console.log('User signed out successfully.');
        window.location.href = "/users/"; 
    }
    catch (error) {
        console.error('Error signing out user:', error);
    }
});

document.getElementById("signInButton").addEventListener("click", async (event) => {
    event.preventDefault();
    try {
        console.log('Navigating to sign-in page...');
        window.location.href = "/users/account/"; 
    }
    catch (error) {
        console.error('Error navigating to sign-in:', error);
    }
});