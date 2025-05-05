class BasePage {
    private static instance: BasePage;

    private constructor() {
        if (BasePage.instance) {
            throw new Error('Only one instance of BasePage can be created');
        }
        console.log('Initializing BasePage...');
        this.currentPage = 1;
        this.pageSize = DEFAULT_PAGE_SIZE;  
        this.initializeElements();
        this.initializeEventListeners();
        this.loadInitialView();
        BasePage.instance = this;
    }

    static getInstance(): BasePage {
        if (!BasePage.instance) {
            BasePage.instance = new BasePage();
        }
        return BasePage.instance;
    }

    initializeElements() {
        // Views
        this.mCardDetailView = document.getElementById('mCardDetailView');
        this.newCardView = document.getElementById('newCardView');
        this.cardsContainer = document.getElementById('cardsContainer');
        this.cardDetailContainer = document.getElementById('cardDetailContainer');
        
        // Buttons and inputs
        this.newCardButton = document.getElementById('newCardButton');
        this.submitNewCardButton = document.getElementById('submitNewCard');
        this.cardContent = document.getElementById('cardContent');
        this.fileInput = document.getElementById('fileInput');
        this.selectFileButton = document.getElementById('selectFileButton');
        this.searchInput = document.getElementById('searchInput');
        
        // Tab elements
        this.textTabButton = document.querySelector('.tab-button[data-tab="textTab"]');
        this.binaryTabButton = document.querySelector('.tab-button[data-tab="binaryTab"]');
        this.textTab = document.getElementById('textTab');
        this.binaryTab = document.getElementById('binaryTab');
        
        // Pagination elements
        this.prevPageButton = document.getElementById('prevPage');
        this.nextPageButton = document.getElementById('nextPage');
        this.pageInfo = document.getElementById('pageInfo');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        
        console.log('Elements initialized:', {
            mCardDetailView: !!this.mCardDetailView,
            newCardView: !!this.newCardView,
            cardsContainer: !!this.cardsContainer,
            newCardButton: !!this.newCardButton,
            submitNewCardButton: !!this.submitNewCardButton,
            searchInput: !!this.searchInput
        });

        console.log('Pagination elements:', {
            prevPageButton: this.prevPageButton,
            nextPageButton: this.nextPageButton,
            pageInfo: this.pageInfo,
            loadingIndicator: this.loadingIndicator
        });
    }

    initializeEventListeners() {
        // New Card button
        if (this.newCardButton) {
            this.newCardButton.addEventListener('click', (e) => {
                console.log('New Card button clicked');
                e.preventDefault();
                this.showNewCardView();
            });
        }

        // Submit button
        document.addEventListener('click', async (e) => {
            if (e.target && e.target.id === 'submitNewCard') {
                console.log('Submit button clicked');
                e.preventDefault();
                await this.handleSubmit();
            }
        });

        // File selection
        if (this.selectFileButton) {
            this.selectFileButton.addEventListener('click', () => {
                if (this.fileInput) {
                    this.fileInput.click();
                }
            });
        }

        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => this.handleTabClick(button));
        });

        // Card selection in collection view
        if (this.cardsContainer) {
            this.cardsContainer.addEventListener('click', async (e) => {
                const cardEntry = e.target.closest('.card-entry');
                if (cardEntry) {
                    const hash = cardEntry.dataset.hash;
                    if (hash) {
                        console.log('Card clicked, hash:', hash);
                        await this.loadCardDetails(hash);
                    }
                }
            });
        }

        // Search input
        if (this.searchInput) {
            this.searchInput.addEventListener('input', this.debounce(() => {
                console.log('Search input changed:', this.searchInput.value);
                this.currentPage = 1;  
                this.updateResults();
            }, 300));
        }

        // Pagination
        if (this.prevPageButton) {
            console.log('Adding click handler to prevPageButton');
            this.prevPageButton.addEventListener('click', async () => {
                console.log('Previous button clicked, disabled:', this.prevPageButton.disabled);
                if (!this.prevPageButton.disabled) {
                    this.currentPage--;
                    await this.updateResults();
                }
            });
        }

        if (this.nextPageButton) {
            console.log('Adding click handler to nextPageButton');
            this.nextPageButton.addEventListener('click', async () => {
                console.log('Next button clicked, disabled:', this.nextPageButton.disabled);
                if (!this.nextPageButton.disabled) {
                    this.currentPage++;
                    await this.updateResults();
                }
            });
        }

        // Initialize drag and drop
        this.initializeDragAndDrop();

        console.log('Event listeners initialized');
    }

    debounce(func, wait) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    showLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.remove('hidden');
        }
    }

    hideLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.add('hidden');
        }
    }

    async loadInitialView() {
        console.log('Loading initial view...');
        await this.updateResults();
        this.showDetailView();
    }

    showNewCardView() {
        console.log('Showing new card view');
        if (this.mCardDetailView) {
            this.mCardDetailView.classList.add('hidden');
        }
        if (this.newCardView) {
            this.newCardView.classList.remove('hidden');
            // Clear previous content
            if (this.cardContent) {
                this.cardContent.value = '';
            }
            if (this.fileInput) {
                this.fileInput.value = '';
            }
        }
    }

    showDetailView() {
        console.log('Showing detail view');
        if (this.newCardView) {
            this.newCardView.classList.add('hidden');
        }
        if (this.mCardDetailView) {
            this.mCardDetailView.classList.remove('hidden');
        }
    }

    handleTabClick(button) {
        const tabId = button.getAttribute('data-tab');
        const allTabs = document.querySelectorAll('.tab-content');
        const allTabButtons = document.querySelectorAll('.tab-button');
        
        allTabs.forEach(tab => tab.classList.add('hidden'));
        allTabButtons.forEach(btn => btn.classList.remove('active'));
        
        const selectedTab = document.getElementById(tabId);
        if (selectedTab) {
            selectedTab.classList.remove('hidden');
            button.classList.add('active');
        }
    }

    async handleSubmit() {
        console.log('Processing submit...');
        
        const cardContent = document.getElementById('cardContent');
        const fileInput = document.getElementById('fileInput');
        
        const textContent = cardContent ? cardContent.value.trim() : '';
        const file = fileInput ? fileInput.files[0] : null;
        
        console.log('Content found:', { 
            hasText: !!textContent, 
            textContent: textContent,
            hasFile: !!file 
        });

        if (!textContent && !file) {
            console.error('Please provide either text content or a file');
            return;
        }

        try {
            const payload = {
                type: 'text',
                content: textContent
            };

            console.log('Sending POST request with data:', payload);

            const response = await fetch('/cards', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            console.log('Response status:', response.status);
            
            const result = await response.json();
            console.log('Response data:', result);

            if (result.status === 'error') {
                throw new Error(result.message || 'Unknown error occurred');
            }

            console.log('Card created successfully:', result);

            // Clear form
            if (cardContent) cardContent.value = '';
            if (fileInput) fileInput.value = '';

            // Switch views
            this.showDetailView();

            // Refresh the collection
            await this.updateResults();
            
            console.log('View transition completed');
        } catch (error) {
            console.error('Error creating new card:', error);
        }
    }

    async loadCardDetails(hash) {
        try {
            console.log('Loading card details for hash:', hash);
            const response = await fetch(`/card_detail/${hash}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const html = await response.text();
            
            if (this.mCardDetailView) {
                this.mCardDetailView.innerHTML = html;
                this.showDetailView();
                console.log('Card details loaded successfully');
            }
        } catch (error) {
            console.error('Error loading card details:', error);
        }
    }

    async updateResults() {
        this.showLoading();
        try {
            console.log('Updating results...');
            const query = this.searchInput ? this.searchInput.value.trim() : '';
            const data = await this.fetchCards(query, this.currentPage);
            
            console.log('Fetch result:', data);
            
            if (data.status === 'success') {
                this.renderCards(data.cards);
                this.updatePaginationControls(data.pagination);
            } else {
                throw new Error(data.message || 'Failed to fetch cards');
            }
        } catch (error) {
            console.error('Error updating results:', error);
        } finally {
            this.hideLoading();
        }
    }

    async fetchCards(query = '', page = 1) {
        const params = new URLSearchParams({
            query: query,
            page: page.toString(),
            per_page: this.pageSize.toString()
        });

        console.log('Fetching cards with params:', params.toString());

        const response = await fetch(`/cards?${params}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const result = await response.json();
        console.log('API response:', result);
        return result;
    }

    renderCards(cards) {
        if (!this.cardsContainer || !Array.isArray(cards)) {
            console.error('Invalid cards container or cards data');
            return;
        }

        console.log('Rendering cards:', cards.length);
        this.cardsContainer.innerHTML = '';
        
        cards.forEach(card => {
            try {
                const cardHtml = `
                    <div class="card-entry p-3 border-b hover:bg-gray-50 transition-colors flex items-center justify-between cursor-pointer" data-hash="${card.hash}">
                        <div class="flex items-center space-x-4">
                            <div class="font-mono text-sm text-gray-500">${card.hash.substring(0, 6)}</div>
                            <div class="text-sm text-gray-600">${new Date(card.g_time).toISOString().split('T')[0]}</div>
                            <div class="text-sm text-gray-600">${card.type.split('/')[1].toUpperCase()}</div>
                        </div>
                    </div>
                `;
                this.cardsContainer.insertAdjacentHTML('beforeend', cardHtml);
            } catch (error) {
                console.error('Error rendering card:', error, card);
            }
        });
    }

    updatePaginationControls(pagination) {
        if (!pagination) {
            console.error('Invalid pagination data');
            return;
        }

        console.log('Updating pagination controls:', pagination);
        
        const { page, total_pages, has_next, has_previous, total } = pagination;
        
        if (this.prevPageButton) {
            this.prevPageButton.disabled = !has_previous;
            if (has_previous) {
                this.prevPageButton.classList.remove('opacity-50', 'cursor-not-allowed');
            } else {
                this.prevPageButton.classList.add('opacity-50', 'cursor-not-allowed');
            }
        }

        if (this.nextPageButton) {
            this.nextPageButton.disabled = !has_next;
            if (has_next) {
                this.nextPageButton.classList.remove('opacity-50', 'cursor-not-allowed');
            } else {
                this.nextPageButton.classList.add('opacity-50', 'cursor-not-allowed');
            }
        }

        if (this.pageInfo) {
            this.pageInfo.textContent = `Page ${page} of ${total_pages} (${total} total items)`;
        }

        // Update current page
        this.currentPage = page;
    }

    initializeDragAndDrop() {
        const dragDropArea = document.getElementById('dragDropArea');
        if (dragDropArea) {
            dragDropArea.addEventListener('dragover', (event) => {
                event.preventDefault();
                dragDropArea.classList.add('bg-gray-200');
            });

            dragDropArea.addEventListener('dragleave', () => {
                dragDropArea.classList.remove('bg-gray-200');
            });

            dragDropArea.addEventListener('drop', (event) => {
                event.preventDefault();
                dragDropArea.classList.remove('bg-gray-200');
                if (this.fileInput && event.dataTransfer.files.length > 0) {
                    this.fileInput.files = event.dataTransfer.files;
                    console.log('File dropped:', event.dataTransfer.files[0]);
                }
            });
        }
    }
}

// Initialize the base page
const basePage = BasePage.getInstance();
export default basePage;
