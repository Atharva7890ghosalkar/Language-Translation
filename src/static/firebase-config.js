// Firebase Modular Web SDK Configuration
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { 
    getAuth, 
    GoogleAuthProvider 
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

// Web app's Firebase configuration belonging to "Language Translation NLP"
const firebaseConfig = {
  apiKey: "AIzaSyCAVHyx6fvUwscTGCZBolmPIUjSuWgejPk",
  authDomain: "high-current-451215-c4.firebaseapp.com",
  projectId: "high-current-451215-c4",
  storageBucket: "high-current-451215-c4.firebasestorage.app",
  messagingSenderId: "1085236122372",
  appId: "1:1085236122372:web:c6914736b85678698bf651"
};

// Initialize Firebase App
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
const auth = getAuth(app);

// Initialize Google Auth Provider
const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
    prompt: 'select_account'
});

export { app, auth, googleProvider };
