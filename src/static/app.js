/**
 * Multilingual Language Translation Application Client
 * 
 * Features:
 * - Dynamic loading of supported languages from /languages endpoint
 * - Accessible, searchable custom language dropdowns (instant case-insensitive filter)
 * - Keyboard navigation (Arrow keys, Enter, Escape)
 * - Top-right visual profile shell with escape & click-outside dismissal
 * - Expand / Collapse workspace mode (preserving text without resetting)
 * - Translation workflow via POST /translate with loading & error UI
 * - Client-side UTF-8 .txt file download with sanitized naming
 * - Clipboard copy with visual feedback
 * - Language & text swapping
 * - Live character counter (max 2000 chars)
 */

document.addEventListener("DOMContentLoaded", () => {


    // DOM Elements - Language Selectors
    const sourceLangBtn = document.getElementById("sourceLangBtn");
    const sourceLangSelectedText = document.getElementById("sourceLangSelectedText");
    const sourceDropdown = document.getElementById("sourceDropdown");
    const sourceSearchInput = document.getElementById("sourceSearchInput");
    const sourceOptionsList = document.getElementById("sourceOptionsList");

    const targetLangBtn = document.getElementById("targetLangBtn");
    const targetLangSelectedText = document.getElementById("targetLangSelectedText");
    const targetDropdown = document.getElementById("targetDropdown");
    const targetSearchInput = document.getElementById("targetSearchInput");
    const targetOptionsList = document.getElementById("targetOptionsList");

    const swapBtn = document.getElementById("swapBtn");

    // DOM Elements - Panes & Textareas
    const sourcePane = document.getElementById("sourcePane");
    const targetPane = document.getElementById("targetPane");
    const sourceExpandBtn = document.getElementById("sourceExpandBtn");
    const targetExpandBtn = document.getElementById("targetExpandBtn");
    const sourceText = document.getElementById("sourceText");
    const targetText = document.getElementById("targetText");
    const charCount = document.getElementById("charCount");
    const sourceLangTitle = document.getElementById("sourceLangTitle");
    const targetLangTitle = document.getElementById("targetLangTitle");

    // DOM Elements - Actions & Status
    const translateBtn = document.getElementById("translateBtn");
    const translateBtnText = document.getElementById("translateBtnText");
    const clearBtn = document.getElementById("clearBtn");
    const copyBtn = document.getElementById("copyBtn");
    const copyText = document.getElementById("copyText");
    const downloadBtn = document.getElementById("downloadBtn");
    const downloadText = document.getElementById("downloadText");

    const loadingOverlay = document.getElementById("loadingOverlay");
    const alertBanner = document.getElementById("alertBanner");

    const MAX_CHARS = 2000;

    // State
    let availableLanguages = [];
    let selectedSourceLang = "English";
    let selectedTargetLang = "French";
    let isTranslating = false;
    let sourceExpanded = false;
    let targetExpanded = false;

    // Icons for Expand & Collapse
    const EXPAND_ICON_SVG = `<svg class="expand-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>`;
    const COLLAPSE_ICON_SVG = `<svg class="expand-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 14 10 14 10 20"></polyline><polyline points="20 10 14 10 14 4"></polyline><line x1="14" y1="10" x2="21" y2="3"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>`;





    // =========================================================================
    // Searchable Dropdown Class
    // =========================================================================
    class SearchableDropdown {
        constructor({ triggerBtn, selectedTextEl, dropdownPanel, searchInput, optionsListEl, onSelect }) {
            this.triggerBtn = triggerBtn;
            this.selectedTextEl = selectedTextEl;
            this.dropdownPanel = dropdownPanel;
            this.searchInput = searchInput;
            this.optionsListEl = optionsListEl;
            this.onSelect = onSelect;
            this.highlightedIndex = -1;
            this.filteredLanguages = [];

            this.initEvents();
        }

        initEvents() {
            // Toggle dropdown
            this.triggerBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                const isExpanded = this.dropdownPanel.classList.contains("hidden");
                closeAllDropdowns();
                if (isExpanded) {
                    this.open();
                }
            });

            // Filter on search input
            this.searchInput.addEventListener("input", () => {
                this.filter(this.searchInput.value.trim());
            });

            // Prevent dropdown panel click from closing itself
            this.dropdownPanel.addEventListener("click", (e) => {
                e.stopPropagation();
            });

            // Keyboard navigation
            this.searchInput.addEventListener("keydown", (e) => {
                this.handleKeydown(e);
            });

            this.triggerBtn.addEventListener("keydown", (e) => {
                if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    if (this.dropdownPanel.classList.contains("hidden")) {
                        closeAllDropdowns();
                        this.open();
                    }
                }
            });
        }

        open() {
            this.dropdownPanel.classList.remove("hidden");
            this.triggerBtn.classList.add("active");
            this.triggerBtn.setAttribute("aria-expanded", "true");
            this.searchInput.value = "";
            this.filter("");
            setTimeout(() => this.searchInput.focus(), 50);
        }

        close() {
            this.dropdownPanel.classList.add("hidden");
            this.triggerBtn.classList.remove("active");
            this.triggerBtn.setAttribute("aria-expanded", "false");
            this.highlightedIndex = -1;
        }

        setSelected(language) {
            this.selectedTextEl.textContent = language;
            this.renderList();
        }

        filter(query) {
            const lowerQuery = query.toLowerCase();
            this.filteredLanguages = availableLanguages.filter(lang =>
                lang.toLowerCase().includes(lowerQuery)
            );
            this.highlightedIndex = this.filteredLanguages.length > 0 ? 0 : -1;
            this.renderList();
        }

        renderList() {
            this.optionsListEl.innerHTML = "";

            if (this.filteredLanguages.length === 0) {
                const emptyItem = document.createElement("li");
                emptyItem.className = "empty-state-item";
                emptyItem.textContent = "No languages found";
                this.optionsListEl.appendChild(emptyItem);
                return;
            }

            const currentSelected = this.selectedTextEl.textContent;

            this.filteredLanguages.forEach((lang, index) => {
                const li = document.createElement("li");
                li.className = "option-item";
                li.setAttribute("role", "option");
                li.setAttribute("id", `opt-${lang.toLowerCase()}`);
                li.textContent = lang;

                const isSelected = lang === currentSelected;
                if (isSelected) {
                    li.classList.add("selected");
                    li.setAttribute("aria-selected", "true");
                    const checkSpan = document.createElement("span");
                    checkSpan.className = "option-check";
                    checkSpan.textContent = "✓";
                    li.appendChild(checkSpan);
                } else {
                    li.setAttribute("aria-selected", "false");
                }

                if (index === this.highlightedIndex) {
                    li.classList.add("highlighted");
                }

                li.addEventListener("click", () => {
                    this.onSelect(lang);
                    this.close();
                    this.triggerBtn.focus();
                });

                this.optionsListEl.appendChild(li);
            });

            this.scrollHighlightedIntoView();
        }

        handleKeydown(e) {
            const items = this.optionsListEl.querySelectorAll(".option-item");
            if (!items.length) return;

            if (e.key === "ArrowDown") {
                e.preventDefault();
                this.highlightedIndex = (this.highlightedIndex + 1) % this.filteredLanguages.length;
                this.updateHighlightedItem(items);
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                this.highlightedIndex = (this.highlightedIndex - 1 + this.filteredLanguages.length) % this.filteredLanguages.length;
                this.updateHighlightedItem(items);
            } else if (e.key === "Enter") {
                e.preventDefault();
                if (this.highlightedIndex >= 0 && this.highlightedIndex < this.filteredLanguages.length) {
                    const chosen = this.filteredLanguages[this.highlightedIndex];
                    this.onSelect(chosen);
                    this.close();
                    this.triggerBtn.focus();
                }
            } else if (e.key === "Escape") {
                e.preventDefault();
                this.close();
                this.triggerBtn.focus();
            }
        }

        updateHighlightedItem(items) {
            items.forEach((item, idx) => {
                if (idx === this.highlightedIndex) {
                    item.classList.add("highlighted");
                } else {
                    item.classList.remove("highlighted");
                }
            });
            this.scrollHighlightedIntoView();
        }

        scrollHighlightedIntoView() {
            const highlightedEl = this.optionsListEl.querySelector(".option-item.highlighted");
            if (highlightedEl) {
                highlightedEl.scrollIntoView({ block: "nearest" });
            }
        }
    }

    function closeAllDropdowns() {
        sourceDropdownInstance.close();
        targetDropdownInstance.close();
    }

    // Close dropdowns when clicking outside
    document.addEventListener("click", () => {
        closeAllDropdowns();
    });

    // Close on Escape key
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeAllDropdowns();
        }
    });

    // =========================================================================
    // Initialize Searchable Dropdown Instances
    // =========================================================================
    const sourceDropdownInstance = new SearchableDropdown({
        triggerBtn: sourceLangBtn,
        selectedTextEl: sourceLangSelectedText,
        dropdownPanel: sourceDropdown,
        searchInput: sourceSearchInput,
        optionsListEl: sourceOptionsList,
        onSelect: (lang) => {
            selectedSourceLang = lang;
            sourceDropdownInstance.setSelected(lang);
            updateWorkspaceTitles();
        }
    });

    const targetDropdownInstance = new SearchableDropdown({
        triggerBtn: targetLangBtn,
        selectedTextEl: targetLangSelectedText,
        dropdownPanel: targetDropdown,
        searchInput: targetSearchInput,
        optionsListEl: targetOptionsList,
        onSelect: (lang) => {
            selectedTargetLang = lang;
            targetDropdownInstance.setSelected(lang);
            updateWorkspaceTitles();
        }
    });

    // =========================================================================
    // Reliable Single-Source-of-Truth Expand / Collapse State Logic
    // =========================================================================
    function setPaneExpanded(isSource, expand) {
        if (isSource) {
            sourceExpanded = expand;
            sourcePane.classList.toggle("expanded", sourceExpanded);
            sourceText.style.height = ""; // Reset manual inline height to ensure clean CSS class control
            if (sourceExpandBtn) {
                sourceExpandBtn.innerHTML = sourceExpanded ? COLLAPSE_ICON_SVG : EXPAND_ICON_SVG;
                sourceExpandBtn.title = sourceExpanded ? "Collapse editor" : "Expand editor";
                sourceExpandBtn.setAttribute("aria-label", sourceExpanded ? "Collapse editor" : "Expand editor");
                sourceExpandBtn.setAttribute("aria-expanded", sourceExpanded ? "true" : "false");
            }
        } else {
            targetExpanded = expand;
            targetPane.classList.toggle("expanded", targetExpanded);
            targetText.style.height = ""; // Reset manual inline height to ensure clean CSS class control
            if (targetExpandBtn) {
                targetExpandBtn.innerHTML = targetExpanded ? COLLAPSE_ICON_SVG : EXPAND_ICON_SVG;
                targetExpandBtn.title = targetExpanded ? "Collapse editor" : "Expand editor";
                targetExpandBtn.setAttribute("aria-label", targetExpanded ? "Collapse editor" : "Expand editor");
                targetExpandBtn.setAttribute("aria-expanded", targetExpanded ? "true" : "false");
            }
        }
    }

    if (sourceExpandBtn) {
        sourceExpandBtn.addEventListener("click", () => {
            setPaneExpanded(true, !sourceExpanded);
        });
    }

    if (targetExpandBtn) {
        targetExpandBtn.addEventListener("click", () => {
            setPaneExpanded(false, !targetExpanded);
        });
    }



    // =========================================================================
    // API: Load Supported Languages (Single Source of Truth)
    // =========================================================================
    async function loadLanguages() {
        try {
            const response = await fetch("/languages");
            if (!response.ok) {
                throw new Error(`Server returned HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            availableLanguages = data.languages || [];

            if (!availableLanguages.length) {
                throw new Error("No supported languages found in response.");
            }

            // Set sensible defaults if available
            if (availableLanguages.includes("English")) {
                selectedSourceLang = "English";
            } else {
                selectedSourceLang = availableLanguages[0];
            }

            if (availableLanguages.includes("French")) {
                selectedTargetLang = "French";
            } else if (availableLanguages.length > 1) {
                selectedTargetLang = availableLanguages[1];
            } else {
                selectedTargetLang = availableLanguages[0];
            }

            sourceDropdownInstance.setSelected(selectedSourceLang);
            targetDropdownInstance.setSelected(selectedTargetLang);
            updateWorkspaceTitles();
            updateDownloadState();
        } catch (error) {
            showAlert(`Failed to load supported languages: ${error.message}. Please refresh the page.`, "error");
        }
    }

    // Update Workspace Headers
    function updateWorkspaceTitles() {
        sourceLangTitle.textContent = `From: ${selectedSourceLang}`;
        targetLangTitle.textContent = `To: ${selectedTargetLang}`;
    }

    function updateDownloadState() {
        const hasText = targetText.value.trim().length > 0;
        downloadBtn.disabled = !hasText;
    }

    // Alert Banner Helpers
    function showAlert(message, type = "error") {
        alertBanner.textContent = message;
        alertBanner.className = `alert-banner ${type}`;
        alertBanner.classList.remove("hidden");
    }

    function hideAlert() {
        alertBanner.classList.add("hidden");
    }

    // =========================================================================
    // Character Counter
    // =========================================================================
    sourceText.addEventListener("input", () => {
        const currentLength = sourceText.value.length;
        charCount.textContent = `${currentLength} / ${MAX_CHARS}`;

        if (currentLength > MAX_CHARS) {
            charCount.style.color = "var(--error-color)";
        } else if (currentLength > MAX_CHARS * 0.9) {
            charCount.style.color = "#f59e0b"; // Warning amber
        } else {
            charCount.style.color = "var(--text-muted)";
        }
    });

    targetText.addEventListener("input", updateDownloadState);

    // =========================================================================
    // Action: Swap Languages & Text
    // =========================================================================
    swapBtn.addEventListener("click", () => {
        const tempLang = selectedSourceLang;
        selectedSourceLang = selectedTargetLang;
        selectedTargetLang = tempLang;

        sourceDropdownInstance.setSelected(selectedSourceLang);
        targetDropdownInstance.setSelected(selectedTargetLang);

        const tempText = sourceText.value;
        sourceText.value = targetText.value;
        targetText.value = tempText;

        updateWorkspaceTitles();
        updateDownloadState();
        sourceText.dispatchEvent(new Event("input"));
    });

    // =========================================================================
    // Action: Clear
    // =========================================================================
    clearBtn.addEventListener("click", () => {
        sourceText.value = "";
        targetText.value = "";
        hideAlert();
        updateDownloadState();
        sourceText.dispatchEvent(new Event("input"));
        sourceText.focus();
    });

    // =========================================================================
    // Action: Copy Translation
    // =========================================================================
    copyBtn.addEventListener("click", async () => {
        const textToCopy = targetText.value.trim();
        if (!textToCopy) {
            showAlert("No translation text available to copy.", "warning");
            return;
        }

        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(textToCopy);
            } else {
                // Fallback for non-https/older contexts
                targetText.select();
                document.execCommand("copy");
            }

            const originalText = copyText.textContent;
            copyText.textContent = "Copied ✓";
            copyBtn.classList.add("success-feedback");

            setTimeout(() => {
                copyText.textContent = originalText;
                copyBtn.classList.remove("success-feedback");
            }, 2000);
        } catch (err) {
            showAlert("Failed to copy text to clipboard.", "error");
        }
    });

    // =========================================================================
    // Action: Download Translation (.txt)
    // =========================================================================
    downloadBtn.addEventListener("click", () => {
        const textToDownload = targetText.value.trim();
        if (!textToDownload) {
            showAlert("Please translate text before downloading.", "warning");
            return;
        }

        try {
            // Create UTF-8 encoded text blob
            const blob = new Blob([textToDownload], { type: "text/plain;charset=utf-8" });
            const url = URL.createObjectURL(blob);

            // Construct sanitized descriptive filename
            const cleanSrc = selectedSourceLang.replace(/[^a-zA-Z0-9_-]/g, "_");
            const cleanTgt = selectedTargetLang.replace(/[^a-zA-Z0-9_-]/g, "_");
            const filename = `translation_${cleanSrc}_to_${cleanTgt}.txt`;

            // Trigger browser download via anchor element
            const anchor = document.createElement("a");
            anchor.href = url;
            anchor.download = filename;
            document.body.appendChild(anchor);
            anchor.click();
            document.body.removeChild(anchor);
            URL.revokeObjectURL(url);

            // Visual feedback
            const originalText = downloadText.textContent;
            downloadText.textContent = "Downloaded ✓";
            downloadBtn.classList.add("success-feedback");

            setTimeout(() => {
                downloadText.textContent = originalText;
                downloadBtn.classList.remove("success-feedback");
            }, 2000);
        } catch (err) {
            showAlert(`Failed to download translation file: ${err.message}`, "error");
        }
    });

    // =========================================================================
    // Action: Translate
    // =========================================================================
    async function performTranslation() {
        if (isTranslating) return;
        hideAlert();

        const rawText = sourceText.value;
        const text = rawText.trim();

        if (!text) {
            showAlert("Please enter text to translate.", "warning");
            sourceText.focus();
            return;
        }

        if (rawText.length > MAX_CHARS) {
            showAlert(`Text exceeds maximum allowed limit of ${MAX_CHARS} characters.`, "error");
            return;
        }

        // Set Loading State
        isTranslating = true;
        loadingOverlay.classList.remove("hidden");
        translateBtn.disabled = true;
        translateBtnText.textContent = "Translating...";

        try {
            const response = await fetch("/translate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: rawText,
                    source_language: selectedSourceLang,
                    target_language: selectedTargetLang
                })
            });

            const data = await response.json();

            if (!response.ok) {
                const errorMessage = data.detail || `Server returned error status ${response.status}`;
                throw new Error(errorMessage);
            }

            targetText.value = data.translated_text || "";
            updateDownloadState();
        } catch (error) {
            showAlert(`Translation error: ${error.message}`, "error");
        } finally {
            loadingOverlay.classList.add("hidden");
            translateBtn.disabled = false;
            translateBtnText.textContent = "Translate";
            isTranslating = false;
        }
    }

    translateBtn.addEventListener("click", performTranslation);

    // Keyboard shortcut: Ctrl+Enter (or Cmd+Enter) in textarea triggers translation
    sourceText.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            performTranslation();
        }
    });

    // Initial Load
    loadLanguages();
});
