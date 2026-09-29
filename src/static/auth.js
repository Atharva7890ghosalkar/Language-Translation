// Firebase Authentication Controller & UI Handler
import { auth, googleProvider } from "./firebase-config.js";
import { 
    onAuthStateChanged,
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    updateProfile,
    signInWithPopup,
    sendPasswordResetEmail,
    signOut
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements - Navigation & Gate Containers
    const authInitializing = document.getElementById("authInitializing");
    const authCard = document.getElementById("authCard");
    const translationCard = document.querySelector(".translation-card");
    const userProfile = document.getElementById("userProfile");

    // Auth Forms & Controls
    const signInForm = document.getElementById("signInForm");
    const signUpForm = document.getElementById("signUpForm");
    const forgotPasswordForm = document.getElementById("forgotPasswordForm");
    
    // Auth Mode Links & Buttons
    const switchToSignUpLink = document.getElementById("switchToSignUpLink");
    const switchToSignInLink = document.getElementById("switchToSignInLink");
    const forgotPasswordLink = document.getElementById("forgotPasswordLink");
    const backToSignInLink = document.getElementById("backToSignInLink");
    const googleSignInBtn = document.getElementById("googleSignInBtn");

    // Header Titles & Subtitles for Auth Modes
    const authCardTitle = document.getElementById("authCardTitle");
    const authCardSubtitle = document.getElementById("authCardSubtitle");
    const authBadgeIcon = document.getElementById("authBadgeIcon");
    const authAlertBanner = document.getElementById("authAlertBanner");
    const googleSignInContainer = document.getElementById("googleSignInContainer");
    const authDivider = document.getElementById("authDivider");

    // User Profile Header Components
    const profileDropdownBtn = document.getElementById("profileDropdownBtn");
    const profileDropdown = document.getElementById("profileDropdown");
    const userAvatarImg = document.getElementById("userAvatarImg");
    const userAvatarInitial = document.getElementById("userAvatarInitial");
    const userDisplayName = document.getElementById("userDisplayName");
    const profileMenuName = document.getElementById("profileMenuName");
    const profileMenuEmail = document.getElementById("profileMenuEmail");
    const providerBadgeText = document.getElementById("providerBadgeText");
    const signOutBtn = document.getElementById("signOutBtn");

    // Auth Mode State: 'signin' | 'signup' | 'forgot'
    let currentAuthMode = "signin";

    // --------------------------------------------------------------------------
    // Password Visibility Eye Toggles
    // --------------------------------------------------------------------------
    document.querySelectorAll(".btn-password-toggle").forEach(btn => {
        btn.addEventListener("click", () => {
            const targetId = btn.getAttribute("data-target");
            const input = document.getElementById(targetId);
            if (!input) return;
            const eyeOpen = btn.querySelector(".eye-open");
            const eyeClosed = btn.querySelector(".eye-closed");
            if (input.type === "password") {
                input.type = "text";
                if (eyeOpen) eyeOpen.classList.add("hidden");
                if (eyeClosed) eyeClosed.classList.remove("hidden");
            } else {
                input.type = "password";
                if (eyeOpen) eyeOpen.classList.remove("hidden");
                if (eyeClosed) eyeClosed.classList.add("hidden");
            }
        });
    });

    // --------------------------------------------------------------------------
    // 1. Firebase Auth Error Mapping (Human-Readable Messages)
    // --------------------------------------------------------------------------
    function getFriendlyErrorMessage(error) {
        const code = error.code || "";
        console.warn("Firebase Auth Error:", code, error.message);

        switch (code) {
            case "auth/invalid-credential":
            case "auth/wrong-password":
            case "auth/user-not-found":
                return "Incorrect email or password. Please try again.";
            case "auth/invalid-email":
                return "Please enter a valid email address.";
            case "auth/email-already-in-use":
                return "An account already exists with this email address.";
            case "auth/weak-password":
                return "Password is too weak. Please use at least 6 characters.";
            case "auth/popup-closed-by-user":
                return "Google sign-in was cancelled.";
            case "auth/account-exists-with-different-credential":
                return "An account already exists with this email using a different sign-in method. Please sign in using your original method.";
            case "auth/unauthorized-domain":
                return "This domain is not authorized for Firebase Auth. Please add it to your Firebase Console authorized domains.";
            case "auth/network-request-failed":
                return "Network connection error. Please check your internet connection.";
            case "auth/too-many-requests":
                return "Too many failed attempts. Please wait a few minutes before trying again.";
            default:
                return error.message || "An unexpected authentication error occurred.";
        }
    }

    // --------------------------------------------------------------------------
    // 2. Alert Banner Helpers
    // --------------------------------------------------------------------------
    function showAuthAlert(message, isSuccess = false) {
        if (!authAlertBanner) return;
        authAlertBanner.textContent = message;
        authAlertBanner.className = `auth-alert-banner ${isSuccess ? 'success' : 'error'}`;
        authAlertBanner.classList.remove("hidden");
    }

    function clearAuthAlert() {
        if (!authAlertBanner) return;
        authAlertBanner.textContent = "";
        authAlertBanner.className = "auth-alert-banner hidden";
    }

    // --------------------------------------------------------------------------
    // 3. Auth Form Mode Switching ('signin', 'signup', 'forgot')
    // --------------------------------------------------------------------------
    function setAuthMode(mode) {
        currentAuthMode = mode;
        clearAuthAlert();

        // Reset forms
        if (signInForm) signInForm.reset();
        if (signUpForm) signUpForm.reset();
        if (forgotPasswordForm) forgotPasswordForm.reset();

        if (mode === "signin") {
            if (authCard) {
                authCard.classList.remove("mode-signup", "mode-forgot");
            }
            if (authBadgeIcon) authBadgeIcon.classList.remove("hidden");
            authCardTitle.textContent = "Welcome Back";
            authCardSubtitle.textContent = "Sign in to access multilingual NLLB-200 translation workspace";
            if (signInForm) signInForm.classList.remove("hidden");
            if (signUpForm) signUpForm.classList.add("hidden");
            if (forgotPasswordForm) forgotPasswordForm.classList.add("hidden");
            if (googleSignInContainer) googleSignInContainer.classList.remove("hidden");
            if (authDivider) authDivider.classList.remove("hidden");
            if (window.location.hash) {
                history.replaceState(null, "", window.location.pathname);
            }
        } else if (mode === "signup") {
            if (authCard) {
                authCard.classList.remove("mode-forgot");
                authCard.classList.add("mode-signup");
            }
            if (authBadgeIcon) authBadgeIcon.classList.add("hidden");
            authCardTitle.textContent = "Create an account";
            authCardSubtitle.innerHTML = 'Already have an account? <a href="#" id="headerSignInLink" class="auth-text-link">Log in</a>';
            const headerSignInLink = document.getElementById("headerSignInLink");
            if (headerSignInLink) {
                headerSignInLink.addEventListener("click", (e) => {
                    e.preventDefault();
                    setAuthMode("signin");
                });
            }
            if (signInForm) signInForm.classList.add("hidden");
            if (signUpForm) signUpForm.classList.remove("hidden");
            if (forgotPasswordForm) forgotPasswordForm.classList.add("hidden");
            if (googleSignInContainer) googleSignInContainer.classList.add("hidden");
            if (authDivider) authDivider.classList.add("hidden");
            if (window.location.hash !== "#signup") {
                window.location.hash = "signup";
            }
        } else if (mode === "forgot") {
            if (authCard) {
                authCard.classList.remove("mode-signup");
                authCard.classList.add("mode-forgot");
            }
            if (authBadgeIcon) authBadgeIcon.classList.remove("hidden");
            authCardTitle.textContent = "Reset Password";
            authCardSubtitle.textContent = "Enter your registered email address to receive reset instructions";
            if (signInForm) signInForm.classList.add("hidden");
            if (signUpForm) signUpForm.classList.add("hidden");
            if (forgotPasswordForm) forgotPasswordForm.classList.remove("hidden");
            if (googleSignInContainer) googleSignInContainer.classList.add("hidden");
            if (authDivider) authDivider.classList.add("hidden");
            if (window.location.hash !== "#forgot") {
                window.location.hash = "forgot";
            }
        }
    }

    if (switchToSignUpLink) {
        switchToSignUpLink.addEventListener("click", (e) => {
            e.preventDefault();
            setAuthMode("signup");
        });
    }

    if (switchToSignInLink) {
        switchToSignInLink.addEventListener("click", (e) => {
            e.preventDefault();
            setAuthMode("signin");
        });
    }

    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener("click", (e) => {
            e.preventDefault();
            setAuthMode("forgot");
        });
    }

    if (backToSignInLink) {
        backToSignInLink.addEventListener("click", (e) => {
            e.preventDefault();
            setAuthMode("signin");
        });
    }

    // Sync hash changes with navigation
    window.addEventListener("hashchange", () => {
        if (!auth.currentUser) {
            if (window.location.hash === "#signup" && currentAuthMode !== "signup") {
                setAuthMode("signup");
            } else if (window.location.hash === "#forgot" && currentAuthMode !== "forgot") {
                setAuthMode("forgot");
            } else if (!window.location.hash && currentAuthMode !== "signin") {
                setAuthMode("signin");
            }
        }
    });

    if (backToSignInLink) {
        backToSignInLink.addEventListener("click", (e) => {
            e.preventDefault();
            setAuthMode("signin");
        });
    }

    // Button Spinner Toggle Helper
    function setButtonLoading(btn, isLoading, defaultText) {
        if (!btn) return;
        const btnText = btn.querySelector(".btn-text");
        const spinner = btn.querySelector(".btn-spinner");
        if (isLoading) {
            btn.disabled = true;
            if (btnText) btnText.textContent = "Processing...";
            if (spinner) spinner.classList.remove("hidden");
        } else {
            btn.disabled = false;
            if (btnText) btnText.textContent = defaultText;
            if (spinner) spinner.classList.add("hidden");
        }
    }

    // --------------------------------------------------------------------------
    // 4. Firebase Authentication Form Event Handlers
    // --------------------------------------------------------------------------

    // --- Sign In with Email / Password ---
    if (signInForm) {
        signInForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearAuthAlert();

            const email = document.getElementById("signInEmail").value.trim();
            const password = document.getElementById("signInPassword").value;
            const submitBtn = document.getElementById("signInSubmitBtn");

            if (!email || !password) {
                showAuthAlert("Please fill in both email and password.");
                return;
            }

            setButtonLoading(submitBtn, true, "Sign In");

            try {
                await signInWithEmailAndPassword(auth, email, password);
                // onAuthStateChanged will handle UI transition automatically
            } catch (err) {
                showAuthAlert(getFriendlyErrorMessage(err));
            } finally {
                setButtonLoading(submitBtn, false, "Sign In");
            }
        });
    }

    // --- Sign Up with Name / Email / Password ---
    if (signUpForm) {
        signUpForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearAuthAlert();

            const name = document.getElementById("signUpName").value.trim();
            const email = document.getElementById("signUpEmail").value.trim();
            const password = document.getElementById("signUpPassword").value;
            const confirmPassword = document.getElementById("signUpConfirmPassword").value;
            const submitBtn = document.getElementById("signUpSubmitBtn");

            if (!name || !email || !password || !confirmPassword) {
                showAuthAlert("Please fill in all required fields.");
                return;
            }

            if (password.length < 6) {
                showAuthAlert("Password must be at least 6 characters long.");
                return;
            }

            if (password !== confirmPassword) {
                showAuthAlert("Passwords do not match. Please verify your password.");
                return;
            }

            setButtonLoading(submitBtn, true, "Create Account");

            try {
                const userCredential = await createUserWithEmailAndPassword(auth, email, password);
                // Update Firebase User Profile with display name
                if (userCredential.user) {
                    await updateProfile(userCredential.user, {
                        displayName: name
                    });
                }
                // onAuthStateChanged will handle UI transition
            } catch (err) {
                showAuthAlert(getFriendlyErrorMessage(err));
            } finally {
                setButtonLoading(submitBtn, false, "Create Account");
            }
        });
    }

    // --- Sign In / Sign Up with Google ---
    const handleGoogleAuth = async () => {
        clearAuthAlert();
        try {
            await signInWithPopup(auth, googleProvider);
            // onAuthStateChanged handles transition
        } catch (err) {
            showAuthAlert(getFriendlyErrorMessage(err));
        }
    };

    if (googleSignInBtn) {
        googleSignInBtn.addEventListener("click", handleGoogleAuth);
    }
    const googleSignUpBtn = document.getElementById("googleSignUpBtn");
    if (googleSignUpBtn) {
        googleSignUpBtn.addEventListener("click", handleGoogleAuth);
    }

    // --- Password Reset ---
    if (forgotPasswordForm) {
        forgotPasswordForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearAuthAlert();

            const email = document.getElementById("resetEmail").value.trim();
            const submitBtn = document.getElementById("resetSubmitBtn");

            if (!email) {
                showAuthAlert("Please enter your email address.");
                return;
            }

            setButtonLoading(submitBtn, true, "Send Reset Instructions");

            try {
                await sendPasswordResetEmail(auth, email);
                showAuthAlert("If an account exists for this email, password-reset instructions have been sent.", true);
            } catch (err) {
                showAuthAlert(getFriendlyErrorMessage(err));
            } finally {
                setButtonLoading(submitBtn, false, "Send Reset Instructions");
            }
        });
    }

    // --------------------------------------------------------------------------
    // 5. Authenticated User Profile Dropdown & Sign Out
    // --------------------------------------------------------------------------
    if (profileDropdownBtn) {
        profileDropdownBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            const isHidden = profileDropdown.classList.contains("hidden");
            if (isHidden) {
                profileDropdown.classList.remove("hidden");
                profileDropdownBtn.setAttribute("aria-expanded", "true");
            } else {
                profileDropdown.classList.add("hidden");
                profileDropdownBtn.setAttribute("aria-expanded", "false");
            }
        });
    }

    // Close dropdown on outside click or Escape key
    document.addEventListener("click", (e) => {
        if (profileDropdown && !profileDropdown.classList.contains("hidden")) {
            if (!userProfile.contains(e.target)) {
                profileDropdown.classList.add("hidden");
                if (profileDropdownBtn) profileDropdownBtn.setAttribute("aria-expanded", "false");
            }
        }
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && profileDropdown && !profileDropdown.classList.contains("hidden")) {
            profileDropdown.classList.add("hidden");
            if (profileDropdownBtn) profileDropdownBtn.setAttribute("aria-expanded", "false");
        }
    });

    // --- Sign Out Action ---
    if (signOutBtn) {
        signOutBtn.addEventListener("click", async () => {
            if (profileDropdown) profileDropdown.classList.add("hidden");
            try {
                await signOut(auth);
                setAuthMode("signin");
            } catch (err) {
                console.error("Sign Out Error:", err);
            }
        });
    }

    // --------------------------------------------------------------------------
    // 6. Firebase Auth State Observer (Single Source of Truth)
    // --------------------------------------------------------------------------
    onAuthStateChanged(auth, (user) => {
        // Hide initializing overlay
        if (authInitializing) {
            authInitializing.classList.add("hidden");
        }

        if (user) {
            // USER IS SIGNED IN -> Enter Translation Workspace
            if (authCard) authCard.classList.add("hidden");
            if (translationCard) translationCard.classList.remove("hidden");
            if (userProfile) userProfile.classList.remove("hidden");

            // Extract display name & fallback to email prefix
            const displayNameVal = user.displayName || (user.email ? user.email.split("@")[0] : "Authenticated User");
            const firstInitial = displayNameVal.charAt(0).toUpperCase();

            // Populate Top Profile Pill
            if (userDisplayName) userDisplayName.textContent = displayNameVal;
            if (profileMenuName) profileMenuName.textContent = displayNameVal;
            if (profileMenuEmail) profileMenuEmail.textContent = user.email || "No email";

            // Determine auth provider (Google vs Email)
            const providerId = user.providerData && user.providerData[0] ? user.providerData[0].providerId : "";
            if (providerBadgeText) {
                providerBadgeText.textContent = providerId === "google.com" ? "Google Account" : "Email Account";
            }

            // Handle Avatar Image vs Initial Circle
            if (user.photoURL && userAvatarImg) {
                userAvatarImg.src = user.photoURL;
                userAvatarImg.classList.remove("hidden");
                if (userAvatarInitial) userAvatarInitial.classList.add("hidden");
            } else {
                if (userAvatarImg) userAvatarImg.classList.add("hidden");
                if (userAvatarInitial) {
                    userAvatarInitial.textContent = firstInitial;
                    userAvatarInitial.classList.remove("hidden");
                }
            }

        } else {
            // USER IS SIGNED OUT -> Show Auth Card Gate
            if (translationCard) translationCard.classList.add("hidden");
            if (userProfile) userProfile.classList.add("hidden");
            if (authCard) authCard.classList.remove("hidden");

            if (window.location.hash === "#signup") {
                setAuthMode("signup");
            } else if (window.location.hash === "#forgot") {
                setAuthMode("forgot");
            } else {
                setAuthMode("signin");
            }
        }
    });
});
