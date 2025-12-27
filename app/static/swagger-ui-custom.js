// 🎨 Ultra-Modern Swagger UI Enhancements - Premium Interactive Features

(function() {
    'use strict';

    // Wait for Swagger UI to load
    window.addEventListener('load', function() {
        setTimeout(enhanceSwaggerUI, 500);
    });

    // Also enhance on DOM changes (for dynamic content)
    const observer = new MutationObserver(function(mutations) {
        enhanceSwaggerUI();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    function enhanceSwaggerUI() {
        addCopyButtons();
        enhanceExamples();
        addQuickTestButtons();
        addCollapsibleSections();
        addSearchFunctionality();
        addKeyboardShortcuts();
        enhanceResponseDisplay();
        addParticleEffects();
        addSmoothScroll();
        addTooltips();
        enhanceCodeBlocks();
    }

    // 📋 Enhanced Copy Buttons with Animation
    function addCopyButtons() {
        const codeBlocks = document.querySelectorAll('.highlight-code, .response .highlight-code');
        codeBlocks.forEach(block => {
            if (block.querySelector('.copy-btn-enhanced')) return;
            
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn-enhanced';
            copyBtn.innerHTML = '<span class="copy-icon">📋</span><span class="copy-text">Copy</span>';
            copyBtn.style.cssText = `
                position: absolute;
                top: 12px;
                right: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                cursor: pointer;
                font-size: 0.85em;
                font-weight: 600;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
                display: flex;
                align-items: center;
                gap: 6px;
                z-index: 10;
                font-family: 'Inter', sans-serif;
            `;
            
            copyBtn.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px) scale(1.05)';
                this.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.6)';
            });
            
            copyBtn.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
            });
            
            copyBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                const text = block.querySelector('pre')?.textContent || block.textContent;
                navigator.clipboard.writeText(text).then(() => {
                    const originalHTML = this.innerHTML;
                    this.innerHTML = '<span class="copy-icon">✓</span><span class="copy-text">Copied!</span>';
                    this.style.background = 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)';
                    
                    setTimeout(() => {
                        this.innerHTML = originalHTML;
                        this.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy:', err);
                });
            });
            
            block.style.position = 'relative';
            block.appendChild(copyBtn);
        });
    }

    // 🎯 Enhanced Examples with Visual Feedback
    function enhanceExamples() {
        const exampleSelects = document.querySelectorAll('.examples-select');
        exampleSelects.forEach(select => {
            select.addEventListener('change', function() {
                this.style.borderColor = '#667eea';
                this.style.boxShadow = '0 0 0 4px rgba(102, 126, 234, 0.2)';
                setTimeout(() => {
                    this.style.borderColor = '';
                    this.style.boxShadow = '';
                }, 500);
            });
        });
    }

    // ⚡ Quick Test Buttons with Animation
    function addQuickTestButtons() {
        const opblocks = document.querySelectorAll('.opblock');
        opblocks.forEach(block => {
            if (block.querySelector('.quick-test-enhanced')) return;
            
            const summary = block.querySelector('.opblock-summary');
            if (!summary) return;
            
            const quickTestBtn = document.createElement('button');
            quickTestBtn.className = 'quick-test-enhanced';
            quickTestBtn.innerHTML = '⚡ Quick Test';
            quickTestBtn.style.cssText = `
                margin-left: auto;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: 700;
                cursor: pointer;
                font-size: 0.85em;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-family: 'Inter', sans-serif;
            `;
            
            quickTestBtn.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px) scale(1.05)';
                this.style.boxShadow = '0 6px 25px rgba(102, 126, 234, 0.6)';
            });
            
            quickTestBtn.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
            });
            
            quickTestBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const tryOutBtn = block.querySelector('.try-out__btn');
                if (tryOutBtn) {
                    tryOutBtn.click();
                    setTimeout(() => {
                        const executeBtn = block.querySelector('.btn.execute');
                        if (executeBtn) {
                            executeBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            executeBtn.style.animation = 'pulse 0.5s ease';
                            setTimeout(() => {
                                executeBtn.style.animation = '';
                            }, 500);
                        }
                    }, 300);
                }
            });
            
            summary.appendChild(quickTestBtn);
        });
    }

    // 📖 Expand/Collapse All with Animation
    function addCollapsibleSections() {
        const topbar = document.querySelector('.topbar');
        if (topbar && !topbar.querySelector('.expand-all-enhanced')) {
            const expandAllBtn = document.createElement('button');
            expandAllBtn.className = 'expand-all-enhanced';
            expandAllBtn.textContent = '📖 Expand All';
            expandAllBtn.style.cssText = `
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                padding: 10px 20px;
                margin-left: 12px;
                cursor: pointer;
                font-weight: 700;
                font-size: 0.85em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                transition: all 0.3s ease;
                font-family: 'Inter', sans-serif;
            `;
            
            let expanded = false;
            expandAllBtn.addEventListener('click', () => {
                const opblocks = document.querySelectorAll('.opblock');
                opblocks.forEach(block => {
                    const isOpen = block.classList.contains('opblock-is-open');
                    const summary = block.querySelector('.opblock-summary');
                    if (!expanded && !isOpen && summary) {
                        summary.click();
                    } else if (expanded && isOpen && summary) {
                        summary.click();
                    }
                });
                expanded = !expanded;
                expandAllBtn.textContent = expanded ? '📕 Collapse All' : '📖 Expand All';
                expandAllBtn.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    expandAllBtn.style.transform = 'scale(1)';
                }, 150);
            });
            
            expandAllBtn.addEventListener('mouseenter', function() {
                this.style.background = 'rgba(255, 255, 255, 0.25)';
                this.style.transform = 'translateY(-2px)';
            });
            
            expandAllBtn.addEventListener('mouseleave', function() {
                this.style.background = 'rgba(255, 255, 255, 0.15)';
                this.style.transform = 'translateY(0)';
            });
            
            topbar.appendChild(expandAllBtn);
        }
    }

    // 🔍 Enhanced Search with Visual Feedback
    function addSearchFunctionality() {
        const topbar = document.querySelector('.topbar');
        if (topbar && !topbar.querySelector('.search-enhanced')) {
            const searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.className = 'search-enhanced';
            searchInput.placeholder = '🔍 Search endpoints...';
            searchInput.style.cssText = `
                margin-left: 12px;
                padding: 10px 20px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                color: white;
                font-size: 0.9em;
                width: 280px;
                font-weight: 500;
                font-family: 'Inter', sans-serif;
                transition: all 0.3s ease;
            `;
            
            searchInput.addEventListener('focus', function() {
                this.style.borderColor = 'rgba(255, 255, 255, 0.5)';
                this.style.boxShadow = '0 0 0 4px rgba(255, 255, 255, 0.1)';
                this.style.width = '320px';
            });
            
            searchInput.addEventListener('blur', function() {
                this.style.borderColor = 'rgba(255, 255, 255, 0.3)';
                this.style.boxShadow = 'none';
                this.style.width = '280px';
            });
            
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                const opblocks = document.querySelectorAll('.opblock-tag');
                let found = false;
                
                opblocks.forEach(tag => {
                    const text = tag.textContent.toLowerCase();
                    if (text.includes(query)) {
                        tag.style.display = '';
                        tag.style.animation = 'slideDown 0.3s ease';
                        found = true;
                        if (query) {
                            tag.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                        }
                    } else {
                        tag.style.display = 'none';
                    }
                });
                
                // Visual feedback
                if (query && found) {
                    searchInput.style.borderColor = '#48bb78';
                } else if (query && !found) {
                    searchInput.style.borderColor = '#f56565';
                }
            });
            
            topbar.appendChild(searchInput);
        }
    }

    // ⌨️ Keyboard Shortcuts
    function addKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('.search-enhanced');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }
            
            if (e.key === 'Escape') {
                const searchInput = document.querySelector('.search-enhanced');
                if (searchInput && document.activeElement === searchInput) {
                    searchInput.value = '';
                    searchInput.dispatchEvent(new Event('input'));
                    searchInput.blur();
                }
            }
        });
    }

    // 🎨 Enhanced Response Display
    function enhanceResponseDisplay() {
        const observer = new MutationObserver(() => {
            const responseCodes = document.querySelectorAll('.response-col_status');
            responseCodes.forEach(code => {
                code.addEventListener('mouseenter', function() {
                    this.style.transform = 'scale(1.1)';
                    this.style.transition = 'transform 0.2s ease';
                });
                
                code.addEventListener('mouseleave', function() {
                    this.style.transform = 'scale(1)';
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // ✨ Particle Effects on Hover
    function addParticleEffects() {
        const opblocks = document.querySelectorAll('.opblock-summary');
        opblocks.forEach(block => {
            block.addEventListener('mouseenter', function() {
                createParticles(this);
            });
        });
    }

    function createParticles(element) {
        const rect = element.getBoundingClientRect();
        for (let i = 0; i < 5; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: fixed;
                width: 4px;
                height: 4px;
                background: #667eea;
                border-radius: 50%;
                pointer-events: none;
                z-index: 9999;
                left: ${rect.left + rect.width / 2}px;
                top: ${rect.top + rect.height / 2}px;
                animation: particleFloat 1s ease-out forwards;
            `;
            
            const angle = (Math.PI * 2 * i) / 5;
            const distance = 30 + Math.random() * 20;
            const x = Math.cos(angle) * distance;
            const y = Math.sin(angle) * distance;
            
            particle.style.setProperty('--x', x + 'px');
            particle.style.setProperty('--y', y + 'px');
            
            document.body.appendChild(particle);
            
            setTimeout(() => {
                particle.remove();
            }, 1000);
        }
    }

    // Add particle animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes particleFloat {
            to {
                transform: translate(var(--x), var(--y));
                opacity: 0;
            }
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
    `;
    document.head.appendChild(style);

    // 📜 Smooth Scroll
    function addSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    // 💡 Tooltips
    function addTooltips() {
        const tooltipElements = document.querySelectorAll('[title]');
        tooltipElements.forEach(el => {
            el.addEventListener('mouseenter', function(e) {
                const title = this.getAttribute('title');
                if (!title) return;
                
                const tooltip = document.createElement('div');
                tooltip.className = 'custom-tooltip';
                tooltip.textContent = title;
                tooltip.style.cssText = `
                    position: fixed;
                    background: rgba(26, 32, 44, 0.95);
                    backdrop-filter: blur(10px);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 0.85em;
                    pointer-events: none;
                    z-index: 10000;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(102, 126, 234, 0.3);
                `;
                
                document.body.appendChild(tooltip);
                
                const rect = this.getBoundingClientRect();
                tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
                tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
                
                this.removeAttribute('title');
                this._tooltip = tooltip;
            });
            
            el.addEventListener('mouseleave', function() {
                if (this._tooltip) {
                    this._tooltip.remove();
                    this.setAttribute('title', this._tooltip.textContent);
                    delete this._tooltip;
                }
            });
        });
    }

    // 💻 Enhanced Code Blocks
    function enhanceCodeBlocks() {
        const codeBlocks = document.querySelectorAll('pre code');
        codeBlocks.forEach(block => {
            block.style.cssText += `
                font-family: 'JetBrains Mono', 'Monaco', 'Menlo', monospace !important;
                font-weight: 500 !important;
            `;
        });
    }

    // 🎯 Loading Indicator Enhancement
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const loadingIndicator = document.createElement('div');
        loadingIndicator.id = 'swagger-loading-enhanced';
        loadingIndicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
            z-index: 10000;
            font-weight: 700;
            font-size: 0.9em;
            display: flex;
            align-items: center;
            gap: 10px;
            font-family: 'Inter', sans-serif;
        `;
        loadingIndicator.innerHTML = `
            <div style="width: 20px; height: 20px; border: 3px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite;"></div>
            <span>Loading...</span>
        `;
        document.body.appendChild(loadingIndicator);
        
        return originalFetch.apply(this, args).finally(() => {
            setTimeout(() => {
                loadingIndicator.style.opacity = '0';
                loadingIndicator.style.transform = 'translateY(-20px)';
                setTimeout(() => {
                    loadingIndicator.remove();
                }, 300);
            }, 500);
        });
    };

    // Add spin animation
    const spinStyle = document.createElement('style');
    spinStyle.textContent = `
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(spinStyle);
})();
