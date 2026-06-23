/**
 * Semantic Location Autocomplete
 * Provides intelligent location suggestions using embeddings
 * with keyboard navigation, ARIA accessibility, and XSS protection
 */

(function () {
    const input = document.getElementById("search");
    const dropdown = document.getElementById("autocompleteDropdown");
    let debounceTimer;
    let currentFocus = -1;

    // ── Setup ARIA attributes ──
    input.setAttribute("aria-autocomplete", "list");
    input.setAttribute("aria-controls", "autocompleteDropdown");
    input.setAttribute("aria-expanded", "false");
    dropdown.setAttribute("role", "listbox");
    dropdown.setAttribute("aria-label", "Location suggestions");

    // ── Fetch suggestions from semantic API ──
    async function fetchSuggestions(query) {
        try {
            const res = await fetch(
                `/api/locations/autocomplete/?q=${encodeURIComponent(query)}&limit=6`
            );

            // Handle non-200 responses
            if (!res.ok) {
                console.error(`API error: ${res.status}`);
                return [];
            }

            const data = await res.json();
            return data.results || [];
        } catch (error) {
            console.error("Fetch error:", error);
            return [];
        }
    }

    // ── Render dropdown items ──
    function renderDropdown(results) {
        // Clear dropdown safely
        while (dropdown.firstChild) {
            dropdown.removeChild(dropdown.firstChild);
        }
        currentFocus = -1;

        if (results.length === 0) {
            dropdown.style.display = "none";
            return;
        }

        results.forEach((loc, index) => {
            const item = document.createElement("a");
            item.href = `/properties/?search=${encodeURIComponent(loc.city)}`;
            item.className =
                "list-group-item list-group-item-action " +
                "d-flex align-items-center gap-2 py-2";
            item.dataset.index = index;

            // Set ARIA attributes for accessibility
            item.setAttribute("role", "option");
            item.setAttribute("aria-label", `${loc.city}, ${loc.state}, ${loc.country}`);

            // Create icon safely
            const icon = document.createElement("i");
            icon.className = "bi bi-geo-alt-fill text-primary flex-shrink-0";

            // Create location info container
            const infoDiv = document.createElement("div");

            // Create city name (safe from XSS)
            const cityDiv = document.createElement("div");
            cityDiv.className = "fw-600 small";
            cityDiv.textContent = loc.city;

            // Create state/country info (safe from XSS)
            const stateDiv = document.createElement("div");
            stateDiv.className = "text-muted";
            stateDiv.style.fontSize = "0.75rem";
            stateDiv.textContent = `${loc.state}, ${loc.country}`;

            // Assemble the item
            infoDiv.appendChild(cityDiv);
            infoDiv.appendChild(stateDiv);
            item.appendChild(icon);
            item.appendChild(infoDiv);

            // Fill input on click
            item.addEventListener("mousedown", function (e) {
                e.preventDefault();
                input.value = loc.city;
                dropdown.style.display = "none";
                dropdown.setAttribute("aria-expanded", "false");
                this.closest("form").submit();
            });

            dropdown.appendChild(item);
        });

        dropdown.style.display = "block";
        dropdown.setAttribute("aria-expanded", "true");
    }

    // ── Keyboard navigation ──
    input.addEventListener("keydown", function (e) {
        const items = dropdown.querySelectorAll(".list-group-item");

        if (e.key === "ArrowDown") {
            currentFocus = Math.min(currentFocus + 1, items.length - 1);
        } else if (e.key === "ArrowUp") {
            currentFocus = Math.max(currentFocus - 1, -1);
        } else if (e.key === "Escape") {
            dropdown.style.display = "none";
            input.setAttribute("aria-expanded", "false");
            return;
        } else if (e.key === "Enter" && currentFocus >= 0) {
            e.preventDefault();
            items[currentFocus].dispatchEvent(new MouseEvent("mousedown"));
            return;
        }

        // Highlight focused item
        items.forEach((item, i) => {
            item.classList.toggle("active", i === currentFocus);
        });
    });

    // ── Main input handler with debounce ──
    input.addEventListener("input", function () {
        clearTimeout(debounceTimer);
        const query = this.value.trim();

        if (query.length < 2) {
            dropdown.style.display = "none";
            dropdown.setAttribute("aria-expanded", "false");
            return;
        }

        // Show loading state (safe DOM manipulation)
        while (dropdown.firstChild) {
            dropdown.removeChild(dropdown.firstChild);
        }

        const loadingItem = document.createElement("div");
        loadingItem.className = "list-group-item text-muted small py-2";
        loadingItem.textContent = "Searching...";

        const loadingIcon = document.createElement("i");
        loadingIcon.className = "bi bi-stars me-2 text-primary";
        loadingItem.insertBefore(loadingIcon, loadingItem.firstChild);

        dropdown.appendChild(loadingItem);
        dropdown.style.display = "block";
        dropdown.setAttribute("aria-expanded", "true");

        // Wait 350ms after user stops typing
        debounceTimer = setTimeout(async () => {
            const results = await fetchSuggestions(query);
            renderDropdown(results);
        }, 350);
    });

    // ── Hide dropdown when clicking outside ──
    document.addEventListener("click", function (e) {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = "none";
            input.setAttribute("aria-expanded", "false");
        }
    });

    // ── Show dropdown again on focus if has value ──
    input.addEventListener("focus", function () {
        if (this.value.trim().length >= 2) {
            this.dispatchEvent(new Event("input"));
        }
    });
})();
